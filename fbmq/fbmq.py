import json
import requests


def _call_function(name, func, *args, **kwargs):
    if func is None:
        print("there's no %s handler" % name)
    else:
        func(*args, **kwargs)


def handle_webhook(payload, optin=None, message=None, echo=None, delivery=None,
                   postback=None, read=None, account_linking=None):
    data = json.loads(payload)

    # Make sure this is a page subscription
    if data.get("object") != "page":
        print("Webhook failed, only support page subscription")
        return

    # Iterate over each entry
    # There may be multiple if batched
    for entry in data.get("entry"):
        for event in entry.get("messaging"):
            if 'optin' in event:
                _call_function('optin', optin, event)
            elif 'message' in event:
                if event.get("message", {}).get("is_echo"):
                    _call_function('echo', echo, event)
                else:
                    _call_function('message', message, event)
            elif 'delivery' in event:
                _call_function('delivery', delivery, event)
            elif 'postback' in event:
                _call_function('postback', postback, event)
            elif 'read' in event:
                _call_function('read', read, event)
            elif 'account_linking' in event:
                _call_function('account_linking', account_linking, event)
            else:
                print("Webhook received unknown messagingEvent:", event)


class Page(object):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token

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


class Payload(object):
    def __init__(self, recipient, message=None, sender_action=None, notification_type=None):
        self.recipient = recipient
        self.message = message
        self.sender_action = sender_action
        self.notification_type = notification_type

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Recipient(object):
    def __init__(self, id=None, phone_number=None):
        self.id = id
        self.phone_number = phone_number


class Message(object):
    """
    https://developers.facebook.com/docs/messenger-platform/send-api-reference#message
    Message object can contain text, attachment, quick_replies and metadata properties
    """

    def __init__(self, text=None, attachment=None, quick_replies=None, metadata=None):
        self.text = text
        self.attachment = attachment
        self.quick_replies = Message.convert_shortcut_quick_reply(quick_replies)
        self.metadata = metadata

    @staticmethod
    def convert_shortcut_quick_reply(items):
        """
        support shortcut [{'title':'title', 'payload':'payload'}]
        """
        if items is not None and isinstance(items, list):
            result = []
            for item in items:
                if isinstance(item, QuickReply):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(QuickReply(title=item.get('title'), payload=item.get('payload')))
                else:
                    raise ValueError('Invalid quick_replies variables')
            return result
        else:
            return items


class QuickReply(object):
    def __init__(self, title, payload):
        self.title = title
        self.payload = payload
        self.content_type = 'text'
