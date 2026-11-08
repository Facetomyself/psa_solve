"""One-shot diagnostics wrapper. Default preflight is strictly offline.

Fresh materials preserve the historical urllib/UA135 -> Gecko handoff.
This is a logical challenge/cookie session, NOT a single TLS connection.
Raw inputs/output are only written below the project's gitignored evidence/.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urljoin, urlparse
from urllib.request import build_opener, Request, HTTPErrorProcessor, HTTPCookieProcessor
import uuid

ROOT = Path(r"D:\reverse_ENV\workspace\psa_solve")
REPO = Path(r"D:\reverse_ENV")
PY = REPO / ".venv/Scripts/python.exe"
NODE = REPO / "tools/node/node.exe"
CASE = REPO / "skill/web-reverse/scripts/web_case.py"
CLI = REPO / "mcp/ruyidom-mcp/dist/cli.js"
BASE = ROOT / "diagnostics/clean-baseline-20260930"
RESTRICTED = ROOT / "evidence/web/diagnostic-cleanup-baseline/restricted"
STATE = ROOT / "agent-notes/20260930-clean-baseline-state.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding="utf-8", newline="\n")


def state(**delta):
    value = read(STATE)
    value.update(delta)
    value['updatedAt'] = now()
    write(STATE, value)


def preflight():
    manifest = read(BASE / "manifest.json")
    assert digest(ROOT / "diagnostics/ruyidom_bridge.js") == manifest['originalSha256']
    assert digest(BASE / "ruyidom_bridge.original.js") == manifest['originalSha256']
    assert digest(BASE / "ruyidom_bridge.clean.js") == manifest['cleanSha256']
    assert digest(ROOT / "contracts/auto-decision-facts.json") == manifest['factsSha256']
    result = subprocess.run([str(NODE), str(CLI), 'status'], capture_output=True, encoding='utf-8')
    assert result.returncode == 0
    runtime = json.loads(result.stdout)
    assert runtime['ok'] is True and runtime['runtime']['status'] == 'healthy'
    write(BASE / 'runtime-status.json', runtime)
    proxy_names = [k for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','CF_PROXY','CF_PRE_PROXY') if os.environ.get(k)]
    return {'hashesValid': True, 'runtimeHealthy': True, 'proxyEnvironmentNames': proxy_names,
            'handoff': 'urllib-UA135-cookie-material-to-Gecko; not same TLS',
            'interaction': 'existing 30000 ms / existing click and pointer path unchanged'}


class Keep(HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response


def parse_orchestrate(html, page_url):
    match = re.search(r"(/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1[^\"'<>\s]*)", html)
    if not match:
        raise ValueError('fresh page has no expected orchestrate URL; no fallback allowed')
    result = urljoin(page_url, match.group(1))
    assert urlparse(result).netloc == urlparse(page_url).netloc
    return result


def fetch_fresh():
    preflight()
    # Only the approved target URL is reused; no cookies/body/script from old input.
    target = read(ROOT / 'diagnostics/bridge-input.json')['challengeUrl']
    session = uuid.uuid4().hex
    out = RESTRICTED / session
    out.mkdir(parents=True, exist_ok=False)
    jar = http.cookiejar.CookieJar()
    opener = build_opener(Keep(), HTTPCookieProcessor(jar))
    cookie_lines, events = [], []
    state(status='fresh-material-fetch-running', sessionId=session,
          rawDirectory=str(out), wrapperPid=os.getpid(), enginePid=None, terminal='running',
          onlineExecuted=False, materialNetworkStartedAt=now())
    def get(url, role):
        request = Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
        with opener.open(request, timeout=30) as response:
            body = response.read()
            cookies = response.headers.get_all('Set-Cookie') or []
            cookie_lines.extend(cookies)
            events.append({'role': role, 'status': response.status, 'bytes': len(body),
                           'at': now(), 'urlSha256': hashlib.sha256(url.encode('utf-8')).hexdigest()})
            return response.status, body
    try:
        status, html = get(target, 'challenge')
        assert status == 403 and len(html) > 100, 'expected fresh 403 challenge'
        orch_url = parse_orchestrate(html.decode('utf-8', 'strict'), target)
        status, script = get(orch_url, 'orchestrate')
        assert status == 200 and len(script) > 1000, 'expected fresh orchestrate body'
        assert cookie_lines and list(jar), 'fresh cookie jar is empty'
        (out / 'challenge.html').write_bytes(html)
        (out / 'orchestrate.js').write_bytes(script)
        (out / 'cookies.txt').write_text('\n'.join(cookie_lines) + '\n', encoding='utf-8', newline='\n')
        input_path = out / 'fresh-input.json'
        write(input_path, {'challengeHtmlPath': str(out/'challenge.html'), 'orchestrateJsPath': str(out/'orchestrate.js'),
                           'challengeUrl': target, 'pumpMs': 30000, 'patchHistory': True, 'liveNetwork': True,
                           'cookieFile': str(out/'cookies.txt'), 'tracePath': str(out/'bridge-live.jsonl')})
        captured = now()
        artifacts = [{'role': role, 'path': str(out/name), 'sha256': digest(out/name), 'bytes': (out/name).stat().st_size}
                     for role, name in [('challenge','challenge.html'),('orchestrate','orchestrate.js'),('cookies','cookies.txt'),('input','fresh-input.json')]]
        receipt_path = out/'source-receipt.json'
        write(receipt_path, {'schema':'psa-fresh-material-receipt.v1','sessionId':session,'capturedAt':captured,
                            'network':'live','sameSession':True,'foreignResponseReplay':False,'artifacts':artifacts,
                            'transport':'urllib UA135 -> Gecko cookie/material handoff; NOT same TLS',
                            'events':events,'limitations':['same logical challenge session, not same engine/TLS',
                            'CookieJar and fail-closed fresh directory differ from historical fetch; not runner-only single-variable experiment'],
                            'runtimeStatusSha256':digest(BASE/'runtime-status.json')})
        provenance = out/'provenance.json'
        write(provenance, {'schema':'diagnostic-cleanup-provenance.v1','sessionId':session,'capturedAt':captured,
                          'network':'live','sameSession':True,'foreignResponseReplay':False,
                          'inputPath':str(input_path),'inputSha256':digest(input_path),
                          'sourceReceiptPath':str(receipt_path),'sourceReceiptSha256':digest(receipt_path)})
        state(status='fresh-material-ready',freshInputPrepared=True,provenancePath=str(provenance),
              wrapperPid=None,terminal='completed',materialNetworkEndedAt=now())
        return provenance
    except Exception as error:
        write(out/'fetch-failure.json', {'errorType':type(error).__name__, 'events':events, 'endedAt':now()})
        state(status='fresh-material-failed',wrapperPid=None,terminal='failed',freshInputPrepared=False)
        raise


def classify(output, exit_code):
    run = output.get('run') or {}
    summary = run.get('result') or {}
    if not isinstance(summary, dict):
        summary = {}
    probe = summary.get('probe') or {}
    healthy = bool(exit_code == 0 and output.get('ok') is True and run.get('exitCode') == 0
                   and not run.get('timedOut') and summary.get('ok') is True
                   and isinstance(probe, dict) and 'evalError' not in probe)
    observed = bool(summary.get('ok') is True and 'evalError' not in probe)
    forms = probe.get('forms') if observed else None
    submits = probe.get('submits') if observed else None
    boundaries=[]
    for row in summary.get('respLog',[]):
        path=str(row.get('path',''))
        role='cert-document' if '/cert/' in path else 'challenge-fo' if '/fo/' in path else 'other'
        host=row.get('hostClass')
        boundary={'order':len(boundaries)+1,'role':role,
                  'realm':'page-host' if host=='page' else 'challenge-host' if host=='cf' else 'unresolved',
                  'method':row.get('method') if row.get('method') in ['GET','POST','OPTIONS'] else 'other',
                  'status':row.get('status'),'requestBytes':row.get('reqLen'),'responseHeaderBytes':row.get('respLen'),
                  'channelBytes':row.get('chanLen'),'protocol':row.get('proto'),
                  'documentDestination':row.get('secDest')=='document'}
        boundaries.append(boundary)
    cert_post=any(r['role']=='cert-document' and r['method']=='POST' for r in boundaries)
    # Existing summary does not prove business response content. Never invent acceptance.
    return {'harnessHealthy':healthy, 'businessAccepted':False,
            'businessAcceptanceStatus':'not-proven', 'forms':forms,'submits':submits,
            'topPageFoOpenCount':probe.get('foSeen') if observed else None,
            'widgetComplete':'complete' in str(probe.get('msgHit','')).split(','),
            'worker':{'status':'probe-disabled','value':None},'subtle':{'status':'probe-disabled','value':None},
            'blob':{'status':'probe-disabled','value':None},
            'iframeWorker':{'status':'not-observed','value':None},
            'clearanceCookieNamed':'cf_clearance' in summary.get('cookieNames',[]),
            'certPostObserved':cert_post,'requestBoundaryTable':boundaries,
            'limitations':['no new independent business-content readback','older observation hooks retained']}


def run_once(provenance):
    preflight()
    provenance = Path(provenance).resolve()
    assert provenance.is_relative_to(RESTRICTED)
    p = read(provenance)
    out = provenance.parent
    claim_cmd = [str(PY),str(CASE),'diagnostic-cleanup-baseline','--project',str(ROOT),
                 '--phase','claim','--opt-in','--provenance',str(provenance)]
    claim_result = subprocess.run(claim_cmd,capture_output=True,encoding='utf-8')
    (out/'claim-stdout.json').write_text(claim_result.stdout,encoding='utf-8',newline='\n')
    (out/'claim-stderr.txt').write_text(claim_result.stderr,encoding='utf-8',newline='\n')
    assert claim_result.returncode == 0, 'claim rejected; no engine spawned'
    claim = json.loads(claim_result.stdout)
    # Fail closed until a real, explicitly authorized argv is returned.
    argv = claim['argv']
    assert '--allow-network' in argv and str(BASE/'ruyidom_bridge.clean.js') in argv
    assert str(Path(p['inputPath'])) in argv
    stdout_path, stderr_path = out/'engine-stdout.json',out/'engine-stderr.txt'
    started, pid, code, spawned = None,None,None,False
    launch_error=None
    env = dict(os.environ)
    env['MOZ_FORCE_DISABLE_E10S']='1'
    env['MOZ_FORCE_DISABLE_FISSION']='1'
    state(status='cleanup-baseline-claimed-not-started',claimId=claim['claimId'],
          wrapperPid=os.getpid(),cliPid=None,enginePid=None,terminal='reserved',onlineExecuted=False)
    try:
        with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
            for relative, expected in claim['protectedHashes'].items():
                assert digest(ROOT/relative)==expected
            for relative, expected in claim['runtimeHashes'].items():
                assert digest(REPO/relative)==expected
            assert digest(ROOT/'diagnostics/ruyidom_bridge.js')==claim['runnerSha256']
            assert digest(BASE/'ruyidom_bridge.clean.js')==claim['candidateSha256']
            assert digest(provenance)==claim['provenanceSha256']
            assert digest(p['inputPath'])==p['inputSha256']
            assert digest(p['sourceReceiptPath'])==p['sourceReceiptSha256']
            for artifact in read(p['sourceReceiptPath'])['artifacts']:
                assert digest(artifact['path'])==artifact['sha256']
            for key,value in claim['environment'].items():
                assert env.get(key)==value
            binding_path = ROOT / claim['claimBindingPath']
            binding_record = read(binding_path)
            assert binding_record['bindingSha256'] == claim['claimBindingSha256']
            assert binding_record['binding']['claimId'] == claim['claimId']
            assert datetime.now(timezone.utc) <= datetime.fromisoformat(claim['executeBefore'].replace('Z','+00:00'))
            child=subprocess.Popen(argv,stdout=stdout,stderr=stderr,env=env)
            started=now()
            pid,spawned=child.pid,True
            state(status='cleanup-baseline-running',sessionId=p['sessionId'],wrapperPid=os.getpid(),
                  cliPid=pid,enginePid=None,terminal='running',onlineExecuted=True,startedAt=started,
                  claimId=claim['claimId'],provenancePath=str(provenance))
            code=child.wait()  # CLI enforces its bounded process-tree timeout.
    except Exception as error:
        launch_error=type(error).__name__
        if not spawned:
            started=None
    finally:
        receipt={'schema':'diagnostic-cleanup-execution.v1','claimId':claim['claimId'],
                 'claimBindingSha256':claim['claimBindingSha256'],
                 'spawned':spawned,'pid':pid,'startedAt':started,'endedAt':now(),'exitCode':code,'argv':argv,
                 'stdoutPath':str(stdout_path),'stdoutSha256':digest(stdout_path),
                 'stderrPath':str(stderr_path),'stderrSha256':digest(stderr_path)}
        receipt_path=out/'execution-receipt.json'
        write(receipt_path,receipt)
        state(status='cleanup-baseline-exited',wrapperPid=None,cliPid=pid,terminal='exited',exitCode=code,endedAt=receipt['endedAt'])
    try:
        output=read(stdout_path)
    except Exception:
        output={}
    result=classify(output,code)
    write(out/'boundary-summary.json',result)
    recorded=subprocess.run([str(PY),str(CASE),'diagnostic-cleanup-baseline','--project',str(ROOT),
                             '--phase','record','--opt-in','--execution-receipt',str(receipt_path)],
                            capture_output=True,encoding='utf-8')
    (out/'record-stdout.json').write_text(recorded.stdout,encoding='utf-8',newline='\n')
    (out/'record-stderr.txt').write_text(recorded.stderr,encoding='utf-8',newline='\n')
    state(status='cleanup-baseline-recorded' if recorded.returncode==0 else 'cleanup-baseline-record-failed',
          boundarySummaryPath=str(out/'boundary-summary.json'),harnessHealthy=result['harnessHealthy'],
          businessAccepted=False,instrumentationExecuted=False,launchErrorType=launch_error)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=['preflight','fetch','run'])
    parser.add_argument('--provenance',type=Path)
    args=parser.parse_args()
    if args.phase=='preflight':
        print(json.dumps(preflight()))
    elif args.phase=='fetch':
        print(json.dumps({'provenancePath':str(fetch_fresh())}))
    else:
        assert args.provenance, 'provenance required'
        print(json.dumps(run_once(args.provenance)))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        # Never echo an exception message containing a request URL/credential.
        print(json.dumps({'ok':False,'errorType':type(error).__name__}))
        sys.exit(1)
