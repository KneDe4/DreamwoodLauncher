import webview
import http.server
import socketserver
import os
import threading
import time
import random
import urllib
import json
import launcher
import requests

port = 1488
# APPPPPPP
appdata = os.getenv('APPDATA')
dirnul = os.path.join(appdata, ".PiLauncher")
os.makedirs(dirnul, exist_ok=True)

win = None


def read_json():

        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)


# получение гуи
response = requests.get('https://api.pililteam.ru/rawcontent/lanc/')
response.raise_for_status()
html_content = response.text
with open('web/output.html', 'w', encoding='utf-8') as file:
    file.write(html_content)
def write_json(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if path == '/':
            self.serve_file('output.html')

        elif path == '/close':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            if win:
                win.destroy()

        elif path == '/hide':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            if win:
                win.minimize()

        elif path == '/api':
            if 'req' in query_params:
                req = query_params['req'][0]

                if req == 'start':
                    if all(k in query_params for k in ['user', 'min', 'max']):
                        user = query_params['user'][0]
                        min_val = query_params['min'][0]
                        max_val = query_params['max'][0]

                        # сейв пользователя
                        data = read_json()
                        data['username'] = user
                        write_json(data)

                        # запка майна
                        a = False
                        b = False


                        launcher.Minecraft.Start(user, min_val, max_val)

                        self.send_json_response({
                            'status': 'success',
                            'message': 'майн запущен'
                        })
                    else:
                        self.send_json_response({
                            'status': 'error',
                            'message': 'Отсутствуют параметры user, min или max'
                        }, 400)
                else:
                    self.send_json_response({
                        'status': 'error',
                        'message': f'Неизвестная команда: {req}'
                    }, 400)
            else:
                self.send_json_response({
                    'status': 'ok',
                    'params': {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
                })

        elif path == '/username':
            data = read_json()
            username = data.get('username', '')
            self.send_text_response(username)
        elif path == '/proxy':
           if 's' in query_params:
               data =read_json()
               data['proxy'] = query_params['s'][0]
               write_json(data)
               self.send_text_response('OK')
           else:
               data = read_json()
               username = data.get('proxy', '')
               self.send_text_response(username)
        elif path == '/ram':
           if 's' in query_params:
               data =read_json()
               data['ram'] = query_params['s'][0]
               write_json(data)
               self.send_text_response('OK')
           else:
               data = read_json()
               username = data.get('ram', '')
               self.send_text_response(username)
        elif path == '/proxy_set':
           if 's' in query_params:
               data =read_json()
               data['proxy_ip'] = query_params['s'][0]
               write_json(data)
               self.send_text_response('OK')
           else:
               data = read_json()
               username = data.get('proxy_ip', '')
               self.send_text_response(username)


        elif path == '/username_set':
            if 'u' in query_params:
                username = query_params['u'][0]
                data = read_json()
                data['username'] = username
                write_json(data)
                self.send_text_response('OK')
            else:
                self.send_error(400)

        elif path == '/username_l':
            data = read_json()
            username = data.get('username', '')
            result = 'true' if len(username) > 3 else 'false'
            self.send_text_response(result)

        elif os.path.exists(path[1:]):
            self.serve_file(path[1:])
        else:
            self.send_error(404)

    def send_json_response(self, data, status=200):
        content = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')  # фиксанул
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_text_response(self, data, status=200):
        if isinstance(data, str):
            content = data.encode('utf-8')
        else:
            content = str(data).encode('utf-8')

        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def serve_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                content = f.read()


            if filename.endswith('.html'):
                content_type = 'text/html; charset=utf-8'
            elif filename.endswith('.css'):
                content_type = 'text/css; charset=utf-8'
            elif filename.endswith('.js'):
                content_type = 'application/javascript; charset=utf-8'
            elif filename.endswith('.json'):
                content_type = 'application/json; charset=utf-8'
            elif filename.endswith('.txt'):
                content_type = 'text/plain; charset=utf-8'
            elif filename.endswith('.png'):
                content_type = 'image/png'
            elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'application/octet-stream'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            print(f"феил отсуствовааааат: {filename}")
            self.send_error(404)
        except Exception as e:
            print(f"не прочитался этот чувак {filename}: {e}")
            self.send_error(500)


def start_server():
    os.chdir(dirnul)
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"сервер пуск пусе на портике {port}")
        print(f"URL: http://localhost:{port}")
        httpd.serve_forever()


def main():
    global win

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    win = webview.create_window(
        "Dreamwood Launcher",
        f"http://localhost:{port}",
        width=800,
        height=600,
        frameless=True,
        easy_drag=True
    )
    webview.start()


if __name__ == "__main__":
    main()