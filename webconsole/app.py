import select
import threading
import uuid

import flask
import paramiko
import logging
from flask_sse import sse

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(sse, url_prefix='/stream')


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/run', methods=['POST'])
def run_command():
    form = flask.request.form
    host = form['host']
    username = form['username']
    password = form['password']
    command = form['command']
    uid = uuid.uuid4().hex
    th = threading.Thread(
        target=flask.copy_current_request_context(do_run_command),
        args=(host, username, password, command, uid))
    th.start()
    return {'uid': uid}


def do_run_command(host, username, password, command, key):
    client = paramiko.SSHClient()
    hostname, port = host.split(':')
    client.load_system_host_keys()
    try:
        client.connect(hostname, port, username, password)
        stdin, stdout, stderr = client.exec_command(command)
        channel = stdout.channel
        pending = err_pending = None
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
            readq, _, _ = select.select([channel], [], [], 1)
            for c in readq:
                if c.recv_ready():
                    chunk = c.recv(len(c.in_buffer))
                    if pending is not None:
                        chunk = pending + chunk
                    lines = chunk.splitlines()
                    if lines and lines[-1] and lines[-1][-1] == chunk[-1]:
                        pending = lines.pop()
                    else:
                        pending = None
                    [push_log(line.decode(), key) for line in lines]
                if c.recv_stderr_ready():
                    chunk = c.recv_stderr(len(c.in_stderr_buffer))
                    if err_pending is not None:
                        chunk = err_pending + chunk
                    lines = chunk.splitlines()
                    if lines and lines[-1] and lines[-1][-1] == chunk[-1]:
                        err_pending = lines.pop()
                    else:
                        err_pending = None
                    [push_log(line.decode(), key) for line in lines]
    finally:
        client.close()


def push_log(message, channel):
    sse.publish({'message': message}, 'message', channel=channel)
