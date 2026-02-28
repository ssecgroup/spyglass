"""
Ultimate SEO Engine - By [github/ssecgroup] Ties everything together
"""
import asyncio
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Optional
import json
import time
import aiohttp

# FIXED: Changed all imports from spyglass.core to core
from core.config import ScanConfig
from core.crawler.advanced_spider import AdvancedSEOSpider
from core.scanners.ssl_scanner import SSLScanner
from core.scanners.subdomain_scanner import SubdomainScanner
from core.scanners.http_misconfig import HTTPMisconfigScanner
from core.scanners.exposed_data import ExposedDataScanner
from core.scanners.dead_links import DeadLinkScanner
from core.scanners.http_headers import HTTPHeadersScanner
from core.scanners.redirects import RedirectScanner
from core.scanners.security import SecurityScanner
from core.scanners.tech_detection import TechnologyDetector
from core.reporters.ultimate_reporter import UltimateReporter

class UltimateSEOEngine:
    """
    The most advanced open-source SEO engine ever built - by https://github/ssecgroup
    """
    
    def __init__(self, config: Optional[ScanConfig] = None):
        self.config = config or ScanConfig()
        self.results = {}
        self.start_time = None
        self.stats = {
            'phases_completed': [],
            'current_phase': '',
            'errors': []
        }
        
    async def scan(self, url: str) -> Dict:
        """Execute complete SEO scan"""
        self.start_time = time.time()
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        print("\n" + "="*80)
        print(f" SSEC-SEO ULTIMATE SEO SCAN")
        print("="*80)
        print(f"Target: {url}")
        print(f"Domain: {domain}")
        print(f"Config: {self.config.max_pages} pages, {self.config.concurrent_requests} concurrent")
        print("="*80 + "\n")
        
        # Initialize results structure
        self.results = {
            'target_url': url,
            'domain': domain,
            'scan_date': datetime.now().isoformat(),
            'config': self.config.__dict__,
            'summary': {},
            'crawl': {},
            'ssl': {},
            'subdomains': {},
            'misconfigurations': {},
            'exposed_data': [],
            'dead_links': [],
            'security_headers': {},
            'redirects': {},
            'security_issues': [],
            'technologies': [],
            'issues': [],
            'recommendations': [],
            'performance': {},
            'statistics': {
                'pages_crawled': 0,
                'total_issues': 0,
                'critical_issues': 0,
                'high_issues': 0,
                'medium_issues': 0,
                'low_issues': 0,
                'total_time': 0
            }
        }
        
        # Create shared session for all scanners
        connector = aiohttp.TCPConnector(limit=100, ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # Phase 1: Crawl website
            self.stats['current_phase'] = 'crawling'
            print("\n📡 PHASE 1: Advanced Website Crawling")
            print("-" * 40)
            
            async with AdvancedSEOSpider(self.config) as spider:
                crawl_results = await spider.crawl(url)
                self.results['crawl'] = crawl_results
                self.results['statistics']['pages_crawled'] = len(crawl_results.get('pages', []))
            
            self.stats['phases_completed'].append('crawling')
            
            # Phase 2: SSL/TLS Analysis
            if self.config.check_ssl_tls:
                self.stats['current_phase'] = 'ssl_analysis'
                print("\n🔒 PHASE 2: SSL/TLS Deep Analysis")
                print("-" * 40)
                
                ssl_scanner = SSLScanner()
                ssl_results = await ssl_scanner.scan(domain)
                self.results['ssl'] = ssl_results
                
                if ssl_results.get('issues'):
                    self.results['issues'].extend(ssl_results['issues'])
            
            # Phase 3: Subdomain Discovery
            if self.config.check_subdomains:
                self.stats['current_phase'] = 'subdomain_discovery'
                print("\n🌐 PHASE 3: Subdomain Discovery")
                print("-" * 40)
                
                sub_scanner = SubdomainScanner()
                sub_results = await sub_scanner.discover(domain)
                self.results['subdomains'] = sub_results
                
                print(f"✅ Found {sub_results.get('total_found', 0)} subdomains")
                print(f"✅ {len(sub_results.get('active', []))} active")
            
            # Phase 4: HTTP Misconfigurations
            if self.config.check_misconfigurations:
                self.stats['current_phase'] = 'misconfiguration_scan'
                print("\n⚠️ PHASE 4: HTTP Misconfiguration Scan")
                print("-" * 40)
                
                http_scanner = HTTPMisconfigScanner()
                http_results = await http_scanner.scan(url, session)
                self.results['misconfigurations'] = http_results
                
                # Add exposed paths to issues
                for path in http_results.get('exposed_paths', []):
                    self.results['issues'].append({
                        'type': 'exposed_path',
                        'severity': path['severity'],
                        'title': f"Exposed: {path['url']}",
                        'url': path['url'],
                        'description': f"Exposed path with status {path.get('status', 200)}"
                    })
            
            # Phase 5: Exposed Data Scan
            if self.config.check_exposed_data:
                self.stats['current_phase'] = 'exposed_data_scan'
                print("\n🔍 PHASE 5: Exposed Data Scan")
                print("-" * 40)
                
                exposed_scanner = ExposedDataScanner()
                exposed_results = await exposed_scanner.scan(url, session)
                self.results['exposed_data'] = exposed_results
                
                # Add exposed data to issues
                for item in exposed_results:
                    self.results['issues'].append({
                        'type': 'exposed_data',
                        'severity': item['severity'],
                        'title': f"Exposed: {item['type']}",
                        'url': item['url'],
                        'description': item.get('description', 'Exposed sensitive data')
                    })
            
            # Phase 6: Dead Links Check
            if self.config.check_dead_links:
                self.stats['current_phase'] = 'dead_links'
                print("\n💀 PHASE 6: Dead Links Check")
                print("-" * 40)
                
                dead_scanner = DeadLinkScanner()
                pages = self.results['crawl'].get('pages', [])
                dead_results = await dead_scanner.scan(pages, session)
                self.results['dead_links'] = dead_results
                
                for link in dead_results:
                    self.results['issues'].append({
                        'type': 'dead_link',
                        'severity': link['severity'],
                        'title': f"Dead link: {link['url']}",
                        'url': link['url'],
                        'description': f"Broken link with status {link.get('status', 'error')}"
                    })
            
            # Phase 7: Security Headers
            self.stats['current_phase'] = 'security_headers'
            print("\n🛡️ PHASE 7: Security Headers Analysis")
            print("-" * 40)
            
            headers_scanner = HTTPHeadersScanner()
            headers_results = await headers_scanner.scan(url, session)
            self.results['security_headers'] = headers_results
            self.results['issues'].extend(headers_results.get('issues', []))
            
            # Phase 8: Redirect Analysis
            self.stats['current_phase'] = 'redirects'
            print("\n🔄 PHASE 8: Redirect Chain Analysis")
            print("-" * 40)
            
            redirect_scanner = RedirectScanner()
            redirect_results = await redirect_scanner.scan(url, session)
            self.results['redirects'] = redirect_results
            self.results['issues'].extend(redirect_results.get('issues', []))
            
            # Phase 9: Security Vulnerability Scan
            self.stats['current_phase'] = 'security_scan'
            print("\n🔐 PHASE 9: Security Vulnerability Scan")
            print("-" * 40)
            
            security_scanner = SecurityScanner()
            security_results = await security_scanner.scan(url, session)
            self.results['security_issues'] = security_results.get('issues', [])
            self.results['issues'].extend(security_results.get('issues', []))
            
            # Phase 10: Technology Detection
            self.stats['current_phase'] = 'tech_detection'
            print("\n🔧 PHASE 10: Technology Detection")
            print("-" * 40)
            
            tech_detector = TechnologyDetector()
            tech_count = 0
            if self.results['crawl'].get('pages'):
                for page in self.results['crawl']['pages'][:5]:  # Check first 5 pages
                    html = page.get('html', '')
                    headers = page.get('headers', {})
                    if html or headers:
                        tech_results = tech_detector.detect(headers, html, page['url'])
                        self.results['technologies'].extend(tech_results)
                        tech_count += len(tech_results)
                print(f"✅ Detected {tech_count} technologies")
        
        # Phase 11: Generate Recommendations
        self.stats['current_phase'] = 'recommendations'
        print("\n💡 PHASE 11: Generating Recommendations")
        print("-" * 40)
        
        self.results['recommendations'] = self._generate_recommendations()
        
        # Phase 12: Calculate Summary
        self.stats['current_phase'] = 'summary'
        self.results['summary'] = self._calculate_summary()
        self.results['statistics']['total_time'] = time.time() - self.start_time
        self.results['statistics']['total_issues'] = len(self.results['issues'])
        self.results['statistics']['critical_issues'] = sum(
            1 for i in self.results['issues'] if i.get('severity') == 'critical'
        )
        self.results['statistics']['high_issues'] = sum(
            1 for i in self.results['issues'] if i.get('severity') == 'high'
        )
        self.results['statistics']['medium_issues'] = sum(
            1 for i in self.results['issues'] if i.get('severity') == 'medium'
        )
        self.results['statistics']['low_issues'] = sum(
            1 for i in self.results['issues'] if i.get('severity') == 'low'
        )
        
        print("\n" + "="*80)
        print(f"✅ SCAN COMPLETE!")
        print(f"⏱️  Time: {self.results['statistics']['total_time']:.2f} seconds")
        print(f"📊 Pages: {self.results['statistics']['pages_crawled']}")
        print(f"⚠️  Issues: {self.results['statistics']['total_issues']}")
        print(f"🔴 Critical: {self.results['statistics']['critical_issues']}")
        print(f"🟠 High: {self.results['statistics']['high_issues']}")
        print(f"🟡 Medium: {self.results['statistics']['medium_issues']}")
        print(f"🔵 Low: {self.results['statistics']['low_issues']}")
        print("="*80)
        
        return self.results
    
    def _generate_recommendations(self) -> List:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Group issues by type
        issues_by_type = {}
        for issue in self.results['issues']:
            issue_type = issue.get('type', 'other')
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # Generate recommendations for each issue type
        for issue_type, issues in issues_by_type.items():
            if issue_type == 'exposed_path' or issue_type == 'exposed_data':
                recommendations.append({
                    'priority': 'high',
                    'category': 'security',
                    'title': 'Secure exposed paths',
                    'description': f'Found {len(issues)} exposed paths that should be secured.',
                    'action': 'Review and restrict access using .htaccess or server config.',
                    'examples': [i['url'] for i in issues[:3]]
                })
            
            elif issue_type == 'missing_security_header':
                headers = list(set([i.get('header', 'Unknown') for i in issues]))
                recommendations.append({
                    'priority': 'medium',
                    'category': 'security',
                    'title': 'Add security headers',
                    'description': f'Missing security headers: {", ".join(headers[:3])}',
                    'action': 'Add these headers to your server configuration.'
                })
            
            elif issue_type == 'dead_link':
                recommendations.append({
                    'priority': 'high',
                    'category': 'seo',
                    'title': 'Fix broken links',
                    'description': f'Found {len(issues)} broken links.',
                    'action': 'Update or remove broken links to improve user experience.'
                })
            
            elif issue_type == 'too_many_redirects':
                recommendations.append({
                    'priority': 'medium',
                    'category': 'performance',
                    'title': 'Optimize redirect chains',
                    'description': 'Long redirect chains slow down page load.',
                    'action': 'Reduce number of redirects or update direct links.'
                })
        
        # SSL recommendations
        ssl = self.results.get('ssl', {})
        cert = ssl.get('certificate', {})
        days = cert.get('days_until_expiry', 365)
        if days < 30:
            recommendations.append({
                'priority': 'critical',
                'category': 'security',
                'title': 'SSL Certificate Expiring Soon',
                'description': f'SSL certificate expires in {days} days.',
                'action': 'Renew SSL certificate immediately.'
            })
        
        return recommendations
    
    def _calculate_summary(self) -> Dict:
        """Calculate overall summary"""
        total_issues = len(self.results['issues'])
        critical = self.results['statistics']['critical_issues']
        high = self.results['statistics']['high_issues']
        medium = self.results['statistics']['medium_issues']
        low = self.results['statistics']['low_issues']
        
        # Calculate scores
        seo_score = 100 - (critical * 10 + high * 5 + medium * 2 + low * 1)
        seo_score = max(0, min(100, seo_score))
        
        security_score = 100 - (critical * 15 + high * 7 + medium * 3)
        security_score = max(0, min(100, security_score))
        
        # Performance score based on load times
        pages = self.results['crawl'].get('pages', [])
        if pages:
            avg_load = sum(p.get('load_time', 0) for p in pages) / len(pages)
            if avg_load < 1:
                performance_score = 90
            elif avg_load < 2:
                performance_score = 70
            elif avg_load < 3:
                performance_score = 50
            else:
                performance_score = 30
        else:
            performance_score = 50
        
        overall_score = (seo_score + security_score + performance_score) // 3
        
        # Determine risk level
        if critical > 0:
            risk_level = 'critical'
        elif high > 0:
            risk_level = 'high'
        elif medium > 5:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'overall_score': overall_score,
            'seo_score': seo_score,
            'security_score': security_score,
            'performance_score': performance_score,
            'total_issues': total_issues,
            'critical_issues': critical,
            'high_issues': high,
            'medium_issues': medium,
            'low_issues': low,
            'risk_level': risk_level
        }
    
    def generate_report(self, format: str = 'html') -> str:
        """Generate report in specified format"""
        reporter = UltimateReporter(self.config)
        return reporter.generate(self.results, format)
