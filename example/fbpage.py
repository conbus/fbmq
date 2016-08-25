from fbmq import Page
from config import CONFIG

page = Page(CONFIG['FACEBOOK_TOKEN'])


@page.after_send
def after_send(payload, response):
    print('AFTER_SEND : ' + payload.to_json())
    print('RESPONSE : ' + response.text)