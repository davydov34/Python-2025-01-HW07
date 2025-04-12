import getopt, sys
import os
from datetime import datetime as dt, timezone as tz
from urllib.parse import unquote
import multiprocessing as mp
import socket, select

from filereader import Reader

HOST, PORT = '', 80
SERVER_NAME = 'OTUS_HTTP_Server'


# Построитель ответа
class Builder_response:
    def __init__(self):
        self.status = "HTTP/1.0 400 Bad Request"
        self.headers = {
            'Date': dt.now(tz=tz.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Content-Length': 0,
            'charset': 'UTF-8',
            'Server': SERVER_NAME,
            'Connection': 'close',
        }
        self.body = b''

    def build_response(self):
        headers = '\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()])
        return f'{self.status}\r\n{headers}\r\n\r\n'.encode('utf-8') + self.body


class HTTP_Worker:
    def __init__(self, root_dir: str):
        self.root_path = os.path.abspath(root_dir)

    def content_handler(self, source_path: str) ->  (str, dict, bytes):
        path = unquote(source_path)
        full_path = os.path.abspath(os.path.join(self.root_path, path.lstrip('/'))).split('?')[0]
        if not self.root_path in full_path: #Если путь из запроса не содержит корневую директорию
           return 'HTTP/1.0 403 Forbidden', {}, b''

        if path.split('/')[-1]: # Если запращивается файл
            ext = os.path.splitext(full_path)[1]
            ctx = Reader(path=full_path, ext=ext)
            return ctx.read()
        else:  # Или запрашивается директория - ищем index.html
            if os.path.exists(os.path.join(full_path, 'index.html')):
                ctx = Reader(path=os.path.join(full_path, 'index.html'), ext='.html')
                return ctx.read()
            else:
                return 'HTTP/1.0 404 Not Found', {}, b''

    def connect_handler(self, worker_socket: socket):
        client_socket = worker_socket.recv(1024)
        server_response = Builder_response()
        if client_socket:
            http_method: str = ''
            path: str = ''
            request = client_socket.decode('utf-8').splitlines() # Получаем данные из сокета
            try:
                http_method, path, protocol = request[0].split()  #Получаем первую строку запроса, содержащей метод, путь и протокол
            except ValueError:
                pass

            if http_method in ['HEAD', 'GET']:  # Если метод содержит GET или HEAD
               server_response.status, headers, body = self.content_handler(path)
               for key, value in headers.items():
                   server_response.headers[key] = value
               if http_method == 'GET':
                  server_response.body = body

            elif not http_method: #Если что-то отличное - возвращаем 405
                server_response.status = 'HTTP/1.0 405 Method Not Allowed'
                server_response.headers['Allow'] = 'HEAD, GET'

        worker_socket.send(server_response.build_response())
        worker_socket.shutdown(socket.SHUT_WR)
        worker_socket.close()


def main(document_root: str, socket_client: socket):
    try:
        worker = HTTP_Worker(document_root)
        worker.connect_handler(socket_client)
    except KeyboardInterrupt:
        pass


    ### -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
if __name__ == "__main__":
    params = {'-w': 4, '-r': 'www'}
    argumentList = sys.argv[1:]

    try:
        optlist, args = getopt.getopt(argumentList, 'r:w:')
        for key, value in optlist:
            params[key] = value
    except getopt.error as err:
        print(err)

    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as srv_socket:
        srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv_socket.bind((HOST, PORT))
        srv_socket.listen(10)
        inputs = [srv_socket]
        outputs = []
        with mp.Pool(processes=int(params['-w'])) as pool:
            while True:
                try:
                    conn, address = srv_socket.accept()
                    pool.apply_async(main, args=(params['-r'], conn))
                except KeyboardInterrupt:
                    pool.terminate()
                    break