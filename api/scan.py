"""
ssec-seo API for Vercel - UNIVERSAL IMPORT FIX
"""
import sys
import os
import json
import asyncio
import inspect
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core_dir = os.path.join(project_root, 'core')
sys.path.insert(0, core_dir)

# Dynamic import that finds ANY class
HAS_ENGINE = False
UltimateSEOEngine = None
ScanConfig = None

try:
    # Import the modules
    import ultimate_engine
    import config
    
    # Find any class in ultimate_engine that looks like an SEO engine
    for name, obj in inspect.getmembers(ultimate_engine):
        if inspect.isclass(obj) and ('SEO' in name or 'Engine' in name or 'Ultimate' in name):
            UltimateSEOEngine = obj
            print(f" Found engine class: {name}")
            break
    
    # Find ScanConfig class
    for name, obj in inspect.getmembers(config):
        if inspect.isclass(obj) and ('ScanConfig' in name or 'Config' in name):
            ScanConfig = obj
            print(f" Found config class: {name}")
            break
    
    if UltimateSEOEngine and ScanConfig:
        HAS_ENGINE = True
        print(" REAL ENGINE READY")
        
except Exception as e:
    print(f"❌ Error: {e}")
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
                'status': 'error',
                'message': 'Engine not loaded',
                'found_classes': {
                    'ultimate_engine': dir(ultimate_engine) if 'ultimate_engine' in dir() else [],
                    'config': dir(config) if 'config' in dir() else []
                }
            }).encode())
            return
        
        if not url:
            self.wfile.write(json.dumps({'status': 'ready'}).encode())
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config_obj = ScanConfig(max_pages=2, concurrent_requests=1)
            engine = UltimateSEOEngine(config_obj)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages': results['statistics']['pages_crawled'],
                'issues': results['statistics']['total_issues']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()