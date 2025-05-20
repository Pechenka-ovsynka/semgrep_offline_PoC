import http.server
import socketserver
import os
import json
import re
import ssl
from urllib.parse import urlparse

PORT = 443
DATA_DIR = "responses"
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

os.makedirs(DATA_DIR, exist_ok=True)

class Handler(http.server.BaseHTTPRequestHandler):
    max_requestline = 16384
    
    def _send_response(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_GET(self):
        if self.path.rstrip("/") == "/api/agent/deployments/current":
            self._serve_file_old("deployments_current.json")
        else:
            self._send_response('{"error": "Not Found"}', 404)

    def do_POST(self):
        # Защитное логирование
        print(f"Received POST request to: {self.path}")
        
        # Чтение тела запроса
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        print(f"Request body (truncated): {body[:200]}...")

        # Убедимся, что путь корректный
        path = self.path.rstrip("/")

        # Обработка маршрутов
        if path == "/api/agent/tokens/requests":
            self._serve_file_old("tokens_requests.json")
            return

        elif path == "/api/cli/scans":
            self._serve_file("cli_scans.json")
            return

        elif match := re.match(r"^/api/agent/scans/([^/]+)/results$", path):
            scan_id = match.group(1)
            # Если нужно обработать тело запроса:
            # data = json.loads(body)
            self._serve_file(f"scan_123_results.json")
            return

        elif match := re.match(r"^/api/agent/scans/([^/]+)/complete$", path):
            scan_id = match.group(1)
            self._serve_file_old(f"scan_123_complete.json")
            return

        elif path == "/api/agent/deployments/current":
            self._serve_file_old("deployments_current.json")
            return

        # Если ничего не подошло
        self._send_response('{"error": "Not Found"}', 404)


    def _serve_file_old(self, filename):
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self._send_response(content)
        else:
            self._send_response(json.dumps({"error": f"File {filename} not found"}), 404)

    def _serve_file(self, filename):
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            self._send_response(json.dumps({"error": f"File {filename} not found"}), 404)
            return

        try:
            with open(filepath, "rb") as f:
                content = f.read()
            
            content_length = len(content)

            # Проверяем, что размер файла совпадает с размером прочитанного контента
            fs = os.stat(filepath)
            file_size = fs.st_size
            if content_length != file_size:
                # Логируем или возвращаем ошибку — данные как-то испортились
                self._send_response(json.dumps({
                    "error": "File size mismatch",
                    "file_size": file_size,
                    "content_length": content_length
                }), 500)
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(content_length))
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            self.wfile.write(content)
            print(str(content_length),file_size)
            self.wfile.flush()
        except Exception as e:
            print(f"Error serving file {filename}: {e}")
            self._send_response(json.dumps({"error": "Internal server error"}), 500)








if __name__ == "__main__":
    httpd = socketserver.ThreadingTCPServer(("", PORT), Handler)

    # Обернуть сокет в TLS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving HTTPS on port {PORT}")
    httpd.serve_forever()
