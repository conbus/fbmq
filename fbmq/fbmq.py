import json
import requests

from .payload import *


class Page(object):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token

    # webhook_handlers contains optin, message, echo, delivery, postback, read, account_linking.
    # these are only set by decorators
    _webhook_handlers = {}

    _quick_reply_callbacks = {}
    _button_callbacks = {}

    def _call_handler(self, name, func, *args, **kwargs):
        if func is not None:
            func(*args, **kwargs)
        elif name in self._webhook_handlers:
            self._webhook_handlers[name](*args, **kwargs)
        else:
            print("there's no %s handler" % name)

    def handle_webhook(self, payload, optin=None, message=None, echo=None, delivery=None,
                       postback=None, read=None, account_linking=None):
        data = json.loads(payload)

        # Make sure this is a page subscription
        if data.get("object") != "page":
            print("Webhook failed, only support page subscription")
            return False

        # Iterate over each entry
        # There may be multiple if batched
        for entry in data.get("entry"):
            for event in entry.get("messaging"):
                if 'optin' in event:
                    self._call_handler('optin', optin, event)
                elif 'message' in event:
                    if event.get("message", {}).get("is_echo"):
                        self._call_handler('echo', echo, event)
                    elif self.is_quick_reply(event) and self.has_quick_reply_callback(event):
                        self.call_quick_reply_callback(event)
                    else:
                        self._call_handler('message', message, event)
                elif 'delivery' in event:
                    self._call_handler('delivery', delivery, event)
                elif 'postback' in event:
                    if self.has_postback_callback(event):
                        self.call_postback_callback(event)
                    else:
                        self._call_handler('postback', postback, event)
                elif 'read' in event:
                    self._call_handler('read', read, event)
                elif 'account_linking' in event:
                    self._call_handler('account_linking', account_linking, event)
                else:
                    print("Webhook received unknown messagingEvent:", event)

    _page_id = None
    _page_name = None

    @property
    def page_id(self):
        if self._page_id is None:
            self._fetch_page_info()

        return self._page_id

    @property
    def page_name(self):
        if self._page_name is None:
            self._fetch_page_info()

        return self._page_name

    def _fetch_page_info(self):
        r = requests.get("https://graph.facebook.com/v2.6/me",
                         params={"access_token": self.page_access_token},
                         headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)
            return

        data = json.loads(r.text)
        if 'id' not in data or 'name' not in data:
            raise ValueError('Could not fetch data : GET /v2.6/me')

        self._page_id = data['id']
        self._page_name = data['name']

    def _send(self, payload):
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                          params={"access_token": self.page_access_token},
                          data=payload.to_json(),
                          headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print(r.text)

    def send(self, recipient_id, message, quick_replies=None, metadata=None):
        text = message if isinstance(message, str) else None
        attachment = message if not isinstance(message, str) else None

        payload = Payload(recipient=Recipient(id=recipient_id),
                          message=Message(text=text,
                                          attachment=attachment,
                                          quick_replies=quick_replies,
                                          metadata=metadata))

        self._send(payload)

    def typing_on(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action='typing_on')

        self._send(payload)

    def typing_off(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action='typing_off')

        self._send(payload)

    def mark_seen(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action='mark_seen')

        self._send(payload)

    """
    decorations
    """

    def handle_optin(self, func):
        self._webhook_handlers['optin'] = func

    def handle_message(self, func):
        self._webhook_handlers['message'] = func

    def handle_echo(self, func):
        self._webhook_handlers['echo'] = func

    def handle_delivery(self, func):
        self._webhook_handlers['delivery'] = func

    def handle_postback(self, func):
        self._webhook_handlers['postback'] = func

    def handle_read(self, func):
        self._webhook_handlers['read'] = func

    def handle_account_linking(self, func):
        self._webhook_handlers['account_linking'] = func

    def callback_quick_reply(self, payloads=None):
        def wrapper(func):
            if payloads is None:
                return func

            for payload in payloads:
                self._quick_reply_callbacks[payload] = func
            return func

        return wrapper

    @staticmethod
    def is_quick_reply(event):
        return event.get("message", {}).get("quick_reply", None) is not None

    def has_quick_reply_callback(self, event):
        payload = event.get("message", {}).get("quick_reply", {}).get('payload', '')
        return payload in self._quick_reply_callbacks

    def call_quick_reply_callback(self, event):
        payload = event.get("message", {}).get("quick_reply", {}).get('payload', '')
        if payload in self._quick_reply_callbacks:
            self._quick_reply_callbacks[payload](payload, event=event)

    def callback_button(self, payloads=None):
        def wrapper(func):
            if payloads is None:
                return func

            for payload in payloads:
                self._button_callbacks[payload] = func
            return func

        return wrapper

    def has_postback_callback(self, event):
        payload = event.get("postback", {}).get("payload", '')
        return payload in self._button_callbacks

    def call_postback_callback(self, event):
        payload = event.get("postback", {}).get("payload", '')
        if payload in self._button_callbacks:
            self._button_callbacks[payload](payload, event=event)
