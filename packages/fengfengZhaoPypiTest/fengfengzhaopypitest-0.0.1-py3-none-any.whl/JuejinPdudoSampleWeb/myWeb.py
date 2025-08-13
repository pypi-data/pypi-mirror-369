
import re
import wsgiref.simple_server
import time
import base64

mapGetRoute = {}
mapPostRoute = {}
mapGetRegularRouting = {}
mapPostRegularRouting = {}

reFindall = re.compile(r"\{(.*?)\}")
reSubAll = re.compile(r"\{.*?\}")

http_code = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout"
}

class response():
    def __init__(self,environ):
        self.response = environ
        self.headers = {}
        self.httpcode = 200
        self.regular = ()

    def set_headers(self,key,val):
        if key and val:
            self.headers[key] = val
        else:
            raise ValueError("set header , Key or val is empty")

    def status_code(self,code):
        self.httpcode = code

    def get_cookie(self):
        return self.response["HTTP_COOKIE"]

    def set_cookie(self,key,value,expires=time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime()),maxage=3600,path="/",domain=".",secure="None"):
        if key and value:
            self.set_headers("Set-Cookie","%s=%s; Expires=%s; Max-Age=%d; Path=%s; Domain=%s; Secure; %s" %(key,value,expires,maxage,path,domain,secure))
        else:
            raise ValueError("set_cookie error , key or value is empty")

    def basicAuth(self):
        if "HTTP_AUTHORIZATION" not in self.response:
            return None,None,"HTTP_AUTHORIZATION request header not found"
        else:
            originalVal = self.response["HTTP_AUTHORIZATION"]
            types = originalVal.split(" ")[0]
            values = originalVal.split(" ")[1]
            if types == "Basic":
                userAndPasswd = base64.b64decode(values).decode()
                user = userAndPasswd.split(":")[0]
                passwd = userAndPasswd.split(":")[1]
                return user,passwd,None
            else:
                return None, None, "HTTP_AUTHORIZATION request error,unrecognized type: %s " %(types)

class routes():
    def __init__(self, *args,**kwargs):
        path = kwargs["path"]
        methods = kwargs["methods"]
        self.path = path
        self.methods = methods

        # 正则路由
        if "regular".lower() in kwargs:
            self.re = kwargs["regular"]
        else:
            self.re = False

    def __call__(self, func):

        regular = ""
        if self.re == True:
            parameter = re.findall(reFindall,self.path)
            reText = re.sub(reSubAll,"(.*?)",self.path)
            reText = f"{reText}$"
            regular = {
                "original": self.path,
                "reText": reText,
                "parameter": parameter,
                "func": func
            }

        if str(self.methods).upper() == "POST":
            if self.re:
                mapPostRegularRouting[regular["reText"]] = regular
            else:
                mapPostRoute[self.path] = func
        elif str(self.methods).upper() == "GET":
            if self.re:
                mapGetRegularRouting[regular["reText"]] = regular
            else:
                mapGetRoute[self.path] = func
        elif str(self.methods).upper() == "ALL":
            if self.re:
                mapPostRegularRouting[regular["reText"]] = regular
                mapGetRegularRouting[regular["reText"]] = regular
            else:
                mapPostRoute[self.path] = func
                mapGetRoute[self.path] = func

        def wrapper(*args, **kwargs):
            result = func(*args,**kwargs)
            return result
        return wrapper

@routes(path="/*",methods="all")
def NotFound(response):
    response.status_code(404)
    return "Not Found"

def application(environ, start_response):
    path = environ['PATH_INFO']
    method = environ["REQUEST_METHOD"]

    RegularRouting = {}
    Route = {}
    isRegular = False

    if method == "GET":
        Route = mapGetRoute
        RegularRouting = mapGetRegularRouting
    elif method == "POST":
        Route = mapPostRoute
        RegularRouting = mapPostRegularRouting

    if path in Route:
        func = Route[path]
    else:
        for key in RegularRouting.keys():
            if re.match(key, path):
                isRegular = True
                collText = re.findall(key, path)
                func = RegularRouting[key]["func"]
                break
        else:
            func = Route["/*"]

    r = response(environ)

    if isRegular:
        # body = func(r,collText)
        r.regular = collText
    # else:
    #     body = func(r)

    body = func(r)
    if body is None:
        body = ""

    code = r.httpcode
    if code not in http_code:
        status = "%d" % (code)
    else:
        status = "%d %s" % (code, http_code[code])

    # headers = [("Content-type", "text/html"), ("Server", "pdudo_web_sites")]
    headers = [(key,val) for key , val in r.headers.items()]

    start_response(status, headers)
    return [body.encode()]

def run(host,port):
    print("web server is starting,listening address: " , host, "port: " , port)
    try:
        s = wsgiref.simple_server.make_server(host, port, application)
        s.serve_forever()
    except Exception as e:
        print("Server failed to start , error: " , e , "listening address: " , host, "port: " , port)
