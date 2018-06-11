import sys
import re
import requests

from .payload import *
from .template import *
from .events import *


# See https://developers.facebook.com/docs/graph-api/changelog
SUPPORTED_API_VERS=[
    "v2.11",
    "v2.10",
    "v2.9",
    "v2.8",
    "v2.7",
    "v2.6",
]

# See https://developers.facebook.com/docs/messenger-platform/messenger-profile/supported-locales
SUPPORTED_LOCALES=[
    "default",
    "en_US",
    "ca_ES",
    "cs_CZ",
    "cx_PH",
    "cy_GB",
    "da_DK",
    "de_DE",
    "eu_ES",
    "en_UD",
    "es_LA",
    "es_ES",
    "gn_PY",
    "fi_FI",
    "fr_FR",
    "gl_ES",
    "hu_HU",
    "it_IT",
    "ja_JP",
    "ko_KR",
    "nb_NO",
    "nn_NO",
    "nl_NL",
    "fy_NL",
    "pl_PL",
    "pt_BR",
    "pt_PT",
    "ro_RO",
    "ru_RU",
    "sk_SK",
    "sl_SI",
    "sv_SE",
    "th_TH",
    "tr_TR",
    "ku_TR",
    "zh_CN",
    "zh_HK",
    "zh_TW",
    "af_ZA",
    "sq_AL",
    "hy_AM",
    "az_AZ",
    "be_BY",
    "bn_IN",
    "bs_BA",
    "bg_BG",
    "hr_HR",
    "nl_BE",
    "en_GB",
    "et_EE",
    "fo_FO",
    "fr_CA",
    "ka_GE",
    "el_GR",
    "gu_IN",
    "hi_IN",
    "is_IS",
    "id_ID",
    "ga_IE",
    "jv_ID",
    "kn_IN",
    "kk_KZ",
    "lv_LV",
    "lt_LT",
    "mk_MK",
    "mg_MG",
    "ms_MY",
    "mt_MT",
    "mr_IN",
    "mn_MN",
    "ne_NP",
    "pa_IN",
    "sr_RS",
    "so_SO",
    "sw_KE",
    "tl_PH",
    "ta_IN",
    "te_IN",
    "ml_IN",
    "uk_UA",
    "uz_UZ",
    "vi_VN",
    "km_KH",
    "tg_TJ",
    "ar_AR",
    "he_IL",
    "ur_PK",
    "fa_IR",
    "ps_AF",
    "my_MM",
    "qz_MM",
    "or_IN",
    "si_LK",
    "rw_RW",
    "cb_IQ",
    "ha_NG",
    "ja_KS",
    "br_FR",
    "tz_MA",
    "co_FR",
    "as_IN",
    "ff_NG",
    "sc_IT",
    "sz_PL",
]


class LocalizedObj():
    def __init__(self, locale, obj):
        if locale not in SUPPORTED_LOCALES:
            raise ValueError("Unsupported locale: {}".format(locale))
        if not obj:
            raise ValueError("Object is mandatory")
        self.locale = locale
        self.obj = obj


# I agree with him : http://stackoverflow.com/a/36937/3843242
class NotificationType:
    REGULAR = 'REGULAR'
    SILENT_PUSH = 'SILENT_PUSH'
    NO_PUSH = 'NO_PUSH'


class SenderAction:
    TYPING_ON = 'typing_on'
    TYPING_OFF = 'typing_off'
    MARK_SEEN = 'mark_seen'


