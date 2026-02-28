"""
ssec-seo API for Vercel - Direct file import solution
"""
import sys
import os
import json
import asyncio
import importlib.util
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add paths to sys.path
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'ssec_seo'))
sys.path.insert(0, os.path.join(project_root, 'ssec_seo', 'core'))

# Direct file imports using importlib
def import_from_path(module_name, file_path):
    """Import a module from file path"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Failed to import {module_name} from {file_path}: {e}")
        return None

# Import core modules directly from files
ultimate_engine_path = os.path.join(project_root, 'ssec_seo', 'core', 'ultimate_engine.py')
config_path = os.path.join(project_root, 'ssec_seo', 'core', 'config.py')

ultimate_module = import_from_path('ultimate_engine', ultimate_engine_path)
config_module = import_from_path('config', config_path)

if ultimate_module and config_module:
    UltimateSEOEngine = ultimate_module.UltimateSEOEngine
    ScanConfig = config_module.ScanConfig
    HAS_ENGINE = True
    print("✅ Direct file imports successful")
else:
    HAS_ENGINE = False
    print("❌ Direct file imports failed")

class handler(BaseHTTPRequestHandler):
    """Handle HTTP requests"""
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # Check if engine is available
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'SEO engine not available',
                'message': 'The scanning engine could not be loaded',
                'debug': {
                    'project_root': project_root,
                    'ultimate_engine_exists': os.path.exists(ultimate_engine_path),
                    'config_exists': os.path.exists(config_path),
                    'core_files': os.listdir(os.path.join(project_root, 'ssec_seo', 'core')) if os.path.exists(os.path.join(project_root, 'ssec_seo', 'core')) else []
                }
            }).encode())
            return
        
        # Get URL parameter
        url = query.get('url', [None])[0]
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo API is running',
                'version': '0.1.0'
            }).encode())
            return
        
        # Run quick scan
        try:
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create minimal config
            config = ScanConfig(
                max_pages=1,
                concurrent_requests=1,
                check_subdomains=False,
                check_ssl_tls=False,
                check_exposed_data=False
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages_scanned': results['statistics']['pages_crawled'],
                'total_issues': results['statistics']['total_issues'],
                'critical_issues': results['statistics']['critical_issues']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({'error': 'Engine not available'}).encode())
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.wfile.write(json.dumps({'error': 'Missing url'}).encode())
                return
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'message': 'Scan started',
                'url': url
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
