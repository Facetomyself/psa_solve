"use strict";

// Reads two artifacts written by runtime/realm-probe-canary.js.
// It does not re-implement the probe. Pass the two result JSON paths.
const fs = require("fs");

const IFRAME_LEN = 238636;
const IFRAME_SHA = "05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262";

function fail(message) {
  process.stderr.write("FAIL " + message + "\n");
  process.exitCode = 1;
}

function load(filePath) {
  const raw = fs.readFileSync(filePath, "utf8").replace(/^\uFEFF/, "");
  return JSON.parse(raw);
}

function frameRecord(result) {
  const records = result.runnerRecords || [];
  for (let i = 0; i < records.length; i += 1) {
    if (records[i] && records[i].frameSha256) return records[i];
  }
  return null;
}

function probeIframe(result) {
  const lines = result.probeLines || [];
  for (let i = 0; i < lines.length; i += 1) {
    const item = typeof lines[i] === "string" ? JSON.parse(lines[i]) : lines[i];
    if (item && item.length === IFRAME_LEN) return item;
  }
  return null;
}

function uncaughtRecord(result) {
  const records = result.runnerRecords || [];
  for (let i = 0; i < records.length; i += 1) {
    if (records[i] && records[i].uncaught) return records[i];
  }
  return null;
}

function checkOne(label, result) {
  if (!result || result.canary !== "realm-probe-canary") fail(label + " canary");
  if (!result || result.exitCode !== 0) fail(label + " exitCode " + (result && result.exitCode));
  const frame = frameRecord(result);
  if (!frame || frame.frameEval !== "ok") fail(label + " frameEval");
  if (!frame || frame.frameScriptLength !== IFRAME_LEN) fail(label + " iframe length");
  if (!frame || frame.frameSha256 !== IFRAME_SHA) fail(label + " iframe sha");
  if (!frame || frame.chlOptKeys !== 37) fail(label + " chlOptKeys");
  const probe = probeIframe(result);
  if (!probe || probe.length !== IFRAME_LEN || probe.sha256 !== IFRAME_SHA) fail(label + " probe window");
  if (!probe || probe.rewritten !== true) fail(label + " iframe expression was not rewritten");
  const call = result.xCall;
  if (!call || typeof call.propertyKey !== "string" || call.propertyKey.length === 0) fail(label + " propertyKey");
  if (!call || typeof call.receiver !== "string" || call.receiver.length === 0) fail(label + " receiver");
  if (!call || typeof call.expression !== "string" || call.expression.indexOf("x[") !== 0 || call.expression.indexOf("][") < 0) {
    fail(label + " throwing expression identity");
  }
  if (result.foRequests !== 0) fail(label + " foRequests " + result.foRequests);
  if (result.framePqType === "function" || (frame && frame.framePqType === "function")) fail(label + " PQak3 function");
  if (result.serverAccepted === true) fail(label + " serverAccepted");
  if (result.restrictions && result.restrictions.wroteServerAccepted) fail(label + " wroteServerAccepted");
  if (result.restrictions && result.restrictions.replayedFoBody) fail(label + " replayedFoBody");
  const uncaught = uncaughtRecord(result);
  const message = uncaught ? String(uncaught.uncaught) : "";
  if (message.indexOf("is not a constructor") !== -1) fail(label + " constructor regression " + message);
  const stack = uncaught && uncaught.stack ? JSON.stringify(uncaught.stack) : "";
  if (stack.indexOf("Timeout.It") === -1) fail(label + " Timeout.It missing");
}

function main() {
  const paths = process.argv.slice(2);
  if (paths.length !== 2) {
    process.stderr.write("usage: node runtime/realm-probe-assert.js <result1.json> <result2.json>\n");
    process.exit(2);
  }
  const first = load(paths[0]);
  const second = load(paths[1]);
  checkOne("run1", first);
  checkOne("run2", second);
  if (!first.xCall || !second.xCall || first.xCall.propertyKey !== second.xCall.propertyKey) {
    fail("property keys differ");
  }
  if (!process.exitCode) {
    process.stdout.write("OK propertyKey=" + first.xCall.propertyKey + " receiver=" + first.xCall.receiver + " expression=" + first.xCall.expression + "\n");
  }
}

main();
