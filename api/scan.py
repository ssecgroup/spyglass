"""
ssec-seo API for Vercel - Working version with mock data
"""
import json
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    """Handle HTTP requests"""
    
    def do_GET(self):
        """Handle GET requests - Quick scan with mock data"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # Get URL parameter
        url = query.get('url', [None])[0]
        
        if not url:
            # Return API info
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo API is running',
                'version': '0.1.0'
            }).encode())
            return
        
        # Generate mock scan data
        mock_data = self.generate_mock_data(url)
        self.wfile.write(json.dumps(mock_data).encode())
    
    def do_POST(self):
        """Handle POST requests - Full scan with mock HTML report"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Generate mock HTML report
        html_report = self.generate_mock_html()
        self.wfile.write(html_report.encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def generate_mock_data(self, url):
        """Generate mock scan data"""
        # Random but realistic values
        pages = random.randint(5, 50)
        critical = random.randint(0, 3)
        high = random.randint(1, 5)
        medium = random.randint(2, 8)
        low = random.randint(3, 10)
        total = critical + high + medium + low
        
        # Calculate score (lower issues = higher score)
        score = max(30, min(95, 100 - (critical * 10 + high * 3 + medium * 1)))
        
        # Determine risk level
        if critical > 0:
            risk = 'critical'
        elif high > 2:
            risk = 'high'
        elif medium > 5:
            risk = 'medium'
        else:
            risk = 'low'
        
        return {
            'status': 'success',
            'url': url,
            'pages_scanned': pages,
            'total_issues': total,
            'critical_issues': critical,
            'high_issues': high,
            'medium_issues': medium,
            'low_issues': low,
            'score': score,
            'risk_level': risk
        }
    
    def generate_mock_html(self):
        """Generate mock HTML report"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>ssec-seo Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #667eea; }}
        .score {{ font-size: 48px; color: #27ae60; }}
        .issues {{ margin: 20px 0; }}
        .critical {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <h1>🔍 ssec-seo SEO Report</h1>
    <p>This is a mock report. Full engine coming soon!</p>
    <div class="score">Score: {random.randint(60, 95)}/100</div>
    <div class="issues">
        <h3>Issues Found:</h3>
        <ul>
            <li class="critical">🔴 Missing meta descriptions (3 pages)</li>
            <li>🟠 Broken links found (2 links)</li>
            <li>🟡 SSL certificate expires in 45 days</li>
            <li>🔵 Images missing alt text (12 images)</li>
        </ul>
    </div>
</body>
</html>"""
