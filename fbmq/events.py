import json

class Event(object):
    def __init__(self, sender=None, recipient=None, timestamp=None, **kwargs):
        if sender is None:
            sender = dict()
        if recipient is None:
            recipient = dict()
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp

    @property
    def sender_id(self):
        return self.sender.get('id')

    @property
    def recipient_id(self):
        return self.recipient.get('id')

    @classmethod
    def new_from_json_dict(cls, data):
        return cls(**data)

    def __str__(self):
        return json.dumps(self.__class__.__name__)


class MessageEvent(Event):
    def __init__(self, message, **kwargs):
        super(MessageEvent, self).__init__(**kwargs)

        self.name = 'message'
        self.message = message

    @property
    def mid(self):
        return self.message.get('mid')

    @property
    def text(self):
        return self.message.get('text')

    @property
    def attachments(self):
        return self.message.get('attachments', [])

    @property
    def quick_reply(self):
        return self.message.get('quick_reply', {})

    @property
    def quick_reply_payload(self):
        return self.quick_reply.get('payload')

    @property
    def is_quick_reply(self):
        return self.message.get('quick_reply') is not None


class DeliveriesEvent(Event):
    def __init__(self, delivery, **kwargs):
        super(DeliveriesEvent, self).__init__(**kwargs)

        self.name = 'delivery'
        self.delivery = delivery

    @property
    def mids(self):
        return self.delivery.get('mids')

    @property
    def watermark(self):
        return self.delivery.get('watermark')

    @property
    def seq(self):
        return self.delivery.get('seq')


class EchoEvent(Event):
    def __init__(self, message, **kwargs):
        super(EchoEvent, self).__init__(**kwargs)

        self.name = 'echo'
        self.message = message

    @property
    def mid(self):
        return self.message.get('mid')

    @property
    def app_id(self):
        return self.message.get('app_id')

    @property
    def metadata(self):
        return self.message.get('metadata')

    @property
    def text(self):
        return self.message.get('text')

    @property
    def attachments(self):
        return self.message.get('attachments')


class ReadEvent(Event):
    def __init__(self, read, **kwargs):
        super(ReadEvent, self).__init__(**kwargs)

        self.name = 'read'
        self.read = read

    @property
    def seq(self):
        return self.read.get('seq')

    @property
    def watermark(self):
        return self.read.get('watermark')


class AccountLinkingEvent(Event):
    def __init__(self, account_linking, **kwargs):
        super(AccountLinkingEvent, self).__init__(**kwargs)

        self.name = 'account_linking'
        self.account_linking = account_linking

    @property
    def status(self):
        return self.account_linking.get('status')

    @property
    def is_linked(self):
        return self.status == 'linked'

    @property
    def authorization_code(self):
        return self.account_linking.get('authorization_code')


class GamePlayEvent(Event):
    def __init__(self, game_play, **kwargs):
        super(GamePlayEvent, self).__init__(**kwargs)

        self.name = 'game_play'
        self.game_play = game_play

    @property
    def game_id(self):
        return self.game_play.get('game_id')

    @property
    def player_id(self):
        return self.game_play.get('player_id')

    @property
    def context_type(self):
        return self.game_play.get('context_type')

    @property
    def context_id(self):
        return self.game_play.get('context_id')

    @property
    def score(self):
        return self.game_play.get('score')

    @property
    def payload(self):
        return self.game_play.get('payload')


class PassThreadEvent(Event):
    def __init__(self, pass_thread_control, **kwargs):
        super(PassThreadEvent, self).__init__(**kwargs)

        self.name = 'pass_thread_control'
        self.pass_thread_control = pass_thread_control

    @property
    def new_owner_app_id(self):
        return self.pass_thread_control.get('new_owner_app_id')

    @property
    def metadata(self):
        return self.pass_thread_control.get('metadata')


class TakeThreadEvent(Event):
    def __init__(self, take_thread_control, **kwargs):
        super(TakeThreadEvent, self).__init__(**kwargs)

        self.name = 'take_thread_control'
        self.take_thread_control = take_thread_control

    @property
    def previous_owner_app_id(self):
        return self.take_thread_control.get('previous_owner_app_id')

    @property
    def metadata(self):
        return self.take_thread_control.get('metadata')


class RequestThreadEvent(Event):
    def __init__(self, request_thread_control, **kwargs):
        super(RequestThreadEvent, self).__init__(**kwargs)

        self.name = 'request_thread_control'
        self.request_thread_control = request_thread_control

    @property
    def requested_owner_app_id(self):
        return self.request_thread_control.get('requested_owner_app_id')

    @property
    def metadata(self):
        return self.request_thread_control.get('metadata')


class AppRoleEvent(Event):
    def __init__(self, app_roles, **kwargs):
        super(AppRoleEvent, self).__init__(**kwargs)

        self.name = 'app_roles'
        self.app_roles = app_roles


class OptinEvent(Event):
    def __init__(self, optin, **kwargs):
        super(OptinEvent, self).__init__(**kwargs)

        self.name = 'optin'
        self.optin = optin

    @property
    def ref(self):
        return self.optin.get('ref')

    @property
    def user_ref(self):
        return self.optin.get('user_ref')


class PolicyEnforcementEvent(Event):
    def __init__(self, policy_enforcement, **kwargs):
        super(PolicyEnforcementEvent, self).__init__(**kwargs)

        self.name = 'policy_enforcement'
        self.policy_enforcement = policy_enforcement

    @property
    def action(self):
        return self.policy_enforcement.get('action')

    @property
    def reason(self):
        return self.policy_enforcement.get('reason')


class PostBackEvent(Event):
    def __init__(self, postback, **kwargs):
        super(PostBackEvent, self).__init__(**kwargs)

        self.name = 'postback'
        self.postback = postback

    @property
    def title(self):
        return self.postback.get('title')

    @property
    def payload(self):
        return self.postback.get('payload')

    @property
    def referral(self):
        return self.postback.get('referral')


class ReferralEvent(Event):
    def __init__(self, referral, **kwargs):
        super(ReferralEvent, self).__init__(**kwargs)

        self.name = 'referral'
        self.referral = referral

    @property
    def source(self):
        return self.referral.get('source')

    @property
    def type(self):
        return self.referral.get('type')

    @property
    def ref(self):
        return self.referral.get('ref')

    @property
    def referer_uri(self):
        return self.referral.get('referer_uri')


class CheckOutUpdateEvent(Event): #beta
    def __init__(self, checkout_update, **kwargs):
        super(CheckOutUpdateEvent, self).__init__(**kwargs)

        self.name = 'checkout_update'
        self.checkout_update = checkout_update

    @property
    def payload(self):
        return self.checkout_update.get('payload')

    @property
    def shipping_address(self):
        return self.checkout_update.get('shipping_address')


class PaymentEvent(Event): #beta
    def __init__(self, payment, **kwargs):
        super(PaymentEvent, self).__init__(**kwargs)

        self.name = 'payment'
        self.payment = payment

    @property
    def payload(self):
        return self.payment.get('payload')

    @property
    def requested_user_info(self):
        return self.payment.get('requested_user_info')

    @property
    def payment_credential(self):
        return self.payment.get('payment_credential')

    @property
    def amount(self):
        return self.payment.get('amount')

    @property
    def shipping_option_id(self):
        return self.payment.get('shipping_option_id')


class StandByEvent(Event):
    # suggest me to handle it.
    pass


class PrecheckoutEvent(Event): # beta
    pass