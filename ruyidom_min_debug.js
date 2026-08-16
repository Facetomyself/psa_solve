/*
 * 最小调试 runner：加载 repro pageHtml，逐个 script 单独执行，
 * 定位「missing ) after argument list」的真实来源。
 */
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
    var html = readUtf8("D:\\reverse_ENV\\tmp\\pageHtml-repro.html");
    var errors = [];
    var vc = new RuyiDOM.VirtualConsole({ historyLimit: 30 });
    vc.on("ruyidomError", function (error) {
      errors.push({
        name: String(error && error.name || "Error"),
        msg: String(error && error.message || error).slice(0, 200),
        fileName: String(error && error.fileName || ""),
        line: error && error.lineNumber != null ? Number(error.lineNumber) : -1,
      });
    });
    dom = new RuyiDOM(html, {
      secure: true,
      webgl: true,
      url: "https://www.psacard.com/cert/143963534/psa",
      referrer: "https://www.psacard.com/",
      runScripts: "dangerously",
      virtualConsole: vc,
    });
    dom.pump(8000);
    print(JSON.stringify({
      ok: true,
      errors: errors,
      wrapperRan: Number(dom.eval("window.__wrapperRan||0")),
      title: String(dom.eval("document.title")),
      optKeys: String(dom.eval("Object.keys(window._cf_chl_opt||{}).length")),
    }));
    RuyiDOM.exit(0);
  } catch (error) {
    print(JSON.stringify({ ok: false, error: String(error && error.stack || error) }));
    RuyiDOM.exit(1);
  }
});
