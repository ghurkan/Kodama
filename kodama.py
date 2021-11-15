from flask import Flask, request, render_template_string, render_template, redirect, make_response, url_for, flash
from http.client import HTTPResponse, responses
from io import BytesIO
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from pathlib import Path




# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='/')

# set the root path for save uploaded static files
UPLOAD_FOLDER = app.root_path +'\\static'
ALLOWED_EXTENSIONS = {'txt', 'js', 'css', 'jpg', 'jpeg', 'png'}

# set the upload folder for js, css file upload.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        if "content" in request.form:
            content = request.form['content']
            with open("response.txt","w",newline='') as f:
                f.write(content)
            return render_template("index.html")
        if 'file' not in request.files:
            return redirect(request.url)
        elif "file" in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                return render_template("index.html")

@app.route('/result')
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
if __name__ == "__main__":
    app.run(debug=True)  # app.run(host='0.0.0.0') for exposing the server to network


# Notes:

#    response.headers["X-Custom-Header"] = "custom-value"
#    response.headers["Server"] = "kodama"
#    return response
#    response.set_cookie("mycookie2", value="htegergergegf")