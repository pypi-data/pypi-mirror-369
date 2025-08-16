#!/usr/bin/env python3

import os
import base64
import cgi
from urllib.parse import parse_qs, unquote
from wsgiref.util import setup_testing_defaults
from wsgiref.headers import Headers
import threading
import time

# CONFIG
UPLOAD_FOLDER = os.path.abspath("shared")
AUTH_USER = os.environ.get("LFS_USER", "admin")
AUTH_PASS = os.environ.get("LFS_PASS", "admin")
MAX_MB = 2048
MAX_BYTES = MAX_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
    <html>
        <head><title>LAN File Server</title></head>
        <body>
            <h1>LAN File Server</h1>
            <p>Upload file (max {max_mb} MB). Remote: {remote}</p>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file" id="fileInput" onchange="toggleUpload()">
                <input type="submit" value="Upload" id="uploadBtn" style="display: none;">
            </form>
            <hr>
                <h2>Files</h2>
            <ul>
                {file_list}
            </ul>
        </body>
        <script>
        function toggleUpload() {{
            const input = document.getElementById("fileInput");
            const btn = document.getElementById("uploadBtn");
            btn.style.display = input.files.length ? "inline" : "none";
        }}
        </script>
    </html>
"""

def auth_required(environ):
    auth = environ.get('HTTP_AUTHORIZATION')
    if not auth or not auth.startswith('Basic '):
        return False
    try:
        encoded = auth.split(' ', 1)[1].strip()
        decoded = base64.b64decode(encoded).decode('utf-8')
        username, password = decoded.split(':', 1)
        return username == AUTH_USER and password == AUTH_PASS
    except Exception:
        return False

def unauthorized(start_response):
    start_response('401 Unauthorized', [
        ('Content-Type', 'text/plain'),
        ('WWW-Authenticate', 'Basic realm="Login Required"')
    ])
    return [b'Authentication required']

def not_found(start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']

def list_files():
    files = sorted(os.listdir(UPLOAD_FOLDER))
    if not files:
        return "<li><em>No files</em></li>"
    return "\n".join(
        f'<li><a href="/files/{f}">{f}</a> (<a href="/files/{f}?dl=1">direct</a>)</li>'
        for f in files
    )

def cleanup_old_files(interval=600, max_age=3600):
    """
    Delete files older than `max_age` seconds every `interval` seconds.
    """
    def cleaner():
        while True:
            now = time.time()
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    file_age = now - os.path.getmtime(filepath)
                    if file_age > max_age:
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print(f"Failed to delete {filepath}: {e}")
            time.sleep(interval)

    thread = threading.Thread(target=cleaner, daemon=True)
    thread.start()

cleanup_started = False

def app(environ, start_response):
    setup_testing_defaults(environ)

    if not auth_required(environ):
        return unauthorized(start_response)

    global cleanup_started
    if not cleanup_started:
        cleanup_old_files()
        cleanup_started = True

    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']

    if method == 'GET' and path == '/':
        # Render upload page
        remote = environ.get('REMOTE_ADDR', 'unknown')
        html = HTML_TEMPLATE.format(max_mb=MAX_MB, remote=remote, file_list=list_files())
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return [html.encode('utf-8')]

    elif method == 'POST' and path == '/':
        # Handle file upload
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            if content_length > MAX_BYTES:
                start_response('413 Payload Too Large', [('Content-Type', 'text/plain')])
                return [b'File too large']

            fs = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
            if 'file' not in fs:
                start_response('400 Bad Request', [('Content-Type', 'text/plain')])
                return [b'No file uploaded']

            file_item = fs['file']
            filename = os.path.basename(file_item.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            with open(filepath, 'wb') as f:
                data = file_item.file.read()
                if len(data) > MAX_BYTES:
                    start_response('413 Payload Too Large', [('Content-Type', 'text/plain')])
                    return [b'File too large']
                f.write(data)

            start_response('303 See Other', [('Location', '/')])
            return []

        except Exception as e:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [f"Error: {str(e)}".encode('utf-8')]

    elif path.startswith('/files/'):
        filename = unquote(path[len('/files/'):])
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return not_found(start_response)

        query = parse_qs(environ.get('QUERY_STRING', ''))
        as_attachment = 'dl' in query

        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            headers = Headers()
            headers.add_header('Content-Type', 'application/octet-stream')
            if as_attachment:
                headers.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            else:
                headers.add_header('Content-Disposition', f'inline; filename="{filename}"')
            start_response('200 OK', list(headers.items()))
            return [data]
        except Exception as e:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [f"Download error: {str(e)}".encode('utf-8')]

    else:
        return not_found(start_response)

def cli_entry():
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description="Run LAN FileShare via Gunicorn")
    parser.add_argument("--bind", default="127.0.0.1:5000", help="Bind address (host:port)")
    args = parser.parse_args()

    os.environ.setdefault("LFS_USER", "admin")
    os.environ.setdefault("LFS_PASS", "admin")

    try:
        subprocess.run([
            "gunicorn",
            "localfiletransfer.server:app",
            "--bind", args.bind
        ])
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
