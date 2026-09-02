#!/usr/bin/env python3
"""
RC LARGECARS - one-click web flasher for the ESP32 truck sound board.

Run from this folder:    python flasher_server.py
Or double-click:         Launch_Flasher.bat
Then open:               http://localhost:8765
"""
import json
import os
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE     = os.path.dirname(os.path.abspath(__file__))
FW_DIR   = os.path.join(HERE, 'firmware')
PORT     = 8765

# --- esptool resolution -----------------------------------------------------
def _find_esptool():
    """Return a list-form command that runs esptool."""
    # 1. esptool installed under the user's Platformio Python
    pio_py = os.path.expandvars(r'%USERPROFILE%\.platformio\penv\Scripts\python.exe')
    if os.path.isfile(pio_py):
        return [pio_py, '-m', 'esptool']
    # 2. plain python -m esptool
    try:
        subprocess.check_call([sys.executable, '-m', 'esptool', 'version'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return [sys.executable, '-m', 'esptool']
    except Exception:
        pass
    # 3. esptool.py on PATH
    return ['esptool.py']

ESPTOOL_CMD = _find_esptool()

# --- COM port enumeration ---------------------------------------------------
def list_com_ports():
    ports = []
    if sys.platform.startswith('win'):
        try:
            out = subprocess.check_output(
                ['powershell', '-NoProfile', '-Command',
                 "Get-CimInstance Win32_PnPEntity | "
                 "Where-Object { $_.Name -match 'COM\\d+' -and "
                 "$_.Name -notmatch 'Bluetooth' } | "
                 "ForEach-Object { $_.Name }"],
                text=True, stderr=subprocess.STDOUT, timeout=10)
            for line in out.splitlines():
                m = re.search(r'(COM\d+)', line)
                if m:
                    ports.append({'port': m.group(1), 'desc': line.strip()})
        except Exception:
            pass
    else:
        import glob
        for p in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
            ports.append({'port': p, 'desc': p})
    seen, dedup = set(), []
    for p in ports:
        if p['port'] in seen: continue
        seen.add(p['port']); dedup.append(p)
    return dedup

# --- manifest ---------------------------------------------------------------
def read_manifest():
    p = os.path.join(FW_DIR, 'manifest.json')
    if not os.path.isfile(p):
        return None
    with open(p, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

# --- flash job (background thread) ------------------------------------------
class FlashJob:
    def __init__(self):
        self.lock     = threading.Lock()
        self.lines    = []
        self.running  = False
        self.exit     = None

    def append(self, s):
        with self.lock:
            self.lines.append(s)
            if len(self.lines) > 4000:
                self.lines = self.lines[-3000:]

    def snapshot(self, since):
        with self.lock:
            return self.lines[since:], len(self.lines), self.running, self.exit

    def start(self, port, variant_id):
        with self.lock:
            if self.running:
                return False, 'already running'
            self.lines = []
            self.running = True
            self.exit = None
        t = threading.Thread(target=self._run, args=(port, variant_id), daemon=True)
        t.start()
        return True, 'started'

    def _run(self, port, variant_id):
        try:
            man = read_manifest()
            variant = next((v for v in man['variants'] if v['id'] == variant_id), None)
            if not variant:
                self.append(f'ERROR: unknown variant {variant_id}')
                self.exit = 1
                return
            boot = os.path.join(FW_DIR, man['bootloader'])
            part = os.path.join(FW_DIR, man['partitions'])
            app  = os.path.join(FW_DIR, variant['file'])
            for pth in (boot, part, app):
                if not os.path.isfile(pth):
                    self.append(f'ERROR: missing {pth}')
                    self.exit = 1
                    return

            cmd = ESPTOOL_CMD + [
                '--chip', 'esp32',
                '--port', port,
                '--baud', '921600',
                'write_flash', '-z',
                '--flash_mode', 'dio',
                '--flash_freq', '40m',
                '--flash_size', '4MB',
                man['bootloader_offset'], boot,
                man['partitions_offset'], part,
                man['app_offset'],        app,
            ]
            self.append('> ' + ' '.join(cmd))
            # Suppress child console window when launched from pythonw / VBS
            popen_kw = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
            if sys.platform == 'win32':
                popen_kw['creationflags'] = 0x08000000  # CREATE_NO_WINDOW
            proc = subprocess.Popen(cmd, **popen_kw)
            for line in proc.stdout:
                self.append(line.rstrip())
            proc.wait()
            self.exit = proc.returncode
            self.append(f'\n[exit code {proc.returncode}]')
        except Exception as e:
            self.append(f'EXCEPTION: {e}')
            self.exit = 1
        finally:
            self.running = False

JOB = FlashJob()

# --- HTML -------------------------------------------------------------------
INDEX_HTML = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>RC LARGECARS - Flasher</title>
<style>
  :root{--bg:#000000;--card:#0a0a0a;--bord:#1a1a1a;--text:#e0e0e0;--mute:#6a6a6a;
        --acc:#39ff14;--acc2:#ff3333;--ok:#39ff14;--amber:#ffaa00}
  *{box-sizing:border-box}
  body{margin:0;font:14px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;
       background:var(--bg);color:var(--text);min-height:100vh}
  header{padding:18px 28px;border-bottom:1px solid #39ff1440;
         background:linear-gradient(180deg,#0a0a0a 0%,#000000 100%);
         display:flex;align-items:center;gap:14px}
  header h1{margin:0;font-size:22px;letter-spacing:3px;font-weight:800;
            color:var(--acc);text-shadow:0 0 8px #39ff1488,0 0 20px #39ff1433,0 0 40px #39ff1422}
  header .sub{color:var(--mute);font-size:12px}
  main{max-width:880px;margin:24px auto;padding:0 24px}
  .card{background:linear-gradient(135deg,#0d120a 0%,#0a0a0a 100%);
        border:1px solid #39ff1440;border-radius:14px;
        padding:20px;margin-bottom:18px;position:relative;overflow:hidden}
  .card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
                background:linear-gradient(90deg,#39ff14,#1fff00)}
  .row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
  .row > *{flex:0 0 auto}
  label{display:block;color:var(--acc);font-size:11px;text-transform:uppercase;
        font-weight:600;letter-spacing:.8px;margin-bottom:6px}
  select,button{font:inherit;background:#0d0d0d;color:var(--text);
                border:1px solid #1a1a1a;border-radius:6px;padding:8px 12px}
  select{min-width:180px}
  select:focus{outline:none;border-color:var(--acc);box-shadow:0 0 0 1px var(--acc)}
  button{cursor:pointer;background:var(--acc);color:#000;border:0;font-weight:700;
         text-transform:uppercase;letter-spacing:1px;
         box-shadow:0 0 12px #39ff1466}
  button:hover:not(:disabled){background:#5fff3a;box-shadow:0 0 18px #39ff1499}
  button:disabled{opacity:.4;cursor:not-allowed;box-shadow:none}
  button.ghost{background:transparent;color:var(--text);border:1px solid #1a1a1a;
               font-weight:400;text-transform:none;letter-spacing:0;box-shadow:none}
  button.ghost:hover:not(:disabled){border-color:var(--acc);color:var(--acc);box-shadow:none;background:transparent}
  .opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-top:6px}
  .opt{border:1px solid #1a1a1a;border-radius:10px;padding:14px;cursor:pointer;
       text-align:center;background:#0d0d0d;transition:.15s}
  .opt:hover{border-color:#39ff1460}
  .opt.on{border-color:var(--acc);background:#0d1f08;
          box-shadow:0 0 0 1px var(--acc) inset,0 0 14px #39ff1444}
  .opt h3{margin:0 0 4px 0;font-size:15px;color:var(--text)}
  .opt.on h3{color:var(--acc)}
  .opt p{margin:0;color:var(--mute);font-size:11px}
  pre{background:#000;border:1px solid #1a1a1a;border-radius:6px;
      padding:14px;color:var(--acc);font-family:Consolas,Menlo,monospace;font-size:12px;
      max-height:380px;overflow:auto;white-space:pre-wrap;margin:0;
      text-shadow:0 0 4px #39ff1444}
  .pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:11px;
        background:#0d0d0d;color:var(--mute);border:1px solid #1a1a1a;
        text-transform:uppercase;letter-spacing:.5px;font-weight:600}
  .pill.ok{background:#0d1f08;color:var(--ok);border-color:#39ff1460;
           box-shadow:0 0 8px #39ff1444}
  .pill.err{background:#1f0808;color:var(--acc2);border-color:#ff333360}
  .warn{background:#1f1808;border:1px solid #ffaa0060;color:var(--amber);
        padding:10px 12px;border-radius:8px;font-size:12px;margin-bottom:14px}
</style>
</head><body>
<header>
  <h1>RC LARGECARS</h1>
  <span class="sub">pick a sound + protocol, plug in the ESP32, hit Flash</span>
  <span style="flex:1"></span>
</header>
<main>

<div class="card">
  <label>1.  Engine sound</label>
  <div id="packs" class="opts"></div>
</div>

<div class="card">
  <label>2.  RC protocol</label>
  <div id="protos" class="opts"></div>
</div>

<div class="card">
  <label>3.  Serial port</label>
  <div class="row">
    <select id="port"></select>
    <button class="ghost" onclick="refreshPorts()">Refresh</button>
    <span id="portinfo" class="pill">-</span>
  </div>
  <div class="warn" style="margin-top:12px">
    Plug the ESP32 in via USB with the truck's battery <b>DISCONNECTED</b>.
    Hold <b>BOOT</b> on the ESP32 if the flash fails the first time.
  </div>
</div>

<div class="card">
  <div class="row">
    <button id="flashbtn" onclick="flash()">Flash firmware</button>
    <span id="status" class="pill">idle</span>
    <span id="size" class="pill">-</span>
  </div>
</div>

<div class="card">
  <label>Output</label>
  <pre id="log">(idle)</pre>
</div>

</main>
<script>
let manifest = null;
let pack  = null;
let proto = null;
let logCount = 0;

async function loadManifest(){
  const r = await fetch('/api/manifest'); manifest = await r.json();
  const packs  = [...new Set(manifest.variants.map(v=>v.pack))];
  const protos = [...new Set(manifest.variants.map(v=>v.proto))];
  const PACK_LBL = {c15:{title:'Caterpillar C15',sub:'six-pack inline turbo'},
                    '8v92':{title:'Detroit 8V92',sub:'two-stroke V8 screamer'},
                    n14:{title:'Cummins N14',sub:'14L big-cam diesel'},
                    c15sim:{title:'C15 Simulated',sub:'synth engine + 10-spd trans (iBUS)'}};
  const PROTO_LBL= {pwm:{title:'PWM',sub:'classic 5-channel pulse-width'},
                    ibus:{title:'iBUS',sub:'FlySky single-wire serial'},
                    sbus:{title:'SBUS',sub:'Futaba / FrSky inverted serial'}};
  const pe = document.getElementById('packs'); pe.innerHTML='';
  packs.forEach(p=>{
    const lbl = PACK_LBL[p] || {title:p,sub:''};
    const d = document.createElement('div');
    d.className='opt'; d.dataset.id=p;
    d.innerHTML = `<h3>${lbl.title}</h3><p>${lbl.sub}</p>`;
    d.onclick = ()=>{pack=p; render();};
    pe.appendChild(d);
  });
  const re = document.getElementById('protos'); re.innerHTML='';
  protos.forEach(p=>{
    const lbl = PROTO_LBL[p] || {title:p,sub:''};
    const d = document.createElement('div');
    d.className='opt'; d.dataset.id=p;
    d.innerHTML = `<h3>${lbl.title}</h3><p>${lbl.sub}</p>`;
    d.onclick = ()=>{proto=p; render();};
    re.appendChild(d);
  });
  pack = packs[0]; proto = protos.includes('ibus')?'ibus':protos[0];
  render();
}

function currentVariant(){
  return manifest.variants.find(v=>v.pack===pack && v.proto===proto);
}

function render(){
  document.querySelectorAll('#packs .opt').forEach(o=>o.classList.toggle('on',o.dataset.id===pack));
  document.querySelectorAll('#protos .opt').forEach(o=>o.classList.toggle('on',o.dataset.id===proto));
  const v = currentVariant();
  document.getElementById('size').textContent = v ? `${v.id}   ${(v.size/1024/1024).toFixed(2)} MB` : '-';
}

async function refreshPorts(){
  const r = await fetch('/api/ports'); const ports = await r.json();
  const sel = document.getElementById('port');
  const cur = sel.value;
  sel.innerHTML='';
  if (!ports.length){
    const o = document.createElement('option'); o.textContent='(no ports detected)'; o.value=''; sel.appendChild(o);
    document.getElementById('portinfo').textContent = 'plug in the ESP32 and hit Refresh';
    document.getElementById('portinfo').className='pill err';
  } else {
    ports.forEach(p=>{
      const o = document.createElement('option'); o.value=p.port; o.textContent=p.desc; sel.appendChild(o);
    });
    if (ports.find(p=>p.port===cur)) sel.value=cur;
    document.getElementById('portinfo').textContent = `${ports.length} port${ports.length>1?'s':''} found`;
    document.getElementById('portinfo').className='pill ok';
  }
}

async function flash(){
  const port = document.getElementById('port').value;
  if (!port){ alert('Pick a serial port first.'); return; }
  const v = currentVariant();
  if (!v){ alert('Pick a sound + protocol.'); return; }
  document.getElementById('flashbtn').disabled = true;
  document.getElementById('log').textContent = '';
  logCount = 0;
  const r = await fetch('/api/flash',{method:'POST',headers:{'Content-Type':'application/json'},
                       body:JSON.stringify({port, variant: v.id})});
  if (!r.ok){ alert('Failed to start: '+(await r.text())); document.getElementById('flashbtn').disabled=false; return; }
  poll();
}

async function poll(){
  const r = await fetch('/api/status?since='+logCount);
  const j = await r.json();
  if (j.lines.length){
    const log = document.getElementById('log');
    log.textContent += j.lines.join('\n')+'\n';
    log.scrollTop = log.scrollHeight;
    logCount = j.total;
  }
  const st = document.getElementById('status');
  if (j.running){
    st.textContent = 'flashing...'; st.className='pill';
    setTimeout(poll, 400);
  } else if (j.exit === 0){
    st.textContent = 'done'; st.className='pill ok';
    document.getElementById('flashbtn').disabled = false;
  } else if (j.exit !== null){
    st.textContent = 'failed (exit '+j.exit+')'; st.className='pill err';
    document.getElementById('flashbtn').disabled = false;
  } else {
    st.textContent = 'idle'; st.className='pill';
    document.getElementById('flashbtn').disabled = false;
  }
}

loadManifest();
refreshPorts();
</script>
</body></html>
"""


# --- HTTP -------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def _send(self, code, ctype, body):
        if isinstance(body, str): body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            self._send(200, 'text/html; charset=utf-8', INDEX_HTML); return
        if self.path == '/api/ports':
            self._send(200, 'application/json', json.dumps(list_com_ports())); return
        if self.path == '/api/manifest':
            man = read_manifest()
            if not man: self._send(500,'text/plain','manifest.json missing - run build_all_variants.ps1'); return
            self._send(200,'application/json', json.dumps(man)); return
        if self.path.startswith('/api/status'):
            since = 0
            m = re.search(r'since=(\d+)', self.path)
            if m: since = int(m.group(1))
            lines, total, running, exit_code = JOB.snapshot(since)
            self._send(200,'application/json', json.dumps({
                'lines': lines, 'total': total,
                'running': running, 'exit': exit_code
            })); return
        self._send(404, 'text/plain', 'not found')

    def do_POST(self):
        if self.path == '/api/flash':
            length = int(self.headers.get('Content-Length','0'))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            port    = data.get('port','').strip()
            variant = data.get('variant','').strip()
            if not port or not variant:
                self._send(400,'text/plain','need port + variant'); return
            ok, msg = JOB.start(port, variant)
            self._send(200 if ok else 409, 'application/json', json.dumps({'ok':ok,'msg':msg})); return
        self._send(404, 'text/plain', 'not found')

def main():
    if not os.path.isfile(os.path.join(FW_DIR, 'manifest.json')):
        print('ERROR: firmware/manifest.json not found.')
        print('Run  tools\\build_all_variants.ps1  first.')
        sys.exit(1)
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    url = f'http://localhost:{PORT}'
    print(f"RC LARGECARS  ->  {url}")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\nbye')

if __name__ == '__main__':
    main()
