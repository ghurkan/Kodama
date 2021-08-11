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

    # Get content length of raw data, it may be different than the header value due to copy-paste of the response
    httpResponseParts = rawResponse.split("\n\n", 1)
    contentLength = len(httpResponseParts[1])

    indexContentLengthHeader = rawResponse.find("Content-Length:")
    if indexContentLengthHeader > -1:
        endContentLengthHeader = rawResponse.find("\n", indexContentLengthHeader)
        parsedContentLength = int(rawResponse[indexContentLengthHeader + 15:endContentLengthHeader])

        if contentLength != parsedContentLength:
            rawResponse = rawResponse[:indexContentLengthHeader] + "Content-Length: " + str(contentLength) + rawResponse[endContentLengthHeader:] 
       

    # Transfer-Encoding breaks the parse if the response is already assembled. So, if the header is present, remove it
    indexTEHeader = rawResponse.find("Transfer-Encoding")
    endOfTEHeader = rawResponse.find("\n", indexTEHeader)
  
    rawResponseChecked = ""
    if indexTEHeader > -1:
        # Transfer Encoding Header found
        indexChunked = rawResponse.find("chunked", indexTEHeader)
        if  indexChunked < endOfTEHeader and indexChunked > -1 :
            # value is chunked, remove the header, replace it with content-length header, https://www.ietf.org/rfc/rfc2616.txt Section 4.4
            rawResponseChecked = rawResponse[:indexTEHeader] + "Content-Length: " + str(contentLength) +  rawResponse[endOfTEHeader:]
        else:
            # value is other than chunked, no changes for now
            rawResponseChecked = rawResponse
    else:
        rawResponseChecked = rawResponse
    

    rawResponseEnc = rawResponseChecked.encode()
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