import json
import re
import requests

from .payload import *


# I agree with him : http://stackoverflow.com/a/36937/3843242
class NotificationType:
    REGULAR = 'REGULAR'
    SILENT_PUSH = 'SILENT_PUSH'
    NO_PUSH = 'NO_PUSH'


class SenderAction:
    TYPING_ON='typing_on'
    TYPING_OFF='typing_off'
    MARK_SEEN='mark_seen'


class Event(object):
    def __init__(self, messaging=None):
        if messaging is None:
            messaging = {}

        self.messaging = messaging
        self.matched_callbacks = []

    @property
    def sender_id(self):
        return self.messaging.get("sender", {}).get("id", None)

    @property
    def recipient_id(self):
        return self.messaging.get("recipient", {}).get("id", None)

    @property
    def timestamp(self):
        return self.messaging.get("timestamp", None)

    @property
    def message(self):
        return self.messaging.get("message", {})

    @property
    def message_text(self):
        return self.message.get("text", None)

    @property
    def message_attachments(self):
        return self.message.get("attachments", [])

    @property
    def quick_reply(self):
        return self.messaging.get("message", {}).get("quick_reply", {})

    @property
    def postback(self):
        return self.messaging.get("postback", {})

    @property
    def optin(self):
        return self.messaging.get("optin", {})

    @property
    def account_linking(self):
        return self.messaging.get("account_linking", {})

    @property
    def delivery(self):
        return self.messaging.get("delivery", {})

    @property
    def read(self):
        return self.messaging.get("read", {})

    @property
    def message_mid(self):
        return self.messaging.get("message", {}).get("mid", None)

    @property
    def message_seq(self):
        return self.messaging.get("message", {}).get("seq", None)

    @property
    def is_optin(self):
        return 'optin' in self.messaging

    @property
    def is_message(self):
        return 'message' in self.messaging

    @property
    def is_text_message(self):
        return self.messaging.get("message", {}).get("text", None) is not None

    @property
    def is_attachment_message(self):
        return self.messaging.get("message", {}).get("attachments", None) is not None

    @property
    def is_echo(self):
        return self.messaging.get("message", {}).get("is_echo", None) is not None

    @property
    def is_delivery(self):
        return 'delivery' in self.messaging

    @property
    def is_postback(self):
        return 'postback' in self.messaging

    @property
    def is_read(self):
        return 'read' in self.messaging

    @property
    def is_account_linking(self):
        return 'account_linking' in self.messaging

    @property
    def is_quick_reply(self):
        return self.messaging.get("message", {}).get("quick_reply", None) is not None

    @property
    def quick_reply_payload(self):
        return self.messaging.get("message", {}).get("quick_reply", {}).get("payload", '')

    @property
    def postback_payload(self):
        return self.messaging.get("postback", {}).get("payload", '')


class Page(object):
    def __init__(self, page_access_token, **options):
        self.page_access_token = page_access_token
        self._after_send = options.pop('after_send', None)
        self._page_id = None
        self._page_name = None

    # webhook_handlers contains optin, message, echo, delivery, postback, read, account_linking.
    # these are only set by decorators
    _webhook_handlers = {}

    _quick_reply_callbacks = {}
    _button_callbacks = {}

    _quick_reply_callbacks_key_regex = {}
    _button_callbacks_key_regex = {}

    _after_send = None

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
        def get_events(data):
            for entry in data.get("entry"):
                for messaging in entry.get("messaging"):
                    event = Event(messaging)
                    yield event

        for event in get_events(data):
            if event.is_optin:
                self._call_handler('optin', optin, event)
            elif event.is_echo:
                self._call_handler('echo', echo, event)
            elif event.is_quick_reply:
                event.matched_callbacks = self.get_quick_reply_callbacks(event)
                self._call_handler('message', message, event)
                for callback in event.matched_callbacks:
                    callback(event.quick_reply_payload, event)
            elif event.is_message and not event.is_echo and not event.is_quick_reply:
                self._call_handler('message', message, event)
            elif event.is_delivery:
                self._call_handler('delivery', delivery, event)
            elif event.is_postback:
                event.matched_callbacks = self.get_postback_callbacks(event)
                self._call_handler('postback', postback, event)
                for callback in event.matched_callbacks:
                    callback(event.postback_payload, event)
            elif event.is_read:
                self._call_handler('read', read, event)
            elif event.is_account_linking:
                self._call_handler('account_linking', account_linking, event)
            else:
                print("Webhook received unknown messagingEvent:", event)

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

    def _send(self, payload, callback=None):
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                          params={"access_token": self.page_access_token},
                          data=payload.to_json(),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)

        if callback is not None:
            callback(payload, r)

        if self._after_send is not None:
            self._after_send(payload, r)

    def send(self, recipient_id, message, quick_replies=None, metadata=None,
             notification_type=None, callback=None):
        text = message if isinstance(message, str) else None
        attachment = message if not isinstance(message, str) else None

        payload = Payload(recipient=Recipient(id=recipient_id),
                          message=Message(text=text,
                                          attachment=attachment,
                                          quick_replies=quick_replies,
                                          metadata=metadata),
                          notification_type=notification_type)

        self._send(payload, callback=callback)

    def typing_on(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action=SenderAction.TYPING_ON)

        self._send(payload)

    def typing_off(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action=SenderAction.TYPING_OFF)

        self._send(payload)

    def mark_seen(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action=SenderAction.MARK_SEEN)

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

    def after_send(self, func):
        self._after_send = func

    def callback_quick_reply(self, payloads=None):
        def wrapper(func):
            if payloads is None:
                return func

            for payload in payloads:
                self._quick_reply_callbacks[payload] = func
            return func

        return wrapper

    def get_quick_reply_callbacks(self, event):
        callbacks = []
        for key in self._quick_reply_callbacks.keys():
            if key not in self._quick_reply_callbacks_key_regex:
                self._quick_reply_callbacks_key_regex[key] = re.compile(key + '$')

            if self._quick_reply_callbacks_key_regex[key].match(event.quick_reply_payload):
                callbacks.append(self._quick_reply_callbacks[key])

        return callbacks

    def callback_button(self, payloads=None):
        def wrapper(func):
            if payloads is None:
                return func

            for payload in payloads:
                self._button_callbacks[payload] = func
            return func

        return wrapper

    def get_postback_callbacks(self, event):
        callbacks = []
        for key in self._button_callbacks.keys():
            if key not in self._button_callbacks_key_regex:
                self._button_callbacks_key_regex[key] = re.compile(key + '$')

            if self._button_callbacks_key_regex[key].match(event.postback_payload):
                callbacks.append(self._button_callbacks[key])

        return callbacks
