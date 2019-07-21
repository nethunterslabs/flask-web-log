# Flask-Log
Flask-Log enables request logging for your flask app. It has support for multiple


## Features
The following useful request data is logged (full explanations are in the [Flask docs](https://flask.palletsprojects.com/en/1.0.x/api/#flask.Request)):
- time: Date and Time in ISO 8601 format
- src_ip: Source IP, has support for 'X-Forwarded-For'
- useragent: Client UserAgent
- connection: Connection Type e.g. keep-alive, close
- http_method: HTTP method e.g. GET, POST OPTIONS
- request_scheme: URL scheme (http or https).
- http_status: HTTP status code e.g. 200, 301, 404
- dest_ip: Destination host IP
- dest_port: Destination host port
- url: URL requested
- url_path: URL path requested
- content_type: indicates the media type of the entity-body
- mimetype: similar to content type but without parameters e.g. if the content type is text/HTML; charset=utf-8 the mimetype would be 'text/html'.
- url_query: raw URL query string
- cookies: A dictionary with the contents of all cookies transmitted with the request.
- data: Contains the incoming request data as string in case it came with a mimetype Werkzeug does not handle.
- content_md5: MD5 digest of the entity-body for the purpose of providing an end-to-end message integrity check (MIC) of the entity-body.
- referrer: URL referrer
- authorisation: HTTP basic/digest authorization header
- duration - Request duration from the time the request was received to the time the request was replied to
- request_id: Correlates HTTP requests between the client and server.
- user(remote_user): If the server supports user authentication, and the script is protected, this attribute contains the username the user has authenticated as.


Flask-Log can log requests to the following formats:
- CSV
- JSON
- SQLITE DB
- STDOUT

## Installation

You can install Flask-Log using pip:
```bash
pip install flask_log
```
or directly from source:
```bash
git clone git@github.com:nethunters/flask-log.git
cd flask-log
python setup.py install
```

## Quickstart
Import flask_log and initialise.
```python
from flask_log import Log
Log(app)
```

## Example App
```python
from flask import Flask, request, Response
from flask_log import Log

app = Flask(__name__)
app.config["LOG_TYPE"] = "CSV"
Log(app)


@app.route('/', methods=["GET", "POST"])
def hello():
    return "lets test this log!"


if __name__ == '__main__':
    app.run(debug=True)

```

## Configuration
The following configuration values are used by Flask-Log:

| Config Value  	| Description                                                                                            	|
|---------------	|--------------------------------------------------------------------------------------------------------	|
| LOG_TYPE      	| Format to log out to. Currently supported log formats are: CSV, JSON, STDOUT and SQLITE DB. Defaults to `CSV`. 	|                                                       	|
| LOG_FILENAME  	| The filename, without the file extension, for the log. Defaults to `flask-log`.                        	|
| LOG_LOCATION  	| The directory to log to. Defaults to the current directory.                                            	|

## License
Flask-Log is licensed under the Apache2.0 license. See [License](https://github.com/nethunterslabs/flask-log/blob/master/LICENSE).
