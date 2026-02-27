"""
SPYGLASS API for Vercel - Complete working version
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
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # Handle CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Check if spyglass is available
        if not HAS_SPYGLASS:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Spyglass module not installed',
                'solution': 'Make sure requirements.txt has "-e ." and redeploy',
                'python_path': sys.path,
                'project_root': project_root
            }).encode())
            return
        
        # Get URL parameter
        url = query.get('url', [''])[0]
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'SPYGLASS API is running!',
                'version': '0.1.0',
                'endpoints': {
                    'GET /api/scan?url=example.com': 'Quick scan',
                    'POST /api/scan': 'Full HTML report'
                }
            }).encode())
            return
        
        # Run quick scan
        try:
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create minimal config
            config = ScanConfig(
                max_pages=5,
                concurrent_requests=3,
                check_subdomains=False,
                check_ssl_tls=False,
                check_exposed_data=False
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            # Return summary
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages_scanned': results['statistics']['pages_crawled'],
                'total_issues': results['statistics']['total_issues'],
                'critical_issues': results['statistics']['critical_issues'],
                'score': results['summary']['overall_score']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e),
                'type': str(type(e).__name__)
            }).encode())
    
    def do_POST(self):
        """Handle POST requests - Full HTML report"""
        
        # Get content length
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Set response headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        
        try:
            # Parse JSON
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing url'}).encode())
                return
            
            # Check spyglass
            if not HAS_SPYGLASS:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Spyglass not installed'}).encode())
                return
            
            # Run full scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = ScanConfig(
                max_pages=20,
                concurrent_requests=5
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            
            # Generate HTML report
            report_html = engine.generate_report('html')
            loop.close()
            
            # Send HTML
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(report_html.encode())
            
        except Exception as e:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
