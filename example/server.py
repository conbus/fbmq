# coding: utf-8
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from flask import Flask, request, send_from_directory, render_template

import example.messenger
from example.config import CONFIG
from example.fbpage import page

app = Flask(__name__)


@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
                    request.args.get('hub.verify_token', '') == CONFIG['VERIFY_TOKEN']:

        print("Validating webhook")

        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    print(payload)
    page.handle_webhook(payload)

    return "ok"


@app.route('/authorize', methods=['GET'])
def authorize():
    account_linking_token = request.args.get('account_linking_token', '')
    redirect_uri = request.args.get('redirect_uri', '')

    auth_code = '1234567890'

    redirect_uri_success = redirect_uri + "&authorization_code=" + auth_code

    return render_template('authorize.html', data={
        'account_linking_token': account_linking_token,
        'redirect_uri': redirect_uri,
        'redirect_uri_success': redirect_uri_success
    })


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('assets', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
