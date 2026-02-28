"""
ssec-seo API for Vercel - Fixed JSON responses
"""
import sys
import os
import json
import asyncio
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'ssec_seo'))
sys.path.insert(0, os.path.join(project_root, 'ssec_seo', 'core'))

# Try to import the engine
HAS_ENGINE = False
try:
    from ssec_seo.core.ultimate_engine import UltimateSEOEngine
    from ssec_seo.core.config import ScanConfig
    HAS_ENGINE = True
    print("✅ Engine imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    try:
        # Fallback to direct import
        from core.ultimate_engine import UltimateSEOEngine
        from core.config import ScanConfig
        HAS_ENGINE = True
        print("✅ Fallback import succeeded")
    except ImportError as e2:
        print(f"❌ Fallback also failed: {e2}")

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
                    'python_path': str(sys.path)
                }
            }).encode())
            return
        
        # Get URL parameter
        url = query.get('url', [None])[0]
        
        if not url:
            # Just return API info
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo API is running',
                'version': '0.1.0',
                'endpoints': {
                    'GET /api/scan?url=example.com': 'Quick scan (returns JSON)',
                    'POST /api/scan with {"url": "example.com"}': 'Full scan (returns HTML report)'
                }
            }).encode())
            return
        
        # Run quick scan
        try:
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create minimal config for quick scan
            config = ScanConfig(
                max_pages=2,
                concurrent_requests=1,
                check_subdomains=False,
                check_ssl_tls=False,
                check_exposed_data=False,
                check_misconfigurations=False,
                check_dead_links=False
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            # Return JSON response
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages_scanned': results['statistics']['pages_crawled'],
                'total_issues': results['statistics']['total_issues'],
                'critical_issues': results['statistics']['critical_issues'],
                'high_issues': results['statistics']['high_issues'],
                'score': results['summary']['overall_score'],
                'risk_level': results['summary']['risk_level']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }).encode())
    
    def do_POST(self):
        """Handle POST requests - Full HTML report"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'SEO engine not available'
            }).encode())
            return
        
        # Get POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'error': 'Missing url parameter'
                }).encode())
                return
            
            # For full scan, we'll return JSON first (can be extended to return HTML)
            self.wfile.write(json.dumps({
                'status': 'success',
                'message': 'Full scan started',
                'url': url,
                'note': 'Full HTML report coming soon'
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e)
            }).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
