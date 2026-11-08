import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path('D:/reverse_ENV')
PROJECT = ROOT / 'workspace/psa_solve'
RUN = 'rt_20261005125421_1d84c46dcd'
INPUT = PROJECT / 'evidence/web/ruyitrace' / RUN
OUTPUT = Path(__file__).resolve().parent
DECODER = ROOT / 'mcp/ruyitrace-mcp/scripts/jscall_decode.py'
spec = importlib.util.spec_from_file_location('jscall_decoder', DECODER)
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_source(url):
    if '/api.js' in url:
        return 'https://challenges.cloudflare.com/turnstile/api.js [run-local variant]'
    if '/turnstile/f/' in url:
        return 'https://challenges.cloudflare.com/cdn-cgi/challenge-platform/turnstile/iframe [run-local variant]'
    return '[source redacted]' if url else ''


receipt = json.loads((INPUT / 'receipt.json').read_text(encoding='utf-8'))
entries = {Path(e['path']).name: e for e in receipt['entries']}
restricted = OUTPUT / 'restricted'
restricted.mkdir(parents=True, exist_ok=True)
result = {'schema': 'psa-jscall-detail-subset.v1', 'run_id': RUN,
          'scope': 'session/process/thread; never cross-run or cross-pid identity',
          'receipt_integrity': receipt['integrity'], 'artifacts': [], 'processes': []}
source_specs = {
    50068: ('000010_GET_200_challenges.cloudflare.com_cdn-cgi_challenge-platform_h_b_turnstile_f_av0_rch_7czq1_0x4AA_05c807ac_pid48180_400000016.http_packet.json',
            'eee05641ead359eed27d49331f02cab589feca0c6373b41305e03eb72e9870a7'),
    51372: ('000006_GET_200_challenges.cloudflare.com_turnstile_v0_b_d76008a69eab_api.js_c7858510_pid48180_400000013.http_packet.json',
            '76763bb46224400a11af989831d62d06629aba6f67d50cac96afae4a590adf59')}
