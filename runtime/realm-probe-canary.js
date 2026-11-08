"use strict";

// Independent diagnostic wrapper. It does not replay FO bodies and does not
// alter the production mirror runner. The only source edit is the one
// Timeout.It call whose callee is the throwing x[...][...] expression.
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const vm = require("vm");

const BASE = path.join(__dirname, "mirror-canary.js");
const RESULT_PATH = path.join(__dirname, "realm-probe-result.json");

function rewriteThrowingXCall(text) {
  function matchingBracket(source, openAt, openCh, closeCh) {
    let depth = 0;
    let quote = null;
    const templates = [];
    for (let i = openAt; i < source.length; i++) {
      const ch = source[i];
      if (quote === "`") {
        if (ch === "\\") { i += 1; continue; }
        if (ch === "$" && source[i + 1] === "{") { templates.push(true); quote = null; i += 1; continue; }
        if (ch === "`") quote = null;
        continue;
      }
      if (quote) {
        if (ch === "\\") { i += 1; continue; }
        if (ch === quote) quote = null;
        continue;
      }
      if (ch === '"' || ch === "'" || ch === "`") { quote = ch; continue; }
      if (ch === "}" && templates.length) { templates.pop(); quote = "`"; continue; }
      if (ch === openCh) depth += 1;
      else if (ch === closeCh) {
        depth -= 1;
        if (depth === 0) return i + 1;
      }
    }
    return -1;
  }

  function functionRange(source, name) {
    const marker = "function " + name + "(";
    const start = source.indexOf(marker);
    if (start < 0) return null;
    const brace = source.indexOf("{", start);
    if (brace < 0) return null;
    const end = matchingBracket(source, brace, "{", "}");
    if (end < 0) return null;
    return { start: start, bodyStart: brace + 1, end: end };
  }

  function skipSpace(source, index, limit) {
    while (index < limit && /\s/.test(source[index])) index += 1;
    return index;
  }

  function sameCallCallee(indexExpr) {
    const match = /^\s*([A-Za-z_$][\w$]*)\(/.exec(indexExpr);
    return match ? match[1] : "";
  }

  const range = functionRange(text, "It");
  if (!range) return { text: text, changed: false, expression: "", candidates: 0 };
  const calls = [];
  let quote = null;
  const templates = [];
  for (let i = range.bodyStart; i < range.end; i++) {
    const ch = text[i];
    if (quote === "`") {
      if (ch === "\\") { i += 1; continue; }
      if (ch === "$" && text[i + 1] === "{") { templates.push(true); quote = null; i += 1; continue; }
      if (ch === "`") quote = null;
      continue;
    }
    if (quote) {
      if (ch === "\\") { i += 1; continue; }
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") { quote = ch; continue; }
    if (ch === "}" && templates.length) { templates.pop(); quote = "`"; continue; }
    if (ch !== "x" || text[i + 1] !== "[") continue;
    if (i > range.bodyStart && /[A-Za-z0-9_$]/.test(text[i - 1])) continue;
    const firstEnd = matchingBracket(text, i + 1, "[", "]");
    if (firstEnd < 0) continue;
    const secondOpen = skipSpace(text, firstEnd, range.end);
    if (text[secondOpen] !== "[") continue;
    const secondEnd = matchingBracket(text, secondOpen, "[", "]");
    if (secondEnd < 0) continue;
    const callOpen = skipSpace(text, secondEnd, range.end);
    if (text[callOpen] !== "(") continue;
    const callEnd = matchingBracket(text, callOpen, "(", ")");
    if (callEnd < 0) continue;
    const index1 = text.slice(i + 2, firstEnd - 1);
    const index2 = text.slice(secondOpen + 1, secondEnd - 1);
    const callee1 = sameCallCallee(index1);
    const callee2 = sameCallCallee(index2);
    if (!callee1 || callee1 !== callee2) continue;
    calls.push({
      start: i,
      end: callEnd,
      index1: index1,
      index2: index2,
      args: text.slice(callOpen + 1, callEnd - 1),
    });
    i = callEnd - 1;
  }
  if (calls.length !== 1) {
    return { text: text, changed: false, expression: "", candidates: calls.length };
  }
  const call = calls[0];
  const expression = text.slice(call.start, call.end);
  const replacement = "(function(__rpRecv,__rpKey){try{var __rpDesc;"
    + "if(__rpRecv==null)__rpDesc=String(__rpRecv);"
    + "else if(typeof __rpRecv===\"function\")__rpDesc=\"function:\"+(__rpRecv.name||\"anonymous\");"
    + "else{var __rpCtor=\"\";try{__rpCtor=__rpRecv.constructor&&__rpRecv.constructor.name||\"\";}catch(__rpC){__rpCtor=\"\";}__rpDesc=__rpCtor||typeof __rpRecv;}"
    + "var __rpRec={propertyKey:String(__rpKey),receiver:String(__rpDesc),expression:" + JSON.stringify(expression) + "};"
    + "(globalThis.__realmProbe=globalThis.__realmProbe||{evals:[],errors:[]}).xCall=__rpRec;"
    + "console.log(JSON.stringify({xCallRecord:__rpRec}));"
    + "}catch(__rpE){}"
    + "return __rpRecv[__rpKey](" + call.args + ");})(x[" + call.index1 + "]," + call.index2 + ")";
  return {
    text: text.slice(0, call.start) + replacement + text.slice(call.end),
    changed: true,
    expression: expression,
    candidates: 1,
  };
}

function collectFacts(parsed) {
  let frame = null;
  let xCall = null;
  for (const record of parsed) {
    if (!record || typeof record !== "object") continue;
    if (record.frameSha256) frame = record;
    if (record.xCallRecord && record.xCallRecord.propertyKey) xCall = record.xCallRecord;
  }
  const foRequests = frame && typeof frame.xhrCount === "number" ? frame.xhrCount : 0;
  return {
    xCall: xCall,
    foRequests: foRequests,
    framePqType: frame ? frame.framePqType : "",
    serverAccepted: parsed.some(function (record) { return !!(record && record.serverAccepted === true); }),
    replayedFoBody: parsed.some(function (record) { return !!(record && record.replayedFoBody === true); }),
  };
}

function main() {
  const source = fs.readFileSync(BASE, "utf8");
  const marker = /const originalEval = global\.eval; global\.eval = function\(src\)\{[\s\S]*?return out; \}; const originalDefineProperty/;
  if (!marker.test(source)) throw new Error("mirror eval marker not found");

  const injected = "const originalEval = global.eval; global.eval = function(src){\n"
    + "  var text = String(src);\n"
    + "  var isLarge = text.length >= 200000;\n"
    + "  if (isLarge) {\n"
    + "    var originalLength = text.length;\n"
    + "    var digest = require(\"crypto\").createHash(\"sha256\").update(text).digest(\"hex\");\n"
    + "    if (!global.__rpRewriteThrowingXCall) global.__rpRewriteThrowingXCall = " + rewriteThrowingXCall.toString() + ";\n"
    + "    var rewritten = global.__rpRewriteThrowingXCall(text);\n"
    + "    text = rewritten.text;\n"
    + "    global.__realmProbe = global.__realmProbe || {evals:[],errors:[]};\n"
    + "    global.__realmProbe.evals.push({length:originalLength,sha256:digest,rewritten:!!rewritten.changed,expression:rewritten.expression||\"\",candidates:rewritten.candidates||0});\n"
    + "    console.log(JSON.stringify({realmEval:true,length:originalLength,sha256:digest,rewritten:!!rewritten.changed,expression:rewritten.expression||\"\",candidates:rewritten.candidates||0}));\n"
    + "  }\n"
    + "  try { var out = originalEval(text); if (isLarge) global.__realmProbe.evals[global.__realmProbe.evals.length-1].returnType=typeof out; return out; }\n"
    + "  catch (e) { if (isLarge) global.__realmProbe.errors.push({message:String(e&&e.message||e),stack:String(e&&e.stack||\"\").split(\"\\n\").slice(0,6)}); throw e; }\n"
    + "};";

  const patched = source.replace(marker, injected + " const originalDefineProperty");
  try { new vm.Script(patched); } catch (error) {
    process.stderr.write(String(error && error.stack || error));
    process.exit(2);
  }

  const child = require("child_process").spawn(process.execPath, ["-e", patched], {
    cwd: path.dirname(BASE),
    env: Object.assign({}, process.env, { FRAME_DEBUG: "0" }),
    stdio: ["ignore", "pipe", "pipe"],
  });
  let stdout = "";
  let stderr = "";
  child.stdout.on("data", function (chunk) { stdout += chunk.toString(); });
  child.stderr.on("data", function (chunk) { stderr += chunk.toString(); });
  child.on("close", function (code) {
    const lines = stdout.trim().split(/\r?\n/).filter(Boolean);
    const parsed = [];
    for (const line of lines) {
      try { parsed.push(JSON.parse(line)); } catch (_) {}
    }
    const facts = collectFacts(parsed);
    const probeLines = lines.filter(function (line) { return line.indexOf("realmEval") !== -1; });
    const result = {
      probeSources: true,
      canary: "realm-probe-canary",
      base: BASE,
      exitCode: code,
      stderr: stderr.slice(0, 1200),
      runnerRecords: parsed,
      probeLines: probeLines,
      xCall: facts.xCall,
      foRequests: facts.foRequests,
      framePqType: facts.framePqType,
      serverAccepted: facts.serverAccepted,
      sourceSha256: crypto.createHash("sha256").update(patched).digest("hex"),
      sourceBytes: Buffer.byteLength(patched),
      note: "realm diagnostic records the throwing x[...][...] call only",
      restrictions: {
        replayedFoBody: facts.replayedFoBody,
        wroteServerAccepted: facts.serverAccepted,
      },
    };
    const body = JSON.stringify(result);
    fs.writeFileSync(RESULT_PATH, body);
    process.stdout.write(body);
    process.exit(code || 0);
  });
}

module.exports = { rewriteThrowingXCall: rewriteThrowingXCall, collectFacts: collectFacts };

if (require.main === module) main();
