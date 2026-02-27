#  SPYGLASS - Ultimate SEO Intelligence Platform

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue)](https://github.com/ssecgroup/spyglass/actions)
[![GitHub Pages](https://img.shields.io/badge/docs-github%20pages-blue)](https://ssecgroup.github.io/spyglass)
[![Donate](https://img.shields.io/badge/Donate-Ethereum-blue.svg)](#donate)
[![Downloads](https://img.shields.io/github/downloads/ssecgroup/spyglass/total)](https://github.com/ssecgroup/spyglass/releases)
[![Stars](https://img.shields.io/github/stars/ssecgroup/spyglass)](https://github.com/ssecgroup/spyglass/stargazers)

**The most advanced open-source SEO scanner - 100% FREE forever**  
*See what others miss. Find exposed data, subdomains, SSL issues, and more.*

---

##  Features

| Category | Capabilities |
|----------|--------------|
| **Deep Crawling** | 1000+ pages, redirect tracking, robots.txt respect |
| **Exposed Data** | Finds `.git`, `.env`, backups, config files, admin panels |
| **Subdomains** | Certificate logs + DNS brute force (1000+ subdomains) |
| **SSL/TLS** | Expiry alerts, protocol support, vulnerabilities |
| **Security** | HTTP headers, misconfigurations, directory listing |
| **Dead Links** | Full redirect chain analysis, broken link detection |
| **Reports** | Beautiful HTML with charts, one-click PDF export |
| **Free Cloud** | GitHub Actions integration - scan without installation |

---

##  Quick Start

### Install via pip
```bash
pip install spyglass-seo
```

### Scan any website
```bash
spyglass scan https://example.com
```

### Quick info
```bash
spyglass quick https://google.com
```

---

##  Example Report

When you run a scan, SPYGLASS generates a **beautiful HTML report** with:
- Executive summary with scores
- Interactive severity charts
- Critical issues highlighted
- Exposed data tables
- Discovered subdomains
- SSL certificate details
- Actionable recommendations

[ View Sample Report](https://ssecgroup.github.io/spyglass/sample.html)

---

##  Advanced Usage

### Scan with custom options
```bash
spyglass scan https://example.com --max-pages 500 --concurrent 50 --output report.html
```

### Batch scan multiple URLs
```bash
# Create urls.txt with one URL per line
echo "https://site1.com" > urls.txt
echo "https://site2.com" >> urls.txt

# Run batch scan (uses GitHub Actions)
```

### Configuration file
```bash
spyglass configure  # Creates spyglass_config.json
spyglass load spyglass_config.json
```

---

##  GitHub Actions (Free Cloud Scanning)

SPYGLASS includes ready-to-use GitHub Actions workflows:

### Manual scan
1. Go to **Actions** tab
2. Select **SPYGLASS SEO Scan**
3. Enter URL and click **Run workflow**
4. Download report from artifacts

### Scheduled scans
```yaml
# Automatic weekly scans
schedule:
  - cron: '0 0 * * 0'  # Every Sunday
```

### Batch scanning
Scan 100+ websites automatically using the matrix workflow.

---

##  What SPYGLASS Finds

| Severity | What We Detect |
|----------|----------------|
| 🔴 **Critical** | Exposed .git, .env, database backups, AWS keys |
| 🟠 **High** | Admin panels, phpinfo, directory listing, missing security headers |
| 🟡 **Medium** | SSL expiry <30 days, too many redirects, missing meta tags |
| 🔵 **Low** | Server info exposure, missing alt text, old file versions |

---

##  Installation on Different Platforms

### Linux / macOS
```bash
git clone https://github.com/ssecgroup/spyglass.git
cd spyglass
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
spyglass --help
```

### Windows
```powershell
git clone https://github.com/ssecgroup/spyglass.git
cd spyglass
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
spyglass --help
```

### Docker
```bash
docker run --rm ssecgroup/spyglass scan https://example.com
```

---

##  Running Tests

```bash
# Unit tests
pytest tests/

# Test specific scanner
pytest tests/test_scanners/test_ssl_scanner.py

# Test with coverage
pytest --cov=spyglass tests/
```

---

##  Contributing

We welcome contributions! Here's how you can help:

1.  **Report bugs** - Open an issue
2.  **Suggest features** - Start a discussion
3.  **Fix issues** - Submit a PR
4.  **Improve docs** - Update README or wiki
5.  **Translate** - Add language support

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 💖 Donate

SPYGLASS is **completely free** and always will be.  
If you find it valuable, consider supporting development:

**Ethereum**: `0x8242f0f25c5445F7822e80d3C9615e57586c6639`

[![Donate](https://img.shields.io/badge/Donate-Ethereum-blue.svg)](https://etherscan.io/address/0x8242f0f25c5445F7822e80d3C9615e57586c6639)

Your donations help:
-  Add new features
-  Fix bugs faster
-  Improve documentation
-  Keep free cloud scanning alive

---

##  Roadmap

- [x] Core crawling engine
- [x] SSL/TLS scanning
- [x] Subdomain discovery
- [x] Exposed data detection
- [x] Beautiful HTML reports
- [ ] Historical tracking
- [ ] Competitor analysis
- [ ] WordPress plugin
- [ ] Browser extension
- [ ] API marketplace

---

##  License

MIT License - use it anywhere!  
Copyright (c) 2026 [ssecgroup](https://github.com/ssecgroup)

---

## ⭐ Support Us

If you like SPYGLASS:
- ⭐ Star this repository
- 🐦 Share on Twitter
- 👥 Tell your friends
- 💖 Donate to support development

---

**Made with ❤️ by [ssecgroup](https://github.com/ssecgroup)**  
*Open source. Always free. Forever.*
