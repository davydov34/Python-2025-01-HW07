class Reader:
    def __init__(self, path='', ext=''):
        self.path = path
        self.ext = ext
        self.content = b''
        self.headers= {
            'Content-Type': 'text/plain',
            'Content-Length': 0
        }

    def get_content_type(self):
        match self.ext:
            case '.html':
                self.headers['Content-Type'] = 'text/html'
            case '.css':
                self.headers['Content-Type'] = 'text/css'
            case '.js':
                self.headers['Content-Type'] = 'text/javascript'
            case '.swf':
                self.headers['Content-Type'] = 'application/x-shockwave-flash'
            case '.jpg' | '.jpeg':
                self.headers['Content-Type'] = 'image/jpeg'
            case '.gif':
                self.headers['Content-Type'] = 'image/gif'
            case '.png':
                self.headers['Content-Type'] = 'image/png'

    def read(self):
        try:
            with open(self.path, 'rb') as file:
                self.content = file.read()
                self.get_content_type()
                self.headers['Content-Length'] = self.content.__len__()
        except (PermissionError, FileNotFoundError):
            return 'HTTP/1.0 404 Not Found', dict([('Content-Length', 0)]), b''

        return 'HTTP/1.0 200 OK', self.headers, self.content