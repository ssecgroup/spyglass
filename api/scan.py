"""
ssec-seo API for Vercel - DEBUG VERSION
"""
import sys
import os
import json
import asyncio
import importlib.util
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
debug_info = {
    'project_root': project_root,
    'files_checked': {},
    'import_attempts': [],
    'python_path': sys.path[:]
}

def debug_import(module_name, file_path):
    """Try to import and return detailed debug info"""
    debug_info['files_checked'][file_path] = os.path.exists(file_path)
    
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            return None, f"spec_from_file_location returned None for {file_path}"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        debug_info['import_attempts'].append({
            'file': file_path,
            'success': True
        })
        return module, None
    except Exception as e:
        debug_info['import_attempts'].append({
            'file': file_path,
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        return None, str(e)

# Check core directory
core_dir = os.path.join(project_root, 'ssec_seo', 'core')
debug_info['core_dir_exists'] = os.path.exists(core_dir)
if os.path.exists(core_dir):
    debug_info['core_files'] = os.listdir(core_dir)

# Try to import engine
ultimate_path = os.path.join(core_dir, 'ultimate_engine.py')
config_path = os.path.join(core_dir, 'config.py')

ultimate_module, ult_err = debug_import('ultimate_engine', ultimate_path)
config_module, conf_err = debug_import('config', config_path)

if ultimate_module and config_module:
    try:
        UltimateSEOEngine = ultimate_module.UltimateSEOEngine
        ScanConfig = config_module.ScanConfig
        HAS_REAL_ENGINE = True
        debug_info['engine_status'] = 'loaded'
    except Exception as e:
        HAS_REAL_ENGINE = False
        debug_info['engine_status'] = f'class_error: {e}'
else:
    HAS_REAL_ENGINE = False
    debug_info['engine_status'] = 'import_failed'
    debug_info['ultimate_error'] = ult_err
    debug_info['config_error'] = conf_err

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # If debug parameter is present, return debug info
        if 'debug' in query:
            self.wfile.write(json.dumps(debug_info, default=str, indent=2).encode())
            return
        
        if not HAS_REAL_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Real SEO engine not available',
                'debug_hint': 'Add ?debug=true to see debug info'
            }).encode())
            return
        
        # Rest of your real engine code...
        url = query.get('url', [None])[0]
        if url:
            self.wfile.write(json.dumps({
                'status': 'success',
                'message': 'Engine loaded!',
                'url': url
            }).encode())
        else:
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo REAL engine is ready'
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