def event_parser(messaging=None):
    if messaging is None:
        messaging = dict()

    if 'message' in messaging:
        is_echo = messaging.get('message', {}).get('is_echo')
        if is_echo:
            event_type = EchoEvent
        else:
            event_type = MessageEvent
    elif 'delivery' in messaging:
        event_type = DeliveriesEvent
    elif 'read' in messaging:
        event_type = ReadEvent.new_from_json_dict(messaging)
    elif 'account_linking' in messaging:
        event_type = AccountLinkingEvent
    elif 'checkout_update' in messaging:
        event_type = CheckOutUpdateEvent
    elif 'game_play' in messaging:
        event_type = GamePlayEvent.new_from_json_dict(messaging)
    elif 'pass_thread_control' in messaging:
        event_type = PassThreadEvent
    elif 'take_thread_control' in messaging:
        event_type = TakeThreadEvent
    elif 'request_thread_control' in messaging:
        event_type = RequestThreadEvent
    elif 'app_roles' in messaging:
        event_type = AppRoleEvent
    elif 'optin' in messaging:
        event_type = OptinEvent
    elif 'payment' in messaging:
        event_type = PaymentEvent
    elif 'policy-enforcement' in messaging:
        # key name must be changed for properly use to class instance.
        messaging['policy_enforcement'] = messaging['policy-enforcement']
        del messaging['policy-enforcement']
        event_type = PolicyEnforcementEvent
    elif 'postback' in messaging:
        event_type = PostBackEvent
    elif 'referral' in messaging:
        event_type = ReferralEvent
    else:
        print("Webhook received unknown messaging")
        return
    event = event_type.new_from_json_dict(messaging)

    return event



