from http.server import BaseHTTPRequestHandler
import json
import asyncio
import sys
import os
from urllib.parse import parse_qs, urlparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spyglass.core.ultimate_engine import UltimateSEOEngine
from spyglass.core.config import ScanConfig

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - scan website"""
        
        # Parse query parameters
        query = parse_qs(urlparse(self.path).query)
        url = query.get('url', [''])[0]
        
        if not url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Missing url parameter'
            }).encode())
            return
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Run scan
        try:
            # Run async scan in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = ScanConfig(max_pages=10, concurrent_requests=5)
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            
            # Generate report
            report_html = engine.generate_report('html')
            
            response = {
                'success': True,
                'url': url,
                'stats': results['statistics'],
                'summary': results['summary'],
                'issues_count': len(results['issues']),
                'report': report_html[:500] + '...'  # Preview
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode())
        
        loop.close()
    
    def do_POST(self):
        """Handle POST requests - full scan with HTML report"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.send_response(400)
                self.end_headers()
                return
            
            # Run scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = ScanConfig(max_pages=50, concurrent_requests=10)
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            
            # Generate full HTML report
            report_html = engine.generate_report('html')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(report_html.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
