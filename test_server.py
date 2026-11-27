"""Local integration checks. Uses a temporary database, never real registrations."""
import contextlib, io, json, tempfile, threading, unittest, urllib.request, urllib.error
from pathlib import Path
import server

class ResearchFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();server.DB=Path(cls.temp.name)/'test.sqlite3'
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.url='http://127.0.0.1:'+str(cls.http.server_port)
        threading.Thread(target=cls.http.serve_forever,daemon=True).start()
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close()
        # SQLite connections are allowed to finish before Windows removes the directory.
        import gc;gc.collect();cls.temp.cleanup()
    def post(self,path,body,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=urllib.request.Request(self.url+path,data=json.dumps(body).encode(),headers=headers)
        try:
            with urllib.request.urlopen(req) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as r:return r.code,json.load(r)
    def test_complete_flow(self):
        for path in ['/','/privacy.html','/styles.css','/app.js','/mark.svg']:
            with urllib.request.urlopen(self.url+path) as r:self.assertEqual(r.status,200)
        for path in ['/server.py','/data/research.sqlite3','/../server.py']:
            with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(self.url+path)
        body={'email':'test@example.com','programme':'Test','eligible':True,'consent':True,'channel':'test','visitor':'12345678-1234-1234-1234-123456789012'}
        self.assertEqual(self.post('/api/signup',{**body,'consent':False})[0],400)
        self.assertEqual(self.post('/api/signup',{**body,'email':'invalid'})[0],400)
        self.assertEqual(self.post('/api/signup',body,'https://other.example')[0],403)
        for _ in range(2):self.assertEqual(self.post('/api/event',{'visitor':body['visitor'],'event':'visit','channel':'test','eligible':True})[0],200)
        status,result=self.post('/api/signup',body);self.assertEqual(status,200);token=result['withdrawal']
        self.assertNotIn('withdrawal',self.post('/api/signup',body)[1])
        with contextlib.redirect_stdout(io.StringIO()) as capture:server.report(0,9999999999)
        report=json.loads(capture.getvalue().strip());self.assertEqual(report['consenting_eligible_unique_visitors'],1);self.assertEqual(report['registrations_in_measured_cohort'],1);self.assertEqual(report['conversion_percent'],100)
        self.assertEqual(self.post('/api/withdraw',{'token':token})[0],200)
        with server.connect() as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM signups').fetchone()[0],0)
if __name__=='__main__':unittest.main()
