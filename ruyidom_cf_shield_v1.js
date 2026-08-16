/*
 * RuyiDOM CF 5s 盾最小 runner v1（真实 Gecko）：
 * 加载 PSA 403 managed challenge 页 -> 内联 init 执行 -> orchestrate JS
 * 经 resources.handler 本地映射加载 -> 自然求解 -> 捕获提交请求边界。
 *
 * 输入（RUYIDOM_INPUT_JSON，小 JSON）：
 *   challengeHtmlPath  403 挑战页 HTML 本地路径
 *   orchestrateJsPath  chl-page-orchestrate.js 本地路径
 *   challengeUrl       带 __cf_chl_tk 的完整 URL（从 403 页 cUPMDTk 提取）
 * 输出：stdout 单行 JSON {ok, errors, errorShapes, wire, pageState}
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

function writeUtf8(path, content) {
  var Cc = Components.classes;
  var Ci = Components.interfaces;
  var file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
  file.initWithPath(path);
  var stream = Cc["@mozilla.org/network/file-output-stream;1"]
    .createInstance(Ci.nsIFileOutputStream);
  stream.init(file, 0x02 | 0x08 | 0x20, 0o644, 0); // WRITE|CREATE|TRUNCATE
  var converter = Cc["@mozilla.org/intl/converter-output-stream;1"]
    .createInstance(Ci.nsIConverterOutputStream);
  converter.init(stream, "UTF-8", 0, 0);
  converter.writeString(content);
  converter.close();
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
  var observedWire = [];
  try {
    var input = readInput();
    var challengeHtml = readUtf8(String(input.challengeHtmlPath));
    var orchestrateJs = readUtf8(String(input.orchestrateJsPath));
    var jsdJs = "";
    try {
      jsdJs = readUtf8(String(input.jsdJsPath ||
        "D:\\reverse_ENV\\workspace\\psa_solve\\challenge-material\\jsd-main-solver.js"));
    } catch (error) { jsdJs = ""; }
    // 只读诊断插桩（纯表达式，逗号位置合法）：
    // 1) IF 首行解码键；2) IF 循环条件前计数（追踪循环推进）
    var probeExpr = "window.__ruyiIFKeys=(rv(wI.J))+','+(rv(wI.IV)),";
    if (orchestrateJs.indexOf("IV=T[rv(wI.J)][rv(wI.IV)]()") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "IV=T[rv(wI.J)][rv(wI.IV)]()",
        probeExpr + "IV=T[rv(wI.J)][rv(wI.IV)]()"
      );
    }
    if (orchestrateJs.indexOf("Ip<IV[rv(wI.Ip)]") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Ip<IV[rv(wI.Ip)]",
        "window.__ruyiIFLoop=Ip,Ip<IV[rv(wI.Ip)]"
      );
    }
    // 插桩 2：new T[1910键] 前解码键；ID 类型（回调体）
    if (orchestrateJs.indexOf("Ii=new T[rv(wI.Ia)](") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Ii=new T[rv(wI.Ia)](",
        "window.__ruyiTkey=(rv(wI.Ia))+','+(typeof T[rv(wI.Ia)]),Ii=new T[rv(wI.Ia)]("
      );
    }
    if (orchestrateJs.indexOf("J[rv(wI.Ii)](ID,IV[Ip])") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "J[rv(wI.Ii)](ID,IV[Ip])",
        "window.__ruyiID=(typeof ID),J[rv(wI.Ii)](ID,IV[Ip])"
      );
    }
    // 插桩 3：ID 状态机 case 进度（case '5' 前记录）
    if (orchestrateJs.indexOf("T[rf(w9.Is)][rf(w9.Il)]?.[rf(w9.Ih)](IG)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "T[rf(w9.Is)][rf(w9.Il)]?.[rf(w9.Ih)](IG)",
        "window.__ruyiCase='5',window.__ruyiKeys5=(rf(w9.Is))+','+(rf(w9.Il))+','+(rf(w9.Ih))+','+(typeof IG)+',arr='+(Array.isArray(T[rf(w9.Is)][rf(w9.Il)])),T[rf(w9.Is)][rf(w9.Il)]?.[rf(w9.Ih)](IG)"
      );
    }
    // case '2' 变量类型插桩（ID 状态机 Ic 集合处理）
    if (orchestrateJs.indexOf("case`2`:if(IV[X7(DF.Z0)](Ic[X7(DF.Z1)],0)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "case`2`:if(IV[X7(DF.Z0)](Ic[X7(DF.Z1)],0)",
        "case`2`:window.__ruyiC2=typeof Ic+','+typeof PX+','+typeof PI+','+typeof IV[X7(DF.IU)];if(IV[X7(DF.Z0)](Ic[X7(DF.Z1)],0)"
      );
    }
    // T[1354] 链解码插桩（Pg 调用的三层链）
    if (orchestrateJs.indexOf("P9=T[ZZ(1354)][ZZ(824)]") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "P9=T[ZZ(1354)][ZZ(824)]",
        "window.__ruyiT1354=(ZZ(1354))+','+(typeof T[ZZ(1354)]),P9=T[ZZ(1354)][ZZ(824)]"
      );
    }
    // ID case '2' 循环体插桩（三个元素方法全插）
    if (orchestrateJs.indexOf("Ic[Io][X7(DF.Il)](X7(DF.Z3),It)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Ic[Io][X7(DF.Il)](X7(DF.Z3),It)",
        "window.__ruyiC2loop=Io+',m='+(X7(DF.Il))+',el='+(typeof Ic[Io])+','+(Ic[Io]?Ic[Io].tagName||'?':'null'),Ic[Io][X7(DF.Il)](X7(DF.Z3),It)"
      );
      orchestrateJs = orchestrateJs.replace(
        "Ic[Io][X7(DF.IW)](IV[X7(DF.Z4)],IV[X7(DF.Z5)])",
        "window.__ruyiC2m2=(X7(DF.IW)),Ic[Io][X7(DF.IW)](IV[X7(DF.Z4)],IV[X7(DF.Z5)])"
      );
      orchestrateJs = orchestrateJs.replace(
        "Ic[Io][X7(DF.Z6)](X7(DF.Z7),X7(DF.Z8))",
        "window.__ruyiC2m3=(X7(DF.Z6)),Ic[Io][X7(DF.Z6)](X7(DF.Z7),X7(DF.Z8))"
      );
    }
    // Pg 三层链完整解码插桩：键 + 各级类型 + 调用返回值（复用 J[ZZ(810)] 槽位承接返回值）
    if (orchestrateJs.indexOf("IV=J,T[XF(FQ.IV)][XF(FQ.Ip)][XF(FQ.Ii)](IV[XF(FQ.Ia)])") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "IV=J,T[XF(FQ.IV)][XF(FQ.Ip)][XF(FQ.Ii)](IV[XF(FQ.Ia)])",
        "IV=J,window.__ruyiPg=(XF(FQ.IV))+','+(XF(FQ.Ip))+','+(XF(FQ.Ii))+','+(XF(FQ.Z))+','+(XF(FQ.J))+',t0='+(typeof T[XF(FQ.IV)])+',t1='+(typeof T[XF(FQ.IV)][XF(FQ.Ip)])+',t2='+(typeof T[XF(FQ.IV)][XF(FQ.Ip)][XF(FQ.Ii)]),J[XF(FQ.Z)]=T[XF(FQ.IV)][XF(FQ.Ip)][XF(FQ.Ii)](IV[XF(FQ.Ia)]),window.__ruyiPgRet=typeof J[XF(FQ.Z)]+','+String(J[XF(FQ.Z)]).slice(0,100),J[XF(FQ.Z)]"
      );
    }
    // Pt 三元分支判定插桩：记录走 success 还是 fail 分支
    if (orchestrateJs.indexOf("Z?Z[Xw(FF.Z)][Xw(FF.J)]=Xw(FF.IV):T[Xw(FF.Ip)]") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Z?Z[Xw(FF.Z)][Xw(FF.J)]=Xw(FF.IV):T[Xw(FF.Ip)]",
        "window.__ruyiPtBr=Z?'success':'fail',Z?Z[Xw(FF.Z)][Xw(FF.J)]=Xw(FF.IV):T[Xw(FF.Ip)]"
      );
    }
    // yR VM call-opcode 崩溃点插桩（branch1）：opcode 值 + 方法键 + 寄存器槽 + IG/It 类型与内容
    if (orchestrateJs.indexOf("=It===void 0?IG():IG[J6(ND.Io)](It);") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "=It===void 0?IG():IG[J6(ND.Io)](It);",
        "=It===void 0?(window.__ruyiYrOp=Io+',k='+(J6(ND.Io))+',reg='+(J6(ND.IG))+','+(Ig)+','+(IV)+',tIG='+(typeof IG)+',sIG='+String(IG).slice(0,40)+',tIt='+(typeof It)+',sIt='+String(It).slice(0,60),IG()):(window.__ruyiYrOp=Io+',k='+(J6(ND.Io))+',reg='+(J6(ND.IG))+','+(Ig)+','+(IV)+',tIG='+(typeof IG)+',sIG='+String(IG).slice(0,40)+',tIt='+(typeof It)+',sIt='+String(It).slice(0,60),IG[J6(ND.Io)](It));"
      );
    }
    // P7 入口插桩：记录每次调用的参数类型与计数
    if (orchestrateJs.indexOf("function P7(Z,J,IV,Dr,DX,DJ,DZ,JE,Ip,Ii,Ia,Ie){if(Dr={Z:1528") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "function P7(Z,J,IV,Dr,DX,DJ,DZ,JE,Ip,Ii,Ia,Ie){if(Dr={Z:1528",
        "function P7(Z,J,IV,Dr,DX,DJ,DZ,JE,Ip,Ii,Ia,Ie){window.__ruyiP7N=(window.__ruyiP7N||0)+1;window.__ruyiP7Arg=window.__ruyiP7N+':Z='+(typeof Z)+',J='+(typeof J)+',IV='+(typeof IV);if(Dr={Z:1528"
      );
    }
    // IY 嵌套机（IQ 回调）入口与 case '1' 插桩：记录程序串与 Ii/Ic 状态
    if (orchestrateJs.indexOf("It=ry(Rj.Z)[ry(Rj.J)](`|`),Io=0;!![];)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "It=ry(Rj.Z)[ry(Rj.J)](`|`),Io=0;!![];)",
        "It=ry(Rj.Z)[ry(Rj.J)](`|`),Io=0,window.__ruyiIqProg=String(It),window.__ruyiIqEntry='Ii='+(typeof Ii)+',Ic='+(typeof Ic);!![];)"
      );
    }
    if (orchestrateJs.indexOf("case`1`:setTimeout(P7,100,Ii,Ic);") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "case`1`:setTimeout(P7,100,Ii,Ic);",
        "case`1`:window.__ruyiIq1='Ii='+(typeof Ii)+',Ic='+(typeof Ic);setTimeout(P7,100,Ii,Ic);"
      );
    }
    // 新版本 fq 入口计数 + call-opcode 插桩（hk 崩溃定位）
    if (orchestrateJs.indexOf("function fq(Yv,zv,o,U,hV,hI,hp,hn,hE,hL,he,hW,hk,hb,hw){") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "function fq(Yv,zv,o,U,hV,hI,hp,hn,hE,hL,he,hW,hk,hb,hw){",
        "function fq(Yv,zv,o,U,hV,hI,hp,hn,hE,hL,he,hW,hk,hb,hw){window.__ruyiFqN=(window.__ruyiFqN||0)+1;"
      );
    }
    if (orchestrateJs.indexOf("hW=U[this.m][hW].o,hk=void 0===hW?hb:hW[hb],he!==0)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "hW=U[this.m][hW].o,hk=void 0===hW?hb:hW[hb],he!==0)",
        "hW=U[this.m][hW].o,window.__ruyiFq=(typeof hW)+',sW='+String(hW).slice(0,60)+',m='+String(hb).slice(0,60),hk=void 0===hW?hb:hW[hb],he!==0)"
      );
    } else if (orchestrateJs.indexOf("hW=U[this.m][hW].o,hk=void 0===hW?hb:hW[hb],he!==0){") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "hW=U[this.m][hW].o,hk=void 0===hW?hb:hW[hb],he!==0){",
        "hW=U[this.m][hW].o,window.__ruyiFq=(typeof hW)+',sW='+String(hW).slice(0,60)+',m='+String(hb).slice(0,60),hk=void 0===hW?hb:hW[hb],he!==0){"
      );
    }
    // Iw setTimeout(P7,100,Ig,IG) 调用点插桩：记录实参类型
    if (orchestrateJs.indexOf("setTimeout(P7,100,Ig,IG)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "setTimeout(P7,100,Ig,IG)",
        "window.__ruyiIwCall=(typeof Ig)+','+(typeof IG)+',sIg='+String(Ig).slice(0,60)+',sIG='+String(IG).slice(0,60),setTimeout(P7,100,Ig,IG)"
      );
    }
    // yR 寄存器重定向插桩：It 对象 + 原始 IG 寄存器（重定向前）
    if (orchestrateJs.indexOf("IG=J[IV^IG],IG=It===void 0?IG:It[IG],Z[J6(ND.It)](Io,0))") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "IG=J[IV^IG],IG=It===void 0?IG:It[IG],Z[J6(ND.It)](Io,0))",
        "IG=J[IV^IG],window.__ruyiYrRed=(typeof It)+',sIt='+String(It).slice(0,80)+',rawIG='+String(IG).slice(0,80),IG=It===void 0?IG:It[IG],Z[J6(ND.It)](Io,0))"
      );
    }
    // yR call-opcode branch2 插桩：崩溃分支（Io===1，双参调用）
    if (orchestrateJs.indexOf("J[IV^Ig]=void 0===It?Z[J6(ND.Ij)](IG,Ip):IG[J6(ND.Io)](It,Ip)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "J[IV^Ig]=void 0===It?Z[J6(ND.Ij)](IG,Ip):IG[J6(ND.Io)](It,Ip)",
        "window.__ruyiYrOp2=Io+',k='+(J6(ND.Io))+',tIG='+(typeof IG)+',sIG='+String(IG).slice(0,40)+',tIt='+(typeof It)+',sIt='+String(It).slice(0,60)+',tIp='+(typeof Ip)+',sIp='+String(Ip).slice(0,60),J[IV^Ig]=void 0===It?Z[J6(ND.Ij)](IG,Ip):IG[J6(ND.Io)](It,Ip)"
      );
    }
    // PJ 入口插桩：J 参数类型与内容（entry 属性字符串）
    if (orchestrateJs.indexOf("function PJ(Z,J,DN,X5,IV,Ip,Ii,Ia){(DN={Z:2121") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "function PJ(Z,J,DN,X5,IV,Ip,Ii,Ia){(DN={Z:2121",
        "function PJ(Z,J,DN,X5,IV,Ip,Ii,Ia){window.__ruyiPJ=typeof J+','+String(J).slice(0,100);(DN={Z:2121"
      );
      // PJ 条件块插桩：T[1354键] 类型 + Z 值
      orchestrateJs = orchestrateJs.replace(
        "IV[X5(DN.It)](Z,X5(DN.Io))&&",
        "window.__ruyiPJ2=String(Z).slice(0,60)+',t1354='+typeof T[X5(DN.Ic)],IV[X5(DN.It)](Z,X5(DN.Io))&&"
      );
    }
    // 全局 case 进度插桩：case 标签后插分号语句（case 标签后语句序列合法）
    orchestrateJs = orchestrateJs.replace(
      /case`(\d+)`:/g,
      "case`$1`:window.__ruyiCaseNow=$1;"
    );
    // VM 调度器数值 case 序列插桩（记录 opcode 执行序列，上限 5000）
    orchestrateJs = orchestrateJs.replace(
      /case (\d+):(y\w+)\[/g,
      "case $1:window.__ruyiVmSeq=(window.__ruyiVmSeq||[]);if(window.__ruyiVmSeq.length<5000)window.__ruyiVmSeq.push($1);$2["
    );
    // yQ 常量物化写追踪：记录每次寄存器写入（reg=type,value 前 500 字符，上限 600）
    if (orchestrateJs.indexOf("J[Ia]=Ie,J[Z[J3(N6.IM)](Ig,IV)]=It}}") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "J[Ia]=Ie,J[Z[J3(N6.IM)](Ig,IV)]=It}}",
        "J[Ia]=Ie,window.__ruyiYqW=(window.__ruyiYqW||[]),window.__ruyiYqW.length<600&&window.__ruyiYqW.push('yQ.'+(Z[J3(N6.IM)](Ig,IV))+'='+(typeof It)+','+String(It).slice(0,500)),J[Z[J3(N6.IM)](Ig,IV)]=It}}"
      );
    }
    // ye call-opcode 顶部插桩：基对象 + 方法名 + 参数形态（属性查找后、分支前）
    if (orchestrateJs.indexOf("Io=IG===void 0?Ic:IG[Ic],It!==0)") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Io=IG===void 0?Ic:IG[Ic],It!==0)",
        "Io=IG===void 0?Ic:IG[Ic],window.__ruyiYe=It+',k='+String(Ic).slice(0,80)+',tIG='+(typeof IG)+',sIG='+String(IG).slice(0,50)+',tIo='+(typeof Io),It!==0)"
      );
    }
    // yX 寄存器移动写追踪
    if (orchestrateJs.indexOf("Ip[Ig]=IG,Ip[Ii^It]=Ia}") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Ip[Ig]=IG,Ip[Ii^It]=Ia}",
        "Ip[Ig]=IG,window.__ruyiYqW=(window.__ruyiYqW||[]),window.__ruyiYqW.length<300&&window.__ruyiYqW.push('yX.'+(Ii^It)+'='+(typeof Ia)+','+String(Ia).slice(0,50)),Ip[Ii^It]=Ia}"
      );
    }
    // yD 常量写入追踪（写两个寄存器）
    if (orchestrateJs.indexOf("Ip[Ia]=IV[J5(NX.Ig)](Ie^IV[J5(NX.Ia)](Ig[IG],20)+256&255,46),Ip[Ii]=It}") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Ip[Ia]=IV[J5(NX.Ig)](Ie^IV[J5(NX.Ia)](Ig[IG],20)+256&255,46),Ip[Ii]=It}",
        "Ip[Ia]=IV[J5(NX.Ig)](Ie^IV[J5(NX.Ia)](Ig[IG],20)+256&255,46),window.__ruyiYqW=(window.__ruyiYqW||[]),window.__ruyiYqW.length<300&&window.__ruyiYqW.push('yD.'+(Ii)+'='+(typeof It)+','+String(It).slice(0,50)),Ip[Ii]=It}"
      );
    }
    // y7 属性获取写追踪
    if (orchestrateJs.indexOf("Ip[It]=Ip[Ii][Ip[Io]]}") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "Ip[It]=Ip[Ii][Ip[Io]]}",
        "Ip[It]=Ip[Ii][Ip[Io]],window.__ruyiYqW=(window.__ruyiYqW||[]),window.__ruyiYqW.length<300&&window.__ruyiYqW.push('y7.'+(It)+'=get,'+(typeof Ip[It])+','+String(Ip[It]).slice(0,50)+',src='+(typeof Ip[Ii])+','+String(Ip[Ii]).slice(0,30)+',key='+String(Ip[Io]).slice(0,40))}"
      );
    }
    // yj 对象字段写追踪
    if (orchestrateJs.indexOf("IG[Ic][`o`]=Ip[Ia^Ii];") !== -1) {
      orchestrateJs = orchestrateJs.replace(
        "IG[Ic][`o`]=Ip[Ia^Ii];",
        "IG[Ic][`o`]=Ip[Ia^Ii],window.__ruyiYqW=(window.__ruyiYqW||[]),window.__ruyiYqW.length<300&&window.__ruyiYqW.push('yj.'+(Ic)+'.o='+(typeof Ip[Ia^Ii])+','+String(Ip[Ia^Ii]).slice(0,50));"
      );
    }
    // 落盘插桩后的 served 代码（列号映射用，不进 Git）
    try {
      writeUtf8(String(input.servedDumpPath || "D:\\reverse_ENV\\workspace\\psa_solve\\challenge-material\\orchestrate-served.js"), orchestrateJs);
    } catch (error) {}
    var challengeUrl = String(input.challengeUrl ||
      "https://www.psacard.com/cert/143963534/psa");

    var errors = 0;
    var errorShapes = [];
    var virtualConsole = new RuyiDOM.VirtualConsole({ historyLimit: 30 });
    virtualConsole.on("ruyidomError", function (error) {
      errors += 1;
      if (errorShapes.length < 8) {
        errorShapes.push({
          name: error && error.name ? String(error.name) : "Error",
          messagePrefix: String(error && error.message || error).slice(0, 200),
          stackHead: String(error && error.stack || "").split("\n").slice(0, 6).join(" | ").slice(0, 700),
          fileName: error && error.fileName ? String(error.fileName) : "",
          lineNumber: error && error.lineNumber != null ? Number(error.lineNumber) : -1,
        });
      }
    });

    // resources.handler：challenge-platform 脚本返回本地内容；
    // 提交类请求（eb/fo 等）放行到真实网络；其余 xhr 记录后 mock 空响应。
    var resources = {
      blockUnmapped: false,
      map: {},
      handler: function (request) {
        var url = request && request.url != null ? String(request.url) : "";
        var kind = request && request.kind ? String(request.kind) : "unknown";
        if (kind === "script" && url.indexOf("jsd") !== -1) {
          observedWire.push({ kind: "script-served", tag: "jsd", url: url.slice(0, 200) });
          return { status: 200, headers: { "content-type": "application/javascript" }, body: jsdJs };
        }
        if (kind === "script" && url.indexOf("challenge-platform") !== -1) {
          observedWire.push({ kind: "script-served", tag: "orchestrate", url: url.slice(0, 200) });
          return { status: 200, headers: { "content-type": "application/javascript" }, body: orchestrateJs };
        }
        if (url.indexOf("challenge-platform") !== -1 && (kind === "xhr" || kind === "fetch" || kind === "document" || kind === "other")) {
          observedWire.push({ kind: "net-pass", kind2: kind, method: request && request.method ? String(request.method) : "", url: url.slice(0, 260) });
          return null;
        }
        if (kind === "xhr" || kind === "fetch") {
          var body = request && request.body != null ? String(request.body) : "";
          observedWire.push({
            kind: kind,
            method: request && request.method ? String(request.method) : "",
            url: url.slice(0, 260),
            bodyLength: body.length,
            bodyHead: body.slice(0, 200),
          });
          return { status: 200, headers: { "content-type": "application/json" }, body: "{}" };
        }
        return null;
      },
    };

    // 页面加载前 wrapper：记录 XHR open/send 边界（不包 Proxy，只记 URL/body）
    var wrapper = "(function(){" +
      // ---- storage 内存桩（原型方法包装）：SecurityError 在 getItem/setItem
      // 调用时抛出（属性访问本身不抛）；包原型方法让真实 storage 对象变安全 ----
      "var __store={};" +
      "try{var __g=Storage.prototype.getItem,__st=Storage.prototype.setItem,__rm=Storage.prototype.removeItem,__cl=Storage.prototype.clear,__ky=Storage.prototype.key,__len=Object.getOwnPropertyDescriptor(Storage.prototype,'length');" +
      "Storage.prototype.getItem=function(k){try{return __g.call(this,k);}catch(e){return Object.prototype.hasOwnProperty.call(__store,k)?__store[k]:null;}};" +
      "Storage.prototype.setItem=function(k,v){try{__st.call(this,k,v);}catch(e){__store[k]=String(v);}};" +
      "Storage.prototype.removeItem=function(k){try{__rm.call(this,k);}catch(e){delete __store[k];}};" +
      "Storage.prototype.clear=function(){try{__cl.call(this);}catch(e){__store={};}};" +
      "Storage.prototype.key=function(i){try{return __ky.call(this,i);}catch(e){return Object.keys(__store)[i]||null;}};" +
      "if(__len&&__len.get){Object.defineProperty(Storage.prototype,'length',{configurable:true,get:function(){try{return __len.get.call(this);}catch(e){return Object.keys(__store).length;}}});}" +
      "}catch(e){}" +
      // ---- history 包：about:blank viewer 的 replaceState/pushState 抛
      // SecurityError（init script 用它构造 __cf_chl_rt_tk URL 重写）----
      "try{var __rs=history.replaceState.bind(history);history.replaceState=function(){try{return __rs.apply(history,arguments);}catch(e){return undefined;}};}catch(e){}" +
      "try{var __ps=history.pushState.bind(history);history.pushState=function(){try{return __ps.apply(history,arguments);}catch(e){return undefined;}};}catch(e){}" +
      "window.__wrapperRan=(window.__wrapperRan||0)+1;" +
      "try{if(typeof performance.getEntries!=='function'){performance.getEntries=function(){return [];};}if(typeof performance.getEntriesByType!=='function'){performance.getEntriesByType=function(){return [];};}if(typeof performance.getEntriesByName!=='function'){performance.getEntriesByName=function(){return [];};}}catch(e){}" +
      "window.__ruyiCEN=0;window.__ruyiLastTag='';" +
      "try{var __origCEN=document.createElementNS;if(typeof __origCEN==='function'){document.createElementNS=function(ns,tag){window.__ruyiCEN+=1;window.__ruyiLastTag=String(tag);return __origCEN.call(document,ns,tag);};}}catch(e){}" +
      "window.__ruyiCE=0;" +
      "try{var __origCE=document.createElement;document.createElement=function(tag){window.__ruyiCE+=1;return __origCE.call(document,tag);};}catch(e){}" +
      "window.__ruyiOptAssignments=[];" +
      "try{var __origOpt=null;Object.defineProperty(window,'_cf_chl_opt',{configurable:true," +
      "get:function(){return __origOpt;}," +
      "set:function(v){window.__ruyiOptAssignments.push({kind:'whole',type:typeof v,keys:Object.keys(v||{}).length});__origOpt=v;" +
      "try{var __cur=v&&v.yQYB9;Object.defineProperty(v,'yQYB9',{configurable:true," +
      "get:function(){return __cur;}," +
      "set:function(nv){window.__ruyiOptAssignments.push({kind:'yQYB9-set',type:typeof nv});__cur=nv;}});}catch(e){window.__ruyiOptAssignments.push({kind:'yQYB9-define-fail',err:String(e).slice(0,80)});}} });}catch(e){}" +
      "window.__ruyiEvalErrors=[];" +
      "try{var __origEval=window.eval;window.eval=function(code){try{return __origEval.call(window,code);}catch(e){try{window.__ruyiEvalErrors.push({msg:String(e.message||'').slice(0,200),stack:String(e.stack||'').slice(0,900)});}catch(x){}throw e;}};}catch(e){}" +
      "window.__ruyiOnError=[];" +
      "window.onerror=function(msg,src,line,col,err){try{window.__ruyiOnError.push({msg:String(msg).slice(0,200),line:line,col:col,stack:String(err&&err.stack||'').split(String.fromCharCode(10)).slice(0,4).join('|').slice(0,600)});}catch(e){}return false;};" +
      "window.__ruyiEvtErrors=[];" +
      "window.addEventListener('error',function(e){try{window.__ruyiEvtErrors.push({msg:String(e.message||'').slice(0,200),line:e.lineno,col:e.colno,src:String(e.filename||'').slice(0,120),errStack:String(e.error&&e.error.stack||'').split(String.fromCharCode(10)).slice(0,8).join('|').slice(0,700)});}catch(x){}},true);" +
      // ---- 回调宿主包装（诊断轮）：捕获异步回调内的真实错误栈 ----
      "window.__ruyiCbErrors=[];" +
      "var __cbRec=function(host,e){try{window.__ruyiCbErrors.push({host:host,msg:String(e&&e.message||e).slice(0,200),stack:String(e&&e.stack||'').split(String.fromCharCode(10)).slice(0,10).join('|').slice(0,900)});}catch(x){}};" +
      "var __cbWrap=function(host,f){if(typeof f!=='function')return f;return function(){try{return f.apply(this,arguments);}catch(e){__cbRec(host,e);throw e;}};};" +
      "try{var __origThen=Promise.prototype.then;Promise.prototype.then=function(a,b){return __origThen.call(this,__cbWrap('pthen',a),__cbWrap('pcatch',b));};}catch(e){}" +
      "try{var __origCatch=Promise.prototype['catch'];Promise.prototype['catch']=function(a){return __origCatch.call(this,__cbWrap('pcatch2',a));};}catch(e){}" +
      "try{var __origMO=window.MutationObserver;window.MutationObserver=function(cb){return new __origMO(__cbWrap('mutobs',cb));};window.MutationObserver.prototype=__origMO.prototype;window.MutationObserver.prototype.constructor=window.MutationObserver;}catch(e){}" +
      "try{var __origPO=window.PerformanceObserver;window.PerformanceObserver=function(cb){return new __origPO(__cbWrap('perfobs',cb));};window.PerformanceObserver.prototype=__origPO.prototype;window.PerformanceObserver.prototype.constructor=window.PerformanceObserver;}catch(e){}" +
      "try{var __origQM=window.queueMicrotask;if(__origQM){window.queueMicrotask=function(f){return __origQM.call(window,__cbWrap('qmicro',f));};}}catch(e){}" +
      "try{var __origST=window.setTimeout;window.setTimeout=function(){var __args=[];for(var __i=0;__i<arguments.length;__i++)__args.push(__i===0&&typeof arguments[0]==='function'?__cbWrap('timeout',arguments[0]):arguments[__i]);return __origST.apply(window,__args);};}catch(e){}" +
      "try{var __origSI=window.setInterval;window.setInterval=function(){var __args=[];for(var __i=0;__i<arguments.length;__i++)__args.push(__i===0&&typeof arguments[0]==='function'?__cbWrap('interval',arguments[0]):arguments[__i]);return __origSI.apply(window,__args);};}catch(e){}" +
        // ---- 诊断桩：VM 程序期望的 window 全局函数占位（级联记录调用）----
      "window.__ruyiUpvCalled=[];" +
      "try{if(typeof window.UpvLO0!=='function'){window.UpvLO0=function(p){try{var __parts=String(p).split('$');var __k=atob(__parts[0]);var __d=atob(__parts[1]);var __out=new Uint8Array(__d.length);for(var __i=0;__i<__d.length;__i++)__out[__i]=__d.charCodeAt(__i)^__k.charCodeAt(__i%__k.length);window.__ruyiUpvCalled.push({n:window.__ruyiUpvCalled.length,name:'UpvLO0',arg:String(p).slice(0,120),decHex:Array.prototype.slice.call(__out).map(function(b){return (b<16?'0':'')+b.toString(16);}).join(''),decStr:String.fromCharCode.apply(null,__out)});return __out;}catch(e){try{window.__ruyiUpvCalled.push({n:window.__ruyiUpvCalled.length,name:'UpvLO0-err',arg:String(e.message||e).slice(0,120),ret:undefined});}catch(x){}return undefined;}};}}catch(e){}" +
      // ---- Worker / iframe / postMessage 全链路观察 ----
      "window.__ruyiWk=[];" +
      "try{var __origWorker=window.Worker;window.Worker=function(url,opts){var __w=null;try{__w=new __origWorker(url,opts);}catch(e){window.__ruyiWk.push({t:'ctor-err',e:String(e.message||e).slice(0,120)});throw e;}window.__ruyiWk.push({t:'ctor',u:String(url).slice(0,150)});window.__ruyiLastWk=__w;" +
      "try{var __wp=__w.postMessage;__w.postMessage=function(m,t){try{window.__ruyiWk.push({t:'post',d:String(m).slice(0,200)});}catch(e){}return __wp.apply(__w,arguments);};}catch(e){}" +
      "try{var __wa=__w.addEventListener;__w.addEventListener=function(ev,fn){if(String(ev)==='message'||String(ev)==='error'){window.__ruyiWk.push({t:'listen',ev:String(ev)});var __fn=fn;fn=function(e){try{window.__ruyiWk.push({t:'msg-in',ev:String(ev),d:String(e&&e.data).slice(0,200)});}catch(x){}return __fn.apply(this,arguments);};}return __wa.apply(__w,[ev,fn]);};}catch(e){}" +
      "var __desc=Object.getOwnPropertyDescriptor(__w,'onmessage');if(!__desc||!__desc.get){try{var __om=null;Object.defineProperty(__w,'onmessage',{configurable:true,get:function(){return __om;},set:function(fn){window.__ruyiWk.push({t:'listen',ev:'onmessage'});var __fn=fn;__om=function(e){try{window.__ruyiWk.push({t:'msg-in',ev:'onmessage',d:String(e&&e.data).slice(0,200)});}catch(x){}return __fn.call(this,e);};}});}catch(e){}}" +
      "return __w;};}catch(e){}" +
      "try{var __origPm=window.postMessage;window.postMessage=function(m,t){try{window.__ruyiWk.push({t:'win-post',d:String(m).slice(0,200),target:String(t||'')});}catch(e){}return __origPm.apply(this,arguments);};}catch(e){}" +
      "try{var __origAdd=window.addEventListener;window.addEventListener=function(ev,fn){if(String(ev)==='message'){window.__ruyiWk.push({t:'win-listen'});var __fn=fn;fn=function(e){try{window.__ruyiWk.push({t:'win-msg-in',d:String(e&&e.data).slice(0,200),src:String(e&&e.source===window?'self':'other')});}catch(x){}return __fn.apply(this,arguments);};}return __origAdd.apply(this,[ev,fn]);};}catch(e){}" +
      "try{if(typeof window.ZHfDS6!=='function'){window.ZHfDS6=window.eval;}window.__ruyiZhfDs6ToString=String(window.ZHfDS6).slice(0,80);}catch(e){}" +
      "var __o=XMLHttpRequest.prototype.open,__s=XMLHttpRequest.prototype.send;" +
      "window.__ruyiXhr=[];" +
      "XMLHttpRequest.prototype.open=function(m,u){try{window.__ruyiXhr.push({m:String(m),u:String(u),body:null,resp:null});}catch(e){}return __o.apply(this,arguments);};" +
      "XMLHttpRequest.prototype.send=function(b){try{var r=window.__ruyiXhr[window.__ruyiXhr.length-1];if(r){r.body=String(b||'');}var __xh=this;var __rd=this.onreadystatechange;this.onreadystatechange=function(){try{var __rr=window.__ruyiXhr[window.__ruyiXhr.length-1];if(__rr&&__xh.readyState===4){__rr.resp={status:__xh.status,respText:String(__xh.responseText||'').slice(0,300),sc:String((__xh.getResponseHeader&&__xh.getResponseHeader('set-cookie'))||'').slice(0,200)};}}catch(e){}if(__rd)return __rd.apply(this,arguments);};}catch(e){}return __s.apply(this,arguments);};" +
      "window.__ruyiFetch=[];" +
      "var __f=window.fetch;if(__f){window.fetch=function(u,o){try{window.__ruyiFetch.push({u:String(u),method:(o&&o.method)||'GET',body:o&&o.body?String(o.body).slice(0,200):''});}catch(e){}return __f.apply(this,arguments);};}" +
      "try{var __c=String('" + String(input.cookie || "") + "');if(__c){document.cookie=__c;}}catch(e){}" +
      "})();";
    // meta CSP 会阻止无 nonce 的 wrapper script（403 页自带 meta
    // http-equiv CSP）——离线文档无网络攻击面，移除 meta CSP 后注入。
    var pageHtml = String(challengeHtml)
      .replace(/<meta\s+http-equiv=["']content-security-policy["'][^>]*>/gi, "")
      .replace("<head>", function () { return "<head><script>" + wrapper + "</" + "script>"; });
    // 调试落盘：pageHtml 与 wrapper 实际内容（诊断轮）
    try {
      writeUtf8("D:\\reverse_ENV\\workspace\\psa_solve\\challenge-material\\pageHtml-served.html", pageHtml);
      writeUtf8("D:\\reverse_ENV\\workspace\\psa_solve\\challenge-material\\wrapper-served.js", wrapper);
    } catch (error) {}

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
    // 主 pump：让挑战 JS 自然执行（managed challenge 求解 + 提交 + 等服务器响应）
    dom.pump(45000);

    var pageState = {
      ifKeys: String(dom.eval("window.__ruyiIFKeys||''")),
      ifLoop: Number(dom.eval("window.__ruyiIFLoop||-1")),
      tKey: String(dom.eval("window.__ruyiTkey||''")),
      idType: String(dom.eval("window.__ruyiID||''")),
      idCase: String(dom.eval("window.__ruyiCase||''")),
      idCaseIdx: Number(dom.eval("window.__ruyiCaseIdx||-1")),
      idKeys5: String(dom.eval("window.__ruyiKeys5||''")),
      yqType: String(dom.eval("typeof (window._cf_chl_opt||{}).yQYB9")),
      optAssignments: String(dom.eval("JSON.stringify(window.__ruyiOptAssignments||[]).slice(0,1500)")),
      caseNow: String(dom.eval("window.__ruyiCaseNow===undefined?'none':String(window.__ruyiCaseNow)")),
      case2Types: String(dom.eval("window.__ruyiC2||''")),
      pjInfo: String(dom.eval("window.__ruyiPJ||''")),
      pjInfo2: String(dom.eval("window.__ruyiPJ2||''")),
      t1354Info: String(dom.eval("window.__ruyiT1354||''")),
      pgInfo: String(dom.eval("window.__ruyiPg||''")),
      pgRet: String(dom.eval("window.__ruyiPgRet||''")),
      ptBr: String(dom.eval("window.__ruyiPtBr||''")),
      yrOp: String(dom.eval("window.__ruyiYrOp||''")),
      yrOp2: String(dom.eval("window.__ruyiYrOp2||''")),
      yrRed: String(dom.eval("window.__ruyiYrRed||''")),
      vmSeqTail: String(dom.eval("(window.__ruyiVmSeq||[]).slice(-120).join(',')")),
      vmSeqLen: Number(dom.eval("(window.__ruyiVmSeq||[]).length")),
      yqW: String(dom.eval("(window.__ruyiYqW||[]).join('|')").slice(0, 4000)),
      upvCalled: String(dom.eval("JSON.stringify(window.__ruyiUpvCalled||[]).slice(0,1000)")),
      upvType: String(dom.eval("typeof window.UpvLO0")),
      yeOp: String(dom.eval("window.__ruyiYe||''")),
      c2loop: String(dom.eval("window.__ruyiC2loop||''")),
      c2m2: String(dom.eval("window.__ruyiC2m2||''")),
      c2m3: String(dom.eval("window.__ruyiC2m3||''")),
      createElementNS: Number(dom.eval("window.__ruyiCEN||0")),
      createElement: Number(dom.eval("window.__ruyiCE||0")),
      lastTag: String(dom.eval("window.__ruyiLastTag||''")),
      onError: String(dom.eval("JSON.stringify(window.__ruyiOnError||[]).slice(0,2000)")),
      evalErrors: String(dom.eval("JSON.stringify(window.__ruyiEvalErrors||[]).slice(0,2500)")),
      evtErrors: String(dom.eval("JSON.stringify(window.__ruyiEvtErrors||[]).slice(0,2000)")),
      cbErrors: String(dom.eval("JSON.stringify(window.__ruyiCbErrors||[]).slice(0,2500)")),
      hostPanel: String(dom.eval(
        "JSON.stringify({" +
        "cryptoSub:typeof crypto.subtle,textEnc:typeof TextEncoder,textDec:typeof TextDecoder," +
        "atob:typeof atob,btoa:typeof btoa,raf:typeof requestAnimationFrame," +
        "perfObs:typeof PerformanceObserver,mutObs:typeof MutationObserver," +
        "interObs:typeof IntersectionObserver,sendBeacon:typeof navigator.sendBeacon," +
        "cryptoGet:typeof crypto.getRandomValues,wk:typeof Worker,blob:typeof Blob," +
        "url:typeof URLSearchParams,dpr:typeof devicePixelRatio," +
        "shadow:typeof document.createElement('div').attachShadow})")),
      wrapperRan: Number(dom.eval("window.__wrapperRan||0")),
      xhr: String(dom.eval("JSON.stringify(window.__ruyiXhr||[]).slice(0,1500)")),
      fetch: String(dom.eval("JSON.stringify(window.__ruyiFetch||[]).slice(0,1500)")),
      title: String(dom.eval("document.title")),
      bodyLen: Number(dom.eval("document.body ? document.body.innerHTML.length : 0")),
      location: String(dom.eval("location.href")),
      cfChlOptKeys: String(dom.eval(
        "Object.keys(window._cf_chl_opt||{}).join(',')")),
      cookie: String(dom.eval("document.cookie").slice(0, 1200)),
      zhfFull: String(dom.eval("JSON.stringify(window.__ruyiZhfFull||[]).slice(0,6000)")),
      wkLog: String(dom.eval("JSON.stringify(window.__ruyiWk||[]).slice(0,4000)")),
      iwCall: String(dom.eval("window.__ruyiIwCall||''")),
      p7Arg: String(dom.eval("window.__ruyiP7Arg||''")),
      p7N: Number(dom.eval("window.__ruyiP7N||0")),
      iqProg: String(dom.eval("window.__ruyiIqProg||''")),
      iqEntry: String(dom.eval("window.__ruyiIqEntry||''")),
      iq1: String(dom.eval("window.__ruyiIq1||''")),
      fqOp: String(dom.eval("window.__ruyiFq||''")),
      fqN: Number(dom.eval("window.__ruyiFqN||0")),
    };
    print(JSON.stringify({
      ok: true,
      errors: errors,
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
