class Buttons(object):
    def __init__(self, text, buttons):
        self.type = 'template'
        self.payload = {
            'template_type': 'button',
            'text': text,
            'buttons': Buttons.convert_shortcut_buttons(buttons)
        }

    @staticmethod
    def convert_shortcut_buttons(items):
        """
        support shortcut buttons [{'type':'web_url', 'title':'open web url', 'value':'https://~~'}]
        """
        if items is not None and isinstance(items, list):
            result = []
            for item in items:
                if isinstance(item, BaseButton):
                    result.append(item)
                elif isinstance(item, dict):
                    if item.get('type') in ['web_url', 'postback', 'phone_number']:
                        type = item.get('type')
                        title = item.get('title')
                        value = item.get('value', item.get('url', item.get('payload')))

                        if type == 'web_url':
                            result.append(ButtonWeb(title=title, url=value))
                        elif type == 'postback':
                            result.append(ButtonPostBack(title=title, payload=value))
                        elif type == 'phone_number':
                            result.append(ButtonPhoneNumber(title=title, payload=value))

                    else:
                        raise ValueError('Invalid button type')
                else:
                    raise ValueError('Invalid buttons variables')
            return result
        else:
            return items


class BaseButton(object):
    pass


class ButtonWeb(BaseButton):
    def __init__(self, title, url):
        self.type = 'web_url'
        self.title = title
        self.url = url


class ButtonPostBack(BaseButton):
    def __init__(self, title, payload):
        self.type = 'postback'
        self.title = title
        self.payload = payload


class ButtonPhoneNumber(BaseButton):
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
        self.buttons = Buttons.convert_shortcut_buttons(buttons)


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