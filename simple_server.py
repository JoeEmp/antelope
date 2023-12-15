import logging
import os
from flask import Flask, request, jsonify

APP = Flask(__name__)
USER_TABLE = [
    {"username": "admin", 'password': '123456'},
]


def request_parse(req_data) -> dict:
    '''解析请求数据并以json形式返回'''
    if req_data.method == 'POST':
        data = req_data.json
    elif req_data.method == 'GET':
        data = req_data.args
    return data


def is_legal_uer(username):
    global USER_TABLE
    return list(filter(lambda x: x['username'] == username, USER_TABLE))


def is_right_password(username, password):
    global USER_TABLE
    return list(filter(lambda x: x['username'] == username and x['password'] == password, USER_TABLE))


@APP.route('/')
def index():
    return '<h1>Hello</h1>'


@APP.route('/login', methods=['POST'])
def login():
    msgs = {
        "success": "login success",
        "pwd_error": "the password is error",
        "not_exist": "user {username} is not exist"
    }
    msg_param = {}
    data = request_parse(request)
    try:
        username, password = data.get('username'), data.get('password')
    except Exception as e:
        print(e)
    if not is_legal_uer(username):
        code, key, msg_param['username'] = 502, 'not_exist', username
    elif is_right_password(username, password):
        logging.info('login success')
        code, key = 200, 'success'
    else:
        logging.info('the password is error')
        code, key = 400, 'pwd_error'
    return jsonify(code=code, msg=msgs[key].format(**msg_param))


@APP.route('/about', methods=['GET', 'POST'])
def about():
    return jsonify(msg='about flask')


if __name__ == "__main__":
    APP.config['JSON_AS_ASCII'] = False
    try:
        APP.run(host='0.0.0.0',
                port=10086,
                debug=True,
                threaded=True
                )
        os.system('lsof -i:10086')
    except Exception as e:
        logging.error(e)
