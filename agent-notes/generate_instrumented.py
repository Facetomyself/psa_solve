from pathlib import Path
import hashlib

base = Path('workspace/psa_solve/diagnostics/clean-baseline-20260930/ruyidom_bridge.clean.js')
out = Path('workspace/psa_solve/diagnostics/instrumentation-20260930')
out.mkdir(parents=True, exist_ok=True)
text = base.read_text(encoding='utf-8')
needle = '    if (probe && probe.path) probe.path = pathTemplate(probe.path);'
assert needle in text
insert = r'''    // Reviewed diagnostic-instrumentation capability probe: read-only realm/API
    // checks. It never wraps a host API, changes the dual-condition patch, or
    // creates a network/worker surface. Results are capability facts only.
    var capabilityProbe = {};
    try {
      capabilityProbe = JSON.parse(String(dom.eval(
        "(function(){var out={version:'capability-probe-v1',topPage:{},iframe:{},blob:{}};" +
        "try{out.topPage.windowSelf=(window===self);out.topPage.windowTop=(window===top);out.topPage.documentSame=(document===window.document);out.topPage.topAccessible=!!top.location;}catch(e){out.topPage.error='unavailable';}" +
        "try{var fs=document.getElementsByTagName('iframe'),same=0,cross=0,wins=0,docs=0;for(var i=0;i<fs.length;i++){var f=fs[i];try{if(f.contentWindow){wins++;var d=f.contentDocument;if(d){docs++;same++;}}}catch(e){cross++;}}out.iframe={count:fs.length,contentWindowReadable:wins,contentDocumentReadable:docs,sameOriginReadable:same,crossOriginBlocked:cross};}catch(eI){out.iframe={error:'unavailable'};}" +
        "try{out.blob.BlobCtor=(typeof Blob==='function');out.blob.createObjectURL=(typeof URL!=='undefined'&&typeof URL.createObjectURL==='function');out.blob.revokeObjectURL=(typeof URL!=='undefined'&&typeof URL.revokeObjectURL==='function');if(out.blob.BlobCtor&&out.blob.createObjectURL){var b=new Blob(['capability-probe-v1'],{type:'text/plain'}),u=URL.createObjectURL(b);out.blob.urlCreated=(typeof u==='string'&&u.indexOf('blob:')===0);if(out.blob.revokeObjectURL)URL.revokeObjectURL(u);out.blob.urlRevoked=!!out.blob.revokeObjectURL;}}catch(eB){out.blob.error='unavailable';}return JSON.stringify(out);})()"
      )));
    } catch (eCapability) {
      capabilityProbe = {version:'capability-probe-v1',error:'unavailable'};
    }
    probe.capabilityProbe = capabilityProbe;
'''
text = text.replace(needle, insert + needle, 1)
path = out / 'ruyidom_bridge.instrumented.js'
path.write_text(text, encoding='utf-8', newline='\n')
print('clean', hashlib.sha256(base.read_bytes()).hexdigest())
print('instrumented', hashlib.sha256(path.read_bytes()).hexdigest())
