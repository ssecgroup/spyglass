"""
ssec-seo API for Vercel - REAL ENGINE WORKING VERSION
"""
import sys
import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core_dir = os.path.join(project_root, 'core')
sys.path.insert(0, core_dir)

# Import the REAL engine with correct class name
try:
    from ultimate_engine import UltimateSEOEngine
    from config import ScanConfig
    HAS_ENGINE = True
    print(" REAL SEO ENGINE LOADED")
except Exception as e:
    print(f" Failed: {e}")
    HAS_ENGINE = False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        url = query.get('url', [None])[0]
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({
                'error': 'Engine failed to load',
                'status': 'error'
            }).encode())
            return
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ready',
                'engine': 'UltimateSEOEngine'
            }).encode())
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = ScanConfig(max_pages=3, concurrent_requests=2)
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages': results['statistics']['pages_crawled'],
                'issues': results['statistics']['total_issues'],
                'critical': results['statistics']['critical_issues']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()