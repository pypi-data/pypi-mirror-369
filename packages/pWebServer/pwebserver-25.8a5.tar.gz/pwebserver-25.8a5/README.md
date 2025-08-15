# pWebServer
Small, asynchronous web server for use with Raspberry Pi Pico W boards and similar

## Background
I wanted something small and reusable to work with my raspberry pi pico w and didn't find anything in the wild.
This is a work in progress, but I intend for it to be stable for at least my own use.

## Notes
This library is not designed to be particularly fast, however it is intended to be easy to use.

### HTTP Methods
Self-defined methods are not currently supported. PATCH, CONNECT, and TRACE are also not implmented

### Paths
Simple paths are supported. Complex path matching is not supported.

For example, in some frameworks you might be able to define a path as
```
/some/path/to/:id
```
And that would populate the id property or some other variable with the value, for pWebServer that is not the case.

For dynamic data use query strings

**Example (micropython - if installed with mip):**
```py
from pWebServer.pWebServer import Server
import uasyncio as asyncio

sv = Server()
sv.add_default_route() # simply adds a route at / that returns 200 OK
loop = asyncio.get_event_loop()
loop.create_task(sv.start()) # Start serving for 0.0.0.0 (all ipv4 ips) on port 80
loop.run_forever()
```

## Requirements

python >=3.11 or micropython >=1.20

## installing

### python (with pypi)

```sh
pip install pWebServer
```

### micropython (with mip & url)

Using repl:
```py
import mip
mip.install("github:sjsadowski/pWebServer", version="latest")
```

Using mpremote:
```sh
mpremote mip install github:sjsadowski/pWebServer
```

## Dependencies

### MicroPython
MicroPython does not ship with the full set of Python Standard Libraries. For information about this, check the [micropython-lib GitHub repo](https://github.com/micropython/micropython-lib) .

- logging

### Python

** None **

### Development
    - pytest >= 7.4.0
    - pytest-asyncio >= 0.21.0
    - httpx >= 0.24.1

## To Do:
- Cookie support
- POST/PUT data support
- HTTP/2.0(?)
- Better test coverage