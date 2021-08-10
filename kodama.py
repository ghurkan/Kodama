from flask import Flask, request, render_template_string, render_template, make_response
from http.client import HTTPResponse

from io import BytesIO

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

@app.route('/test')
def test():
    return render_template('example.html')


@app.route('/echo')
def echo():
    
    rawResponse = ""
    with open("response.txt") as f:
        rawResponse = f.read()


    rawResponseEnc = rawResponse.encode()
    class FakeSocket():
        def __init__(self, response_bytes):
            self._file = BytesIO(response_bytes)
        def makefile(self, *args, **kwargs):
            return self._file

    source = FakeSocket(rawResponseEnc)
    parsedResponse = HTTPResponse(source)
    parsedResponse.begin()
    parsedResponse_body = parsedResponse.read()
    parsedResponse_headers = parsedResponse.getheaders()
    parsedResponse_status = parsedResponse.status
    parsedResponse.close()
    
    response = make_response(parsedResponse_body)
    response.status_code = parsedResponse_status
    for header in parsedResponse_headers:
        print(header[0] + " " + header[1])
        response.headers[header[0]] = header[1]

    return response


# Set Headers for all responses, overwrite existing ones.
#@app.after_request
#def apply_caching(response):
#    response.headers["X-Custom-Header"] = "custom-value"
#    response.headers["Server"] = "kodama"
#    return response

if __name__ == "__main__":
    app.run()