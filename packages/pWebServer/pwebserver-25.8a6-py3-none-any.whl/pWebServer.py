import sys
import json

try:
    import logging
except ImportError:
    # If logging is not available, we use a mock logging class
    from .MockLogging import logging

# we need this for reimplementing readuntil
MICROPYTHON = sys.version.find('MicroPython') > -1
# Conditional import
if MICROPYTHON:
    import uasyncio as asyncio # type: ignore
    from uasyncio import StreamReader, StreamWriter # type: ignore

    def iscoroutinefunction(fn: callable) -> bool:
        '''Check if a function is a coroutine function

        also note that this is silly because in micropython, coroutines are generators,
        '''
        return str(type(fn)) == "<class 'generator'>"
else:
    import asyncio
    from asyncio import StreamReader, StreamWriter
    from inspect import iscoroutinefunction

logging.basicConfig(level=logging.DEBUG) # type: ignore

class NotFoundError(NotImplementedError):
    pass

class Request:
    '''Parses the request from the client
    '''

    # headers is a list of tuples with the header name and its value

    __slots__ = [
        '_reader',
        '_request',
        '_headers',
        '_query_params',
        '_preserve_body',
        '_body',
        '_standard_methods',
        '_unimplemented_methods',
        'method',
        'path',
        'query_string'
    ]

    _reader: StreamReader
    _request: tuple
    _headers: list
    _query_params: list
    _preserve_body: bool
    _body: str
    _standard_methods: list
    method: str
    path: str
    query_string: str

    def __init__(self, reader:StreamReader, preserve_body = False) -> None:
        self._standard_methods = ['GET','POST','PUT','PATCH','DELETE','CONNECT','OPTIONS','TRACE']
        self._unimplemented_methods = ['PATCH','CONNECT','TRACE']
        self._preserve_body = preserve_body
        self._reader = reader

    # parse the request
    # TODO: store query params
    # TODO: Process form data
    # TODO: Store body
    async def parse(self):
        '''Parse an http request
        '''
        self._request = await self._parse_request(self._reader)
        self.method, self.path, self.query_string = self._request
        self._headers = await self._parse_headers(self._reader)
        self._body = await self._parse_body(self._reader)
        if self._request[0] in ['GET', 'DELETE']:
            if not self._preserve_body:
                logging.debug(f'Request: {self._request} includes a body where none is expected, discarding')
                self._body = ''
            else:
                logging.debug(f'Request: {self._request} includes a body where none is expected, but preserve_body is set')

    async def _readuntil(self, reader: StreamReader, delimiter: bytes = b"\r\n\r\n") -> bytes:
        '''(Private) read until a delimiter is found
        This is a (bad) reimplementation of StreamReader.readuntil for MicroPython

        problem statement: reading bytes from a stream consumes the byte from the stream,
        effectively shifting it off. Each byte then needs to be stored until the delimiter
        is found. We then need to return the bytearray of the bytes read until the delimiter.

        The delimeter also needs to be read and tracked, because if a byte arrives in sequence
        that doesn't matche the delimeter, the count of bytes needs to be reset.

        NOTE: this problem only exists in MicroPython, and only because the stream is consumed
        during reading.

        This also check on each byte as it is read as opposed to reading bytes and checking
        against a growing string every time, which is less efficient.
        '''
        header_block: bytes = b''
        count: int = 0

        while count < len(delimiter):
            bchar: bytes = bytes(await reader.read(1))
            header_block += bchar
            if bchar[0] == delimiter[count]:
                count += 1
            else:
                count = 0
                # (f"match: {count}")
            if count == len(delimiter):
                break

        if count == 0:
            logging.debug("Delimiter not found in request")
            raise asyncio.IncompleteReadError("Delimiter not found in request", 0)
        return header_block

    async def _parse_headers(self, reader: StreamReader) -> list:
        '''(Private) parse request headers
        '''
        # The below reads the incoming request until it hits an empty line
        header_lines: str = await reader.readuntil(b"\r\n\r\n") if not MICROPYTHON else await self._readuntil(reader, b"\r\n\r\n")
        headers: list = []

        for header_line in header_lines.split(b"\r\n"):
            if header_line.decode('utf-8') == "\r\n":
                continue
            try:
                key, value = header_line.decode('utf-8').strip().split(':',1)
                headers.append((key, value))
            except ValueError:
                logging.debug("Discarding empty header value")


        return headers


    async def _parse_request(self, reader: StreamReader = None) -> tuple:
        '''(private) parse request line and determine method, path, and query params
        '''
        if not reader:
            reader = self._reader

        if not reader:
            raise ValueError('No StreamReader supplied')
        logging.debug("parsing request")
        request_bytes = await reader.readline()
        request_line = request_bytes.decode('utf-8')
        logging.debug(f"Request: {request_line}")
        # we should only get the method, the path, and the query string
        method, path, query_string = request_line.replace('?',' ').split(' ', 2)

        if method not in self._standard_methods:
            raise NotImplementedError(f'Method: {method} is not a standard method and not implemented')

        if method in self._unimplemented_methods:
            raise NotImplementedError(f'Method: {method} is not implemented')

        # HTTP encode the spaces in the query string, just in case
        query_string.replace(' ', '%20')

        return (method, path, query_string)

    async def _parse_body(self, reader: StreamReader):
        '''(private) parse body
        '''
        return ''