for pid, lines in [(50068, {101, 102}), (51372, {83043, 83044})]:
    packet_name, expected_source_hash = source_specs[pid]
    packet = json.loads((INPUT / 'raw/http_packet' / packet_name).read_text(encoding='utf-8'))
    body = packet['responseBody']
    text = body['text'] if isinstance(body, dict) else body
    candidates = [text] if pid == 51372 else re.findall(r'<script\b[^>]*>([\s\S]*?)</script\s*>', text, re.I)
    matched_sources = [s for s in candidates if hashlib.sha256(s.encode('utf-8')).hexdigest() == expected_source_hash]
    assert len(matched_sources) == 1
    base = INPUT / 'raw/jscall' / ('trace_jscall_process_%s' % pid)
    bin_path = base.with_suffix('.bin')
    dict_path = base.with_suffix('.dict.jsonl')
    detail_path = base.with_suffix('.detail.bin')
    for path in [bin_path, dict_path, detail_path]:
        entry = entries[path.name]
        actual = digest(path)
        assert entry['indexed'] and entry['indexMatch']
        assert entry['sha256'] == actual and entry['bytes'] == path.stat().st_size
        result['artifacts'].append({'path': str(path.relative_to(PROJECT)),
                                  'bytes': path.stat().st_size, 'sha256': actual,
                                  'indexed': True, 'index_match': True})
    values_out = restricted / ('pid%s-values.txt' % pid)
    cmd = [sys.executable, str(DECODER), str(bin_path), '--dict', str(dict_path),
           '--detail', str(detail_path), '--values', '--output', str(values_out)]
    execution = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    (restricted / ('pid%s-decoder-stderr.txt' % pid)).write_text(execution.stderr, encoding='utf-8')
    assert execution.returncode == 0, execution.stderr
    actual_pid, records, trailing = decoder.read_records(bin_path)
    functions, stats = decoder.load_dict(dict_path)
    details = decoder.load_detail(detail_path)
    events = {r['call_id']: decoder.enrich(r, functions) for r in records}
    dom = []
    dom_path = INPUT / 'raw/domtrace' / ('trace_process_%s.ndjson' % pid)
    with dom_path.open(encoding='utf-8') as stream:
        for line_no, line in enumerate(stream, 1):
            if line_no in lines:
                dom.append((line_no, json.loads(line)))
            if line_no >= max(lines):
                break
    selected = []
    for line_no, row in dom:
        call_id = row['origin_call_id']
        event = events.get(call_id)
        item = {'dom_line': line_no, 'dom_seq': row['seq'], 'pid': row['pid'],
                'origin_call_id': call_id, 'interface': row['interface'],
                'member': row['member'], 'jscall_found': event is not None,
                'dom_this': row.get('thisObj'), 'dom_return': row.get('returnObj', row.get('valueObj')),
                'dom_args_identity': row.get('argsObj'), 'source': []}
        for frame in row.get('stack', []):
            item['source'].append({'function': frame['func'], 'url': clean_source(frame['file']),
                                   'line': frame['line'], 'column': frame['col'],
                                   'url_exact_packet_match': frame['file'] == packet['url'],
                                   'url_without_query_match': urlsplit(frame['file'])._replace(query='', fragment='') == urlsplit(packet['url'])._replace(query='', fragment='')})
        if event:
            item['jscall'] = {k: v for k, v in event.items() if k != 'url'}
            item['jscall']['url'] = clean_source(event['url'])
            parent = events.get(event['parent_call_id'])
            item['parent'] = ({k: v for k, v in parent.items() if k not in ('url',)} if parent else None)
            if parent:
                item['parent']['url'] = clean_source(parent['url'])
        safe_values = {}
        for slot, value in details.get(call_id, {}).items():
            safe = dict(value)
            if not safe['identity_only'] and safe['type'] == 'string' and safe['value'] not in ('div', 'body'):
                safe['value'] = '[redacted string]'
            safe_values[slot] = safe
        item['values'] = safe_values
        item['joins'] = []
        for slot, key in [('this', 'thisObj'), ('return', 'returnObj' if 'returnObj' in row else 'valueObj')]:
            v = safe_values.get(slot)
            obj = row.get(key, {})
            stable = bool(v and v['identity_only'] and not v['unstable_identity'] and not v['unreadable']
                          and not v['truncated'] and isinstance(v['value'], str) and v['value'].startswith('#'))
            item['joins'].append({'slot': slot, 'stable': stable,
                                  'dom_js_id_present': bool(obj.get('id')),
                                  'identity_matches': bool(stable and obj.get('id') == v['value'][1:]),
                                  'kind': 'JS id (not nativeId)'})
        for index, obj in enumerate(row.get('argsObj') or []):
            v = safe_values.get('arg%s' % index)
            stable = bool(v and v['identity_only'] and not v['unstable_identity'] and not v['unreadable']
                          and not v['truncated'] and isinstance(v['value'], str) and v['value'].startswith('#'))
            item['joins'].append({'slot': 'arg%s' % index, 'stable': stable,
                                  'dom_js_id_present': bool(obj and obj.get('id')),
                                  'identity_matches': bool(stable and obj and obj.get('id') == v['value'][1:]),
                                  'kind': 'JS id (not nativeId)'})
        selected.append(item)
    result['processes'].append({'pid': actual_pid, 'decoder_command': cmd, 'decoder_exit': execution.returncode,
                                'source_sha256': expected_source_hash, 'source_chars': len(matched_sources[0]),
                                'source_packet': packet_name,
                                'trailing_bytes': trailing, 'records': len(records),
                                'stats': {k: v for k, v in (stats or {}).items() if k not in ('script_filter',)},
                                'rows': selected})
write_json(OUTPUT / 'identity-source-subset.json', result)
print(json.dumps({'path': str(OUTPUT / 'identity-source-subset.json'),
                  'processes': [{'pid': p['pid'], 'rows': [{'call': r['origin_call_id'],
                                  'found': r['jscall_found'], 'values': r['values'], 'joins': r['joins'],
                                  'name': r.get('jscall', {}).get('name')}
                                 for r in p['rows']]} for p in result['processes']]}, ensure_ascii=True))
