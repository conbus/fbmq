from fbmq import Page
from config import CONFIG


def after_send(payload):
    print('AFTER_SEND : ' + payload.to_json())

page = Page(CONFIG['FACEBOOK_TOKEN'], after_send=after_send)