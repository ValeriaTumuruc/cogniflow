"""Cogniflow local research page. Python 3.10+, standard library only."""
import argparse, csv, hashlib, json, os, re, secrets, sqlite3, threading, time
from collections import defaultdict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('COGNIFLOW_DB', str(ROOT / 'data' / 'research.sqlite3')))
STATIC = {'/assets/Barlow-Bold.ttf':('assets/Barlow-Bold.ttf','font/ttf'), '/assets/Barlow-Regular.ttf':('assets/Barlow-Regular.ttf','font/ttf'), '/assets/Barlow-OFL.txt':('assets/Barlow-OFL.txt','text/plain'), '/config.js':('config.js','text/javascript'), '/':('index.html','text/html'), '/index.html':('index.html','text/html'), '/privacy.html':('privacy.html','text/html'), '/styles.css':('styles.css','text/css'), '/app.js':('app.js','text/javascript'), '/mark.svg':('mark.svg','image/svg+xml')}
def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.executescript('''CREATE TABLE IF NOT EXISTS signups(email TEXT PRIMARY KEY, programme TEXT, created REAL, channel TEXT, visitor TEXT, withdrawal TEXT UNIQUE, consent_version TEXT);
    CREATE TABLE IF NOT EXISTS events(visitor TEXT,event TEXT,day TEXT,created REAL,channel TEXT,PRIMARY KEY(visitor,event,day));''')
    c.execute('DELETE FROM signups WHERE created < ?', (time.time()-90*86400,))
    c.execute('DELETE FROM events WHERE created < ?', (time.time()-30*86400,))
    c.commit(); return c
def channel(value): return re.sub(r'[^a-zA-Z0-9_-]', '', str(value or 'direct'))[:60] or 'direct'
def visitor(value): return value if isinstance(value,str) and re.fullmatch(r'[a-fA-F0-9-]{36}',value) else None
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
rate = defaultdict(list); lock = threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def headers_common(self):
        self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
        api_origin = ''
        config = re.search(r"apiBaseUrl:\s*['\"]([^'\"]+)['\"]", (ROOT/'config.js').read_text(encoding='utf-8'))
        if config:
            api = urlsplit(config.group(1))
            if api.scheme == 'https' and re.fullmatch(r'[a-zA-Z0-9.:-]+', api.netloc): api_origin = ' https://' + api.netloc
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'" + api_origin + "; frame-src https://embed.figma.com https://www.figma.com; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        self.send_header('Cache-Control','no-store')
    def reply(self,code,data):
        payload=json.dumps(data).encode();self.send_response(code);self.headers_common();self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    def do_GET(self):
        entry=STATIC.get(urlsplit(self.path).path)
        if not entry: return self.reply(404,{'error':'Not found'})
        payload=(ROOT/entry[0]).read_bytes();self.send_response(200);self.headers_common();self.send_header('Content-Type',entry[1]+'; charset=utf-8');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    def do_POST(self):
        if self.path not in ['/api/signup','/api/event','/api/withdraw']:return self.reply(404,{'error':'Not found'})
        origin=self.headers.get('Origin')
        if origin and urlsplit(origin).netloc != self.headers.get('Host'):return self.reply(403,{'error':'Use the form on the Cogniflow website.'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.reply(415,{'error':'JSON required'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=4096:raise ValueError()
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict):raise ValueError()
        except (ValueError,TypeError):return self.reply(400,{'error':'Invalid request'})
        now=time.time()
        with lock:
            key=(self.client_address[0],self.path);rate[key]=[t for t in rate[key] if t>now-60]
            if len(rate[key])>=30:return self.reply(429,{'error':'Too many attempts. Please wait a minute.'})
            rate[key].append(now)
            if len(rate)>1000:
                for k in list(rate):
                    if not rate[k] or rate[k][-1]<now-60:del rate[k]
        if self.path=='/api/event':
            vid=visitor(body.get('visitor')); event=body.get('event')
            if not vid or event not in ['visit','cta'] or body.get('eligible') is not True:return self.reply(400,{'error':'Invalid measurement'})
            with connect() as c:c.execute('INSERT OR IGNORE INTO events VALUES(?,?,?,?,?)',(vid,event,datetime.now(timezone.utc).date().isoformat(),now,channel(body.get('channel'))))
            return self.reply(200,{'ok':True})
        if self.path=='/api/withdraw':
            token=body.get('token','')
            if not isinstance(token,str) or not 30<=len(token)<=100:return self.reply(400,{'error':'Please enter your complete withdrawal code.'})
            with connect() as c:c.execute('DELETE FROM signups WHERE withdrawal=?',(digest(token),))
            return self.reply(200,{'ok':True})
        email=body.get('email','');programme=body.get('programme','')
        if body.get('website'):return self.reply(200,{'ok':True})
        if not isinstance(email,str) or len(email)>254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):return self.reply(400,{'error':'Please enter a valid email address.'})
        if body.get('eligible') is not True or body.get('consent') is not True:return self.reply(400,{'error':'Please confirm eligibility and consent before registering.'})
        if not isinstance(programme,str) or len(programme)>100:return self.reply(400,{'error':'Please keep the programme field under 100 characters.'})
        token=secrets.token_urlsafe(32)
        with connect() as c:
            cur=c.execute('INSERT OR IGNORE INTO signups VALUES(?,?,?,?,?,?,?)',(email.strip().lower(),programme.strip(),now,channel(body.get('channel')),visitor(body.get('visitor')),digest(token),'research-v1'))
            inserted=cur.rowcount==1
        return self.reply(200,{'ok':True,**({'withdrawal':token} if inserted else {})})

def report(start, end):
    with connect() as c:
        rows=c.execute('SELECT DISTINCT channel FROM events UNION SELECT DISTINCT channel FROM signups').fetchall()
        for row in rows:
            source=row[0]
            visitors=c.execute("SELECT COUNT(DISTINCT visitor) FROM events WHERE event='visit' AND channel=? AND created>=? AND created<?",(source,start,end)).fetchone()[0]
            clicks=c.execute("SELECT COUNT(DISTINCT visitor) FROM events WHERE event='cta' AND channel=? AND created>=? AND created<?",(source,start,end)).fetchone()[0]
            total=c.execute('SELECT COUNT(*) FROM signups WHERE channel=? AND created>=? AND created<?',(source,start,end)).fetchone()[0]
            measured=c.execute("SELECT COUNT(*) FROM signups s WHERE s.channel=? AND s.created>=? AND s.created<? AND EXISTS(SELECT 1 FROM events e WHERE e.visitor=s.visitor AND e.event='visit' AND e.channel=s.channel AND e.created>=? AND e.created<?)",(source,start,end,start,end)).fetchone()[0]
            print(json.dumps({'channel':source,'consenting_eligible_unique_visitors':visitors,'unique_cta_clickers':clicks,'total_registrations':total,'registrations_in_measured_cohort':measured,'conversion_percent':round(measured/visitors*100,2) if visitors else None}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=8080);parser.add_argument('--report',action='store_true');parser.add_argument('--from-date',default='1970-01-01');parser.add_argument('--to-date',default='2100-01-01');args=parser.parse_args()
    if args.report: report(datetime.fromisoformat(args.from_date).replace(tzinfo=timezone.utc).timestamp(),datetime.fromisoformat(args.to_date).replace(tzinfo=timezone.utc).timestamp())
    else:
        connect().close();print(f'Cogniflow is running at http://{args.host}:{args.port}',flush=True)
        try:ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
        except KeyboardInterrupt:pass
