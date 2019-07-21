from collections import OrderedDict
import csv
from datetime import datetime, timezone
import os
import time

from flask import g, request
import jsonpickle
import sqlalchemy as db


def make_new_csv(LOG_FILENAME):
    with open(LOG_FILENAME, 'w') as log_file:
        log_field_names = OrderedDict(
            [("time", None), ("src_ip", None), ("useragent", None),
             ("connection", None), ("http_method", None), ("request_scheme", None),
             ("http_status", None), ("dest_host", None), ("url", None),
             ("url_path", None), ("mimetype", None), ("content_type", None),
             ("url_query", None), ("cookies", None), ("data", None),
             ("referrer", None), ("authorisation", None), ("duration", None),
             ("request_id", None), ("user", None), ("dest_port", None),
             ("content_md5", None)])
        log_file_csv = csv.DictWriter(log_file, fieldnames=log_field_names)
        log_file_csv.writeheader()


def make_new_db(connection, engine, metadata):
    db_log = db.Table('flask_web_log', metadata,
                      db.Column('id', db.Integer()),
                      db.Column('authorisation', db.String()),
                      db.Column('connection', db.String()),
                      db.Column('content_md5', db.String()),
                      db.Column('content_type', db.String()),
                      db.Column('cookies', db.String()),
                      db.Column('data', db.String()),
                      db.Column('dest_host', db.String()),
                      db.Column('dest_port', db.Integer()),
                      db.Column('duration', db.Float()),
                      db.Column('http_method', db.String()),
                      db.Column('http_status', db.Integer()),
                      db.Column('mimetype', db.String()),
                      db.Column('referrer', db.String()),
                      db.Column('request_id', db.String()),
                      db.Column('src_ip', db.String()),
                      db.Column('time', db.String()),
                      db.Column('url', db.String()),
                      db.Column('url_path', db.String()),
                      db.Column('url_query', db.String()),
                      db.Column('user', db.String()),
                      db.Column('useragent', db.String()))
    metadata.create_all(engine)
    return db_log


def write_to_csv(LOG_FILENAME, log_fields):
    with open(LOG_FILENAME, 'r') as init_log_file:
        init_log_file = csv.DictReader(init_log_file)
        log_field_names = init_log_file.fieldnames
    with open(LOG_FILENAME, 'a') as log_file:
        log_file_csv = csv.DictWriter(
            log_file, fieldnames=log_field_names)
        # log_file, fieldnames=log_field_names, extrasaction='ignore')
        log_file_csv.writerow(log_fields)


def write_to_json(LOG_FILENAME, log_fields):
    with open(LOG_FILENAME, 'a') as log_file:
        log_file.write(jsonpickle.encode(log_fields, unpicklable=False) + "\n")


def write_to_db(connection, db_log, engine, log_fields, metadata):
    query = db.insert(db_log)
    values_list = log_fields
    ResultProxy = connection.execute(query, values_list)
    return ResultProxy


class Log(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        config = app.config.copy()
        config.setdefault('LOG_TYPE', "CSV")
        config.setdefault('LOG_FILENAME', "flask-web-log")
        config.setdefault('LOG_LOCATION', "")
        LOG_TYPE = config.get('LOG_TYPE')
        LOG_FILENAME = config.get('LOG_FILENAME')
        LOG_LOCATION = config.get('LOG_LOCATION')
        LOG_FILENAME = os.path.join(LOG_LOCATION, LOG_FILENAME)
        if LOG_TYPE == "CSV":
            LOG_FILENAME = LOG_FILENAME + ".csv"
            if not os.path.isfile(LOG_FILENAME):
                make_new_csv(LOG_FILENAME)
        elif LOG_TYPE == "JSON":
            LOG_FILENAME = LOG_FILENAME + ".json"
        elif LOG_TYPE == "DB":
            LOG_FILENAME = LOG_FILENAME + ".db"
            engine = db.create_engine("sqlite:///" + LOG_FILENAME,
                                      connect_args={'check_same_thread': False})
            connection = engine.connect()
            metadata = db.MetaData()
            if not engine.dialect.has_table(connection, table_name="flask_web_log"):
                db_log = make_new_db(connection, engine, metadata)
            else:
                db_log = db.Table('flask_web_log', metadata,
                                  autoload=True, autoload_with=engine)

        with app.app_context():

            @app.before_request
            def write_log():
                g.start = time.time()

            @app.after_request
            def log_request(response):
                log_fields = OrderedDict()
                log_fields['time'] = datetime.now(
                    timezone.utc).astimezone().isoformat()
                log_fields['src_ip'] = request.headers.get(
                    'X-Forwarded-For', request.remote_addr)
                log_fields['useragent'] = request.user_agent
                log_fields['connection'] = request.headers.get(
                    'Connection')
                log_fields['http_method'] = request.method
                log_fields['request_scheme'] = request.scheme
                log_fields['http_status'] = response.status_code
                log_fields['dest_host'] = request.host.split(':', 1)[0]
                log_fields['url'] = request.url
                log_fields['url_path'] = request.path
                log_fields['mimetype'] = request.mimetype
                log_fields['content_type'] = request.content_type
                log_fields['url_query'] = request.query_string
                log_fields['cookies'] = request.cookies
                log_fields['data'] = request.data
                log_fields['content_md5'] = request.content_md5
                log_fields['referrer'] = request.referrer
                log_fields['authorisation'] = request.authorization
                log_fields['duration'] = time.time() - g.start
                log_fields['request_id'] = request.headers.get(
                    'X-Request-ID') if request.headers.get('X-Request-ID') else ""
                log_fields['user'] = request.remote_user if request.remote_user else ""
                log_fields['dest_port'] = int(request.host.split(':', 1)[1]) if len(
                    request.host.split(':', 1)) == 2 else 80
                if LOG_TYPE == "CSV":
                    write_to_csv(LOG_FILENAME, log_fields)
                elif LOG_TYPE == "JSON":
                    write_to_json(LOG_FILENAME, log_fields)
                elif LOG_TYPE == "DB":
                    log_fields = dict((k, str(v))
                                      for k, v in log_fields.items())
                    write_to_db(connection, db_log, engine,
                                log_fields, metadata)
                elif LOG_TYPE == "STDOUT":
                    log_line_parts = []
                    for log_field_name, log_field_value in log_fields.items():
                        log_line_part = "{}=\"{}\"".format(
                            log_field_name, log_field_value)
                        log_line_parts.append(log_line_part)
                    log_line = ", ".join(log_line_parts)
                    app.logger.info(log_line)
                return response
