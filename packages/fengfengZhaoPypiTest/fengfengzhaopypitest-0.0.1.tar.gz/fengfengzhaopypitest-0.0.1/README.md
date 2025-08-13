
> This is a test project, upload the user test package to pypi

## Project description
myWeb is an extremely simple but WSGI-compliant web application framework. myWeb uses decorators to register routes, not only supports static routes, but also supports dynamic route resolution. You can make it follow the parameters directly in the url.


## Installing
Install using pip

```bash
pip3 install -i https://test.pypi.org/simple/ JuejinPdudoProject
```

## Simple static routing case
code:
```python
from JuejinPdudoSampleWeb import myWeb

@myWeb.routes(path="/index",methods="all")
def index(r):
    return "hello world\n"

def main():
    myWeb.run("",8888)


if __name__ == '__main__':
    main()
```

tests:
```bash
pdudo$ curl -v 127.0.0.1:8888/index
*   Trying 127.0.0.1:8888...
* Connected to 127.0.0.1 (127.0.0.1) port 8888 (#0)
> GET /index HTTP/1.1
> Host: 127.0.0.1:8888
> User-Agent: curl/7.81.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Date: Sat, 06 May 2023 06:21:17 GMT
< Server: WSGIServer/0.2 CPython/3.11.0
< Content-Length: 12
<
hello world
* Closing connection 0
pdudo$
```


## Simple Dynamic Routing Case
```python
from JuejinPdudoSampleWeb import myWeb

@myWeb.routes(path="/hello/{name}",methods="all",regular=True)
def hello(r):
    name = r.regular[0]
    return "hello %s\n" % (name)


def main():
    myWeb.run("",8888)


if __name__ == '__main__':
    main()
```

tests:
```bash
pdudo$ curl -v 127.0.0.1:8888/hello/pdudo
*   Trying 127.0.0.1:8888...
* Connected to 127.0.0.1 (127.0.0.1) port 8888 (#0)
> GET /hello/pdudo HTTP/1.1
> Host: 127.0.0.1:8888
> User-Agent: curl/7.81.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Date: Sat, 06 May 2023 06:22:11 GMT
< Server: WSGIServer/0.2 CPython/3.11.0
< Content-Length: 12
<
hello pdudo
* Closing connection 0
pdudo$
```

### End
Good luck with your use.
