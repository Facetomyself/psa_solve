/*
 * RuyiDOM Worker/blob postMessage 往返 smoke：
 * 页面内创建 blob Worker -> postMessage('ping') -> 等 onmessage 回传。
 * 输出 stdout 单行 JSON {ok, workerCreated, workerErr, gotMsg, msgEvents}
 */
RuyiDOM.main(function () {
  var dom;
  try {
    var html =
      "<html><body><script>" +
      "window.__msgEvents=[];" +
      "try{" +
      "var __code='self.onmessage=function(e){self.postMessage(\"pong:\"+e.data);};';" +
      "var __url=URL.createObjectURL(new Blob([__code],{type:'text/javascript'}));" +
      "window.__w=new Worker(__url);" +
      "window.__w.onmessage=function(e){window.__gotMsg=String(e.data);window.__msgEvents.push({t:'onmessage',d:String(e.data)});};" +
      "window.__w.onerror=function(e){window.__msgEvents.push({t:'onerror',m:String(e.message||'')});};" +
      "window.__w.postMessage('ping');" +
      "window.__workerOk=true;" +
      "}catch(e){window.__workerErr=String(e&&e.message||e);window.__workerOk=false;}" +
      "</" + "script></body></html>";

    dom = new RuyiDOM(html, {
      url: "https://www.psacard.com/cert/143963534/psa",
      referrer: "https://www.psacard.com/",
      runScripts: "dangerously",
    });
    dom.pump(6000);

    print(JSON.stringify({
      ok: true,
      workerOk: Boolean(dom.eval("window.__workerOk")),
      workerErr: String(dom.eval("window.__workerErr||''")),
      gotMsg: String(dom.eval("window.__gotMsg||''")),
      msgEvents: String(dom.eval("JSON.stringify(window.__msgEvents||[])")),
      workerType: String(dom.eval("typeof Worker")),
      blobType: String(dom.eval("typeof Blob")),
      urlType: String(dom.eval("typeof URL.createObjectURL")),
    }));
    RuyiDOM.exit(0);
  } catch (error) {
    print(JSON.stringify({ ok: false, error: String(error && error.stack || error) }));
    RuyiDOM.exit(1);
  }
});
