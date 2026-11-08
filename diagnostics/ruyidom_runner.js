/*
 * runner.js — PSA CF 5s 盾补环境执行 harness（干净版，无诊断探针）
 *
 * 模块职责：
 *   - 读取挑战材料（403 页 + orchestrate + 可选 __cf_bm cookie）
 *   - 注入 runtime/code.js 补环境（外部宿主面 patch）
 *   - 本地 serve orchestrate / 放行提交请求到真实网络
 *   - pump 求解窗口后输出结构化结果 JSON
 *
 * 输入（RUYIDOM_INPUT_JSON / RUYIDOM_INPUT_FILE）：
 *   challengeHtmlPath  403 挑战页 HTML 本地路径
 *   orchestrateJsPath  orchestrate JS 本地路径
 *   challengeUrl       页面 URL
 *   cookie             可选 __cf_bm（提交凭证）
 *   codeJsPath         补环境脚本路径（默认 runtime/code.js）
 *   pumpMs             求解窗口毫秒（默认 45000）
 * 输出：stdout 单行 JSON {ok, errors, wire, pageState}
 */
function readInput() {
  var raw = "{}";
  try {
    var env = Components.classes["@mozilla.org/process/environment;1"]
      .getService(Components.interfaces.nsIEnvironment);
    if (env.exists("RUYIDOM_INPUT_FILE")) {
      raw = readUtf8(env.get("RUYIDOM_INPUT_FILE"));
    } else if (env.exists("RUYIDOM_INPUT_JSON")) {
      raw = env.get("RUYIDOM_INPUT_JSON");
    }
  } catch (error) {}
  return JSON.parse(raw || "{}");
}

function readUtf8(path) {
  var Cc = Components.classes;
  var Ci = Components.interfaces;
  var file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
  file.initWithPath(path);
  var stream = Cc["@mozilla.org/network/file-input-stream;1"]
    .createInstance(Ci.nsIFileInputStream);
  stream.init(file, -1, 0, 0);
  var converter = Cc["@mozilla.org/intl/converter-input-stream;1"]
    .createInstance(Ci.nsIConverterInputStream);
  converter.init(stream, "UTF-8", 0, Ci.nsIConverterInputStream.DEFAULT_REPLACEMENT_CHARACTER);
  var output = "";
  var chunk = {};
  while (converter.readString(0x8000, chunk) !== 0) output += chunk.value;
  converter.close();
  return output;
}

RuyiDOM.main(function () {
  var dom;
  try {
    var input = readInput();
    var challengeHtml = readUtf8(String(input.challengeHtmlPath));
    var orchestrateJs = readUtf8(String(input.orchestrateJsPath));
    var codeJs = "";
    try {
      codeJs = readUtf8(String(input.codeJsPath ||
        "D:\\reverse_ENV\\workspace\\psa_solve\\runtime\\code.js"));
    } catch (error) {}

    var pumpMs = Number(input.pumpMs || 45000);
    var challengeUrl = String(input.challengeUrl ||
      "https://www.psacard.com/cert/143963534/psa");

    var errors = 0;
    var errorShapes = [];
    var virtualConsole = new RuyiDOM.VirtualConsole({ historyLimit: 30 });
    virtualConsole.on("ruyidomError", function (error) {
      errors += 1;
      if (errorShapes.length < 5) {
        errorShapes.push({
          name: error && error.name ? String(error.name) : "Error",
          messagePrefix: String(error && error.message || error).slice(0, 200),
        });
      }
    });

    var observedWire = [];
    // resources：orchestrate 本地 serve；challenge-platform 提交放行真实网络
    var resources = {
      blockUnmapped: false,
      map: {},
      handler: function (request) {
        var url = request && request.url != null ? String(request.url) : "";
        var kind = request && request.kind ? String(request.kind) : "unknown";
        if (kind === "script" && url.indexOf("challenge-platform") !== -1) {
          observedWire.push({ kind: "script-served", url: url.slice(0, 200) });
          return { status: 200, headers: { "content-type": "application/javascript" }, body: orchestrateJs };
        }
        if (url.indexOf("challenge-platform") !== -1 &&
            (kind === "xhr" || kind === "fetch" || kind === "document" || kind === "other")) {
          observedWire.push({
            kind: "net-pass",
            method: request && request.method ? String(request.method) : "",
            url: url.slice(0, 300),
          });
          return null;
        }
        if (kind === "xhr" || kind === "fetch") {
          return { status: 200, headers: { "content-type": "application/json" }, body: "{}" };
        }
        // 页面源站：内存里的挑战页 URL 回本地 HTML，不放行 www.psacard.com。
        var pagePath = String(challengeUrl || "").split("?")[0];
        var reqPath = url.split("?")[0];
        if (pagePath && reqPath === pagePath) {
          observedWire.push({
            kind: "local-html",
            method: request && request.method ? String(request.method) : "",
            url: reqPath.slice(0, 200),
          });
          return { status: 200, headers: { "content-type": "text/html" }, body: challengeHtml };
        }
        return null;
      },
    };

    // 2026-08-15 外部宿主缺口，不是新算法：about:blank viewer 上
    // history.replaceState/pushState 抛 SecurityError。只抽这两条包装。
    // 不依赖 Storage，也不带 v1 的 opcode/UpvLO0/ZHfDS6 插桩。原包装无 toString。
    var historyHost = "(function(){" +
      "try{var __rs=history.replaceState.bind(history);history.replaceState=function(){try{return __rs.apply(history,arguments);}catch(e){return undefined;}};}catch(e){}" +
      "try{var __ps=history.pushState.bind(history);history.pushState=function(){try{return __ps.apply(history,arguments);}catch(e){return undefined;}};}catch(e){}" +
      "})();";

    // 页面组装：移除 meta CSP + history 宿主包装。codeJs 仅在显式读到时注入。
    var cookieScript = "";
    try {
      if (String(input.cookie || "")) {
        cookieScript = "<script>try{document.cookie=" +
          JSON.stringify(String(input.cookie)) +
          ";}catch(e){}</" + "script>";
      }
    } catch (error) {}
    var codeScript = codeJs ? "<script>" + codeJs + "</" + "script>" : "";
    var pageHtml = String(challengeHtml)
      .replace(/<meta\s+http-equiv=["']content-security-policy["'][^>]*>/gi, "")
      .replace("<head>", function () {
        return "<head><script>" + historyHost + "</" + "script>" + codeScript + cookieScript;
      });

    var options = {
      secure: true,
      webgl: true,
      url: challengeUrl,
      referrer: "https://www.psacard.com/",
      runScripts: "dangerously",
      virtualConsole: virtualConsole,
      resources: resources,
    };
    dom = new RuyiDOM(pageHtml, options);
    dom.pump(pumpMs);

    var pageState = {
      errors: errors,
      title: String(dom.eval("document.title")),
      bodyLen: Number(dom.eval("document.body ? document.body.innerHTML.length : 0")),
      location: String(dom.eval("location.href")),
      cookie: String(dom.eval("document.cookie").slice(0, 800)),
      optKeys: String(dom.eval("Object.keys(window._cf_chl_opt||{}).length")),
      xhr: String(dom.eval("JSON.stringify(window.__patchXhr||[])").slice(0, 1500)),
    };
    print(JSON.stringify({
      ok: true,
      errorShapes: errorShapes,
      wire: observedWire,
      pageState: pageState,
    }));
    RuyiDOM.exit(0);
  } catch (error) {
    print(JSON.stringify({ ok: false, error: String(error && error.stack || error) }));
    RuyiDOM.exit(1);
  }
});