class Response:
    '''Builds a response to be sent to the client
    '''

    slots = ('_code', '_code_text', '_headers', '_body')

    _code: int
    _code_text: str
    _headers: list[tuple[str, str]]
    _body: str
    _close: bool = True

    def __init__(self, code: int = 200, headers: list = [], body: str = '') -> None:
        if code not in HTTP_CODES.keys():
            raise NotImplementedError(f'HTTP code ({code}) not implemented')

        self._code = code
        self._code_text = HTTP_CODES[int(code)]
        self._headers = headers
        self._body = body

    def add_header(self, header: tuple[str, str]) -> None:
        if not isinstance(header, tuple): # type: ignore
            raise ValueError('Header is not a tuple')

        self._headers.append(header)

    def __str__(self) -> str:
        '''Return text for HTTP response
        '''
        response_line: str = f"HTTP/1.1 {self._code_text}\r\n"
        body: str = ''
        headers: list[tuple[str, str]] = self._headers if self._headers else []

        if self._body != '':
            body = f"\r\n\r\n{self._body}"

        if len(self._headers) == 0:
            headers.append(('Content-Type','text/plain'))
            headers.append(('Content-Length', str(len(self._body))))
        else:
            if 'Content-Type' not in [a[0] for a in self._headers]:
                headers.append(('Content-Type','text/plain'))

        if 'Content-Length' not in [a[0] for a in headers]:
            headers.append(('Content-Length', str(len(self._body))))
        else:
            # find the Cont-Length header and replace it
            new_headers = [(header, value) for header, value in headers if header != 'Content-Length']
            new_headers.append(('Content-Length', str(len(self._body))))
            headers = new_headers

        # if we want to stream, close will be false
        if self._close:
            self.add_header(('Connection', 'close'))

        header_list = [': '.join(h) for h in headers]
        header_text: str = "\r\n".join(header_list)

        return f"{response_line}{header_text}{body}"


class Server:
    '''Handles the actual incoming requests and sends a response
    '''

    __slots__ = ('routes', '_reader', '_writer', '_server')

    routes: list[tuple[str, str, callable]] # type: ignore
    _writer: StreamWriter
    _reader: StreamReader
    _server: asyncio.AbstractServer

    def __init__(self) -> None:
        self.routes = []

    def add_route(self, method: str, path: str, fn: callable) -> None:
        '''Adds a function-based route
        '''
        self.routes.append((method, path, fn))


    # TODO: static route logic necessary
    def static_route(self, path: str, recursive: bool = True) -> None:
        '''Adds a static route - serves direct file content
        '''
        pass


    async def find_route(self, method: str, path:str) -> callable:
        '''Find a route based on method and path

        Returns first matching route
        '''

        # TODO: route logic
        print(self.routes)
        matched_routes = [route for route in self.routes if route[0] == method and route[1] == path]
        if len(matched_routes) == 0:
            raise NotFoundError(f'No route matched {method} {path}')
        else:
            route = matched_routes.pop(0)[2]
        return route


    # get the reader and
    async def create_request(self, reader):
        req = Request()
        req.parse(reader)

    async def send_response(self, res: Response):
        #res.generate(req)
        response_text = str(res).encode()
        logging.debug(f"Sending response: {res._code}")

        self._writer.write(response_text)

        logging.debug(f"Response: {response_text.decode('utf-8')}")
        await self._writer.drain()
        #self._writer.close()
        await self._writer.wait_closed()
        logging.debug(f'Response sent {res._code_text}')

    async def _serve(self, reader, writer):
        '''Find and serve the route
        '''

        self._reader = reader
        self._writer = writer

        req = Request(self._reader)
        # parse the request
        try:
            logging.debug('Parsing request')
            await req.parse()
        except NotImplementedError as not_implemented:
            logging.warn(not_implemented)
            res = Response(code=500, body=not_implemented)
            await self.send_response(res)

        try:
            fn = await self.find_route(req.method, req.path)
            logging.debug(f"Found route for {req.method} {req.path}")

            if not iscoroutinefunction(fn):
                logging.debug(f"Calling route function {fn.__name__} synchronously - this MAY block the event loop")
                res = fn(req)
            else:
                res = await fn(req)

            # Check if the response is a Response object
            if type(res) is not Response:
                raise TypeError(f"Route function {fn.__name__} did not return a Response object")

        # 404 Not Found
        except NotFoundError as nfe:
            logging.warning(f"No route found for {req.method} {req.path}")
            res = Response(code=404)

        # if our function didn't return a Response object return a 500 error
        except TypeError as te:
            logging.error(f"Type error in route function {fn.__name__}: {te}")
            res = Response(code=500, body="Internal Server Error: bad response from route")

        await self.send_response(res)
        await self._server.wait_closed()

        logging.info("Client disconnected")

    def add_default_route(self) -> None:
        async def _default_route(request: Request) -> Response:
            res = Response(body='200 OK')
            return res

        self.add_route('GET', '/', _default_route)

    async def start(self, address: str = "0.0.0.0", port: int = 80):
        '''Start the web server on adddress:port (default any:80)
        '''
        if len(self.routes) == 0:
            raise NotImplementedError('There are no routes implemented')

        self._server = await asyncio.start_server(self._serve, address, port)

HTTP_CODES = {
    200: '200 OK',
    400: '400 Bad Request',
    401: '401 Unauthorized',
    403: '403 Forbidden',
    404: '404 Not Found',
    500: '500 Internal Server Error',
    503: '503 Service Unavailable'
}
