from fbmq import Page
from config import CONFIG


def after_send(payload, response):
    print('AFTER_SEND : ' + payload.to_json())
    print('RESPONSE : ' + response.text)

page = Page(CONFIG['FACEBOOK_TOKEN'], after_send=after_send)