class Page(object):
    def __init__(self, page_access_token, **options):
        self.page_access_token = page_access_token
        self._after_send = options.pop('after_send', None)
        self._api_ver = options.pop('api_ver', 'v2.6')
        if self._api_ver not in SUPPORTED_API_VERS:
            raise ValueError('Unsupported API Version : ' + self._api_ver)
        self._page_id = None
        self._page_name = None

    WEBHOOK_ENDPOINTS = ['optin', 'message', 'echo', 'delivery', 'postback', 'read', 'account_linking', 'referral']

    # these are set by decorators or the 'set_webhook_handler' method
    _webhook_handlers = {}

    _quick_reply_callbacks = {}
    _button_callbacks = {}

    _quick_reply_callbacks_key_regex = {}
    _button_callbacks_key_regex = {}

    _after_send = None

    def _api_uri(self, sub):
        return "https://graph.facebook.com/" + self._api_ver + "/" + sub

    def _call_handler(self, name, func, *args, **kwargs):
        if func is not None:
            func(*args, **kwargs)
        elif name in self._webhook_handlers:
            self._webhook_handlers[name](*args, **kwargs)
        else:
            print("there's no %s handler" % name)

    def handle_webhook(self, payload, optin=None, message=None, echo=None, delivery=None,
                       postback=None, read=None, account_linking=None, referral=None,
                       game_play=None, pass_thread_control=None, take_thread_control=None,
                       request_thread_control=None, app_roles=None, policy_enforcement=None,
                       checkout_update=None, payment=None):
        data = json.loads(payload)

        # Make sure this is a page subscription
        if data.get("object") != "page":
            print("Webhook failed, only support page subscription")
            return False

        # Iterate over each entry
        # There may be multiple if batched
        def get_events(data):
            for entry in data.get("entry"):
                messagings = entry.get("messaging")
                if not messagings:
                    print("Webhook received unsupported Entry:", entry)
                    continue
                for messaging in messagings:
                    event = event_parser(messaging)
                    yield event

        for event in get_events(data):
            if isinstance(event, OptinEvent):
                self._call_handler('optin', optin, event)
            elif isinstance(event, EchoEvent):
                self._call_handler('echo', echo, event)
            elif isinstance(event, MessageEvent):
                self._call_handler('message', message, event)
                if event.is_quick_reply:
                    matched_callbacks = self.get_quick_reply_callbacks(event)
                    for callback in matched_callbacks:
                        callback(event.quick_reply_payload, event)
            elif isinstance(event, DeliveriesEvent):
                self._call_handler('delivery', delivery, event)
            elif isinstance(event, PostBackEvent):
                matched_callbacks = self.get_postback_callbacks(event)
                self._call_handler('postback', postback, event)
                for callback in matched_callbacks:
                    callback(event.payload, event)
            elif isinstance(event, ReadEvent):
                self._call_handler('read', read, event)
            elif isinstance(event, AccountLinkingEvent):
                self._call_handler('account_linking', account_linking, event)
            elif isinstance(event, ReferralEvent):
                self._call_handler('referral', referral, event)

            elif isinstance(event, GamePlayEvent):
                self._call_handler('game_play', game_play, event)
            elif isinstance(event, PassThreadEvent):
                self._call_handler('pass_thread_control', pass_thread_control, event)
            elif isinstance(event, TakeThreadEvent):
                self._call_handler('take_thread_control', take_thread_control, event)
            elif isinstance(event, RequestThreadEvent):
                self._call_handler('request_thread_control', request_thread_control, event)
            elif isinstance(event, AppRoleEvent):
                self._call_handler('app_roles', app_roles, event)
            elif isinstance(event, PolicyEnforcementEvent):
                self._call_handler('policy_enforcement', policy_enforcement, event)
            elif isinstance(event ,CheckOutUpdateEvent):
                self._call_handler('checkout_update', checkout_update, event)
            elif isinstance(event, PaymentEvent):
                self._call_handler('payment', payment, event)
            else:
                print("Webhook received unknown messaging Event:", event)

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
        r = requests.get(self._api_uri("me"),
                         params={"access_token": self.page_access_token},
                         headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)
            return

        data = json.loads(r.text)
        if 'id' not in data or 'name' not in data:
            raise ValueError('Could not fetch data : GET /' + self._api_ver +
                             '/me')

        self._page_id = data['id']
        self._page_name = data['name']

    def get_user_profile(self, fb_user_id):
        r = requests.get(self._api_uri(fb_user_id),
                         params={"access_token": self.page_access_token},
                         headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)
            return

        return json.loads(r.text)

    def get_messenger_code(self, ref=None, image_size=1000):
        d = {}
        d['type']='standard'
        d['image_size'] = image_size
        if ref:
            d['data'] = {'ref': ref}

        r = requests.post(self._api_uri("me/messenger_codes"),
                          params={"access_token": self.page_access_token},
                          json=d,
                          headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print(r.text)
            return None

        data = json.loads(r.text)
        if 'uri' not in data:
            raise ValueError('Could not fetch messener code : GET /' +
                             self._api_ver + '/me')

        return data['uri']

    def _send(self, payload, callback=None):
        r = requests.post(self._api_uri("me/messages"),
                          params={"access_token": self.page_access_token},
                          data=payload.to_json(),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)

        if callback is not None:
            callback(payload, r)

        if self._after_send is not None:
            self._after_send(payload, r)

        return r

    def send(self, recipient_id, message, quick_replies=None, metadata=None,
             notification_type=None, callback=None, tag=None):
        if sys.version_info >= (3, 0):
            text = message if isinstance(message, str) else None
        else:
            text = message if isinstance(message, str) else message.encode('utf-8') if isinstance(message, unicode) else None

        attachment = message if not text else None

        payload = Payload(recipient=Recipient(id=recipient_id),
                          message=Message(text=text,
                                          attachment=attachment,
                                          quick_replies=quick_replies,
                                          metadata=metadata),
                          notification_type=notification_type,
                          tag=tag)

        return self._send(payload, callback=callback)

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
    messenger profile (see https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api)
    """

    def _set_profile_property(self, pname, pval):
        r = requests.post(self._api_uri("me/messenger_profile"),
                          params={"access_token": self.page_access_token},
                          data=json.dumps({
                              pname: pval
                          }),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)

    def _del_profile_property(self, pname):
        r = requests.delete(self._api_uri("me/messenger_profile"),
                            params={"access_token": self.page_access_token},
                            data=json.dumps({
                                'fields': [pname,]
                            }),
                            headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)

    def greeting(self, text):
        self.localized_greeting([LocalizedObj(locale="default", obj=text)])

    def localized_greeting(self, locale_list):
        if not locale_list:
            raise ValueError("List of locales is mandatory")
        pval = []
        for l in locale_list:
            if not isinstance(l, LocalizedObj):
                raise ValueError("greeting type error")
            if not isinstance(l.obj, str):
                raise ValueError("greeting text error")
            pval.append({
                "locale": l.locale,
                "text": l.obj
            })
        self._set_profile_property(pname="greeting", pval=pval)

    def hide_greeting(self):
        self._del_profile_property(pname="greeting")

    def show_starting_button(self, payload):
        if not payload or not isinstance(payload, str):
            raise ValueError("show_starting_button payload error")
        self._set_profile_property(pname="get_started",
                                   pval={"payload": payload})

    def hide_starting_button(self):
        self._del_profile_property(pname="get_started")

    def show_persistent_menu(self, buttons):
        self.show_localized_persistent_menu([LocalizedObj(locale="default",
                                                          obj=buttons)])

    def show_localized_persistent_menu(self, locale_list):
        if not locale_list:
            raise ValueError("List of locales is mandatory")
        pval = []
        for l in locale_list:
            if not isinstance(l, LocalizedObj):
                raise ValueError("persistent_menu error")
            if not isinstance(l.obj, list):
                raise ValueError("menu call_to_actions error")

            buttons = Buttons.convert_shortcut_buttons(l.obj)

            buttons_dict = []
            for button in buttons:
                if isinstance(button, ButtonWeb):
                    buttons_dict.append({
                        "type": "web_url",
                        "title": button.title,
                        "url": button.url
                    })
                elif isinstance(button, ButtonPostBack):
                    buttons_dict.append({
                        "type": "postback",
                        "title": button.title,
                        "payload": button.payload
                    })
                else:
                    raise ValueError('show_persistent_menu button type must be "url" or "postback"')

            pval.append({
                "locale": l.locale,
                "call_to_actions": buttons_dict
            })
        self._set_profile_property(pname="persistent_menu", pval=pval)

    def hide_persistent_menu(self):
        self._del_profile_property(pname="persistent_menu")

    """
    handlers and decorations
    """
    def set_webhook_handler(self, scope, callback):
        """
        Allows adding a webhook_handler as an alternative to the decorators
        """
        scope = scope.lower()

        if scope == 'after_send':
            self._after_send = callback
            return

        if scope not in Page.WEBHOOK_ENDPOINTS:
            raise ValueError("The 'scope' argument must be one of {}.".format(Page.WEBHOOK_ENDPOINTS))

        self._webhook_handlers[scope] = callback

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

    def handle_referral(self, func):
        self._webhook_handlers['referral'] = func

    def handle_game_play(self, func):
        self._webhook_handlers['game_play'] = func

    def handle_pass_thread_control(self, func):
        self._webhook_handlers['pass_thread_control'] = func

    def handle_take_thread_control(self, func):
        self._webhook_handlers['take_thread_control'] = func

    def handle_request_thread_control(self, func):
        self._webhook_handlers['request_thread_control'] = func

    def handle_app_roles(self, func):
        self._webhook_handlers['app_roles'] = func

    def handle_policy_enforcement(self, func):
        self._webhook_handlers['policy_enforcement'] = func

    def handle_checkout_update(self, func):
        self._webhook_handlers['checkout_update'] = func

    def handle_payment(self, func):
        self._webhook_handlers['payment'] = func

    def after_send(self, func):
        self._after_send = func

    _callback_default_types = ['QUICK_REPLY', 'POSTBACK']

    def callback(self, payloads=None, types=None):
        if types is None:
            types = self._callback_default_types

        if not isinstance(types, list):
            raise ValueError('callback types must be list')

        for type in types:
            if type not in self._callback_default_types:
                raise ValueError('callback types must be "QUICK_REPLY" or "POSTBACK"')

        def wrapper(func):
            if payloads is None:
                return func

            for payload in payloads:
                if 'QUICK_REPLY' in types:
                    self._quick_reply_callbacks[payload] = func
                if 'POSTBACK' in types:
                    self._button_callbacks[payload] = func

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

    def get_postback_callbacks(self, event):
        callbacks = []
        for key in self._button_callbacks.keys():
            if key not in self._button_callbacks_key_regex:
                self._button_callbacks_key_regex[key] = re.compile(key + '$')

            if self._button_callbacks_key_regex[key].match(event.payload):
                callbacks.append(self._button_callbacks[key])

        return callbacks
