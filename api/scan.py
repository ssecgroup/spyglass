"""
SPYGLASS API for Vercel - Complete working version with POST support
"""
import sys
import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Try importing spyglass
try:
    from spyglass.core.ultimate_engine import UltimateSEOEngine
    from spyglass.core.config import ScanConfig
    HAS_SPYGLASS = True
    print("✅ Spyglass imported successfully")
except ImportError as e:
    HAS_SPYGLASS = False
    print(f"❌ Spyglass import error: {e}")

class handler(BaseHTTPRequestHandler):
    """Handle HTTP requests to Vercel"""
    
    def do_GET(self):
        """Handle GET requests - API status and quick scan"""
        self._handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests - Full HTML report"""
        self._handle_request('POST')
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _handle_request(self, method):
        """Unified request handler"""
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # Handle CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Check if spyglass is available
        if not HAS_SPYGLASS:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Spyglass module not installed',
                'solution': 'Make sure requirements.txt has "-e ." and redeploy',
                'python_path': sys.path,
                'project_root': project_root
            }).encode())
            return
        
        # Handle different methods
        if method == 'GET':
            # Get URL from query string
            url = query.get('url', [''])[0]
            
            if not url:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'ok',
                    'message': 'SPYGLASS API is running!',
                    'version': '0.1.0',
                    'endpoints': {
                        'GET /api/scan?url=example.com': 'Quick scan',
                        'POST /api/scan (JSON with {"url": "..."})': 'Full HTML report'
                    }
                }).encode())
                return
            
            # Quick scan with GET
            self._run_scan(url, quick=True)
            
        elif method == 'POST':
            # Get URL from POST body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                url = data.get('url')
                
                if not url:
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Missing url parameter'}).encode())
                    return
                
                # Full scan with POST
                self._run_scan(url, quick=False)
                
            except json.JSONDecodeError:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
    
    def _run_scan(self, url, quick=True):
        """Run scan and return results"""
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Configure scan based on type
            if quick:
                config = ScanConfig(
                    max_pages=3,
                    concurrent_requests=2,
                    check_subdomains=False,
                    check_ssl_tls=False,
                    check_exposed_data=False,
                    check_misconfigurations=False,
                    check_dead_links=False
                )
            else:
                config = ScanConfig(
                    max_pages=10,
                    concurrent_requests=3,
                    check_subdomains=True,
                    check_ssl_tls=True,
                    check_exposed_data=True,
                    check_misconfigurations=True,
                    check_dead_links=True
                )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            if quick:
                # Return JSON for quick scan
                self.send_header('Content-type', 'application/json')
                self.end_headers()
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
            else:
                # Return HTML for full report
                report_html = engine.generate_report('html')
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(report_html.encode())
            
        except Exception as e:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e),
                'type': str(type(e).__name__)
            }).encode())
