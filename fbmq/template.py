class Buttons(object):
    def __init__(self, text, buttons):
        self.type = 'template'
        self.payload = {
            'template_type': 'button',
            'text': text,
            'buttons': buttons
        }


class ButtonWeb(object):
    def __init__(self, title, url):
        self.type = 'web_url'
        self.title = title
        self.url = url


class ButtonPostBack(object):
    def __init__(self, title, payload):
        self.type = 'postback'
        self.title = title
        self.payload = payload


class ButtonPhoneNumber(object):
    def __init__(self, title, payload):
        self.type = 'phone_number'
        self.title = title
        self.payload = payload


class Generic(object):
    def __init__(self, elements):
        self.type = 'template'
        self.payload = {
            'template_type': 'generic',
            'elements': elements
        }


class GenericElement(object):
    def __init__(self, title, subtitle=None, item_url=None, image_url=None, buttons=None):
        self.title = title
        self.subtitle = subtitle
        self.item_url = item_url
        self.image_url = image_url
        self.buttons = buttons


class Receipt(object):
    def __init__(self, recipient_name=None, order_number=None, currency='USD', payment_method='Visa 1234',
                 timestamp=None, elements=None, address=None, summary=None, adjustments=None):
        self.type = 'template'
        self.payload = {
            'template_type': 'receipt',
            'recipient_name': recipient_name,
            'order_number': order_number,
            'currency': currency,
            'payment_method': payment_method,
            'timestamp': timestamp,
            'elements': elements,
            'address': address,
            'summary': summary,
            'adjustments': adjustments
        }


class ReceiptElement(object):
    def __init__(self, title, subtitle=None, quantity=1, price=0, currency="USD", image_url=None):
        self.title = title
        self.subtitle = subtitle
        self.quantity = quantity
        self.price = price
        self.currency = currency
        self.image_url = image_url


class ReceiptAddress(object):
    def __init__(self, street_1=None, street_2=None, city=None, postal_code=None, state=None, country=None):
        self.street_1 = street_1
        self.street_2 = street_2
        self.city = city
        self.postal_code = postal_code
        self.state = state
        self.country = country


class ReceiptSummary(object):
    def __init__(self, subtotal=None, shipping_cost=None, total_tax=None, total_cost=None):
        self.subtotal = subtotal
        self.shipping_cost = shipping_cost
        self.total_tax = total_tax
        self.total_cost = total_cost


class ReceiptAdjustment(object):
    def __init__(self, name, amount=0):
        self.name = name
        self.amount = amount


class AccountLink(object):
    def __init__(self, text, account_link_url=None, account_unlink_button=False):
        self.type = 'template'
        self.payload = {
            'template_type': 'button',
            'text': text,
            'buttons': []
        }

        if account_link_url is not None:
            self.payload['buttons'].append({
                'type': 'account_link',
                'url': account_link_url
            })

        if account_unlink_button:
            self.payload['buttons'].append({
                'type': 'account_unlink'
            })