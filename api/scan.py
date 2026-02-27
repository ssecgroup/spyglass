"""
SPYGLASS API for Vercel - Complete working version with proper imports
"""
import sys
import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add all possible paths
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'spyglass'))
sys.path.insert(0, os.path.join(project_root, 'core'))

# Try multiple import strategies
HAS_SPYGLASS = False
UltimateSEOEngine = None
ScanConfig = None

try:
    # Strategy 1: Direct import from spyglass package
    from spyglass.core.ultimate_engine import UltimateSEOEngine
    from spyglass.core.config import ScanConfig
    HAS_SPYGLASS = True
    print("✅ Import strategy 1 succeeded")
except ImportError as e1:
    try:
        # Strategy 2: Import from core directly
        sys.path.insert(0, os.path.join(project_root, 'core'))
        from ultimate_engine import UltimateSEOEngine
        from config import ScanConfig
        HAS_SPYGLASS = True
        print("✅ Import strategy 2 succeeded")
    except ImportError as e2:
        try:
            # Strategy 3: Import from local modules
            from core.ultimate_engine import UltimateSEOEngine
            from core.config import ScanConfig
            HAS_SPYGLASS = True
            print("✅ Import strategy 3 succeeded")
        except ImportError as e3:
            print(f"❌ All import strategies failed:")
            print(f"  Strategy 1: {e1}")
            print(f"  Strategy 2: {e2}")
            print(f"  Strategy 3: {e3}")
            print(f"Python path: {sys.path}")
            print(f"Project root contents: {os.listdir(project_root) if os.path.exists(project_root) else 'Not found'}")

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
            
            # Get directory listing for debugging
            project_contents = []
            if os.path.exists(project_root):
                project_contents = os.listdir(project_root)[:10]
            
            core_path = os.path.join(project_root, 'core')
            core_contents = []
            if os.path.exists(core_path):
                core_contents = os.listdir(core_path)[:10]
            
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Spyglass module not installed',
                'message': 'Running in diagnostic mode',
                'project_root': project_root,
                'project_contents': project_contents,
                'core_contents': core_contents,
                'python_path': sys.path[:5]
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
                    'import_status': 'success',
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
                    max_pages=2,
                    concurrent_requests=1,
                    check_subdomains=False,
                    check_ssl_tls=False,
                    check_exposed_data=False,
                    check_misconfigurations=False,
                    check_dead_links=False
                )
            else:
                config = ScanConfig(
                    max_pages=5,
                    concurrent_requests=2,
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
