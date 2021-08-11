# Kodama こだま
Simple server implementation that responds according to HTTP raw response

## Usage

- Install Flask.
<code> pip install Flask </code>
- Edit response.txt with desired HTTP raw response.
- Start the server.
<code> python kodama.py </code>
- Visit http://localhost:5000/echo

## Knowns Issues
- If the response is chunked, it breaks the parsing. Therefore, the response should be given as assembled. Transfer-Encoding header is automatically removed if it exists.
