import unittest
from fbmq import template as Template
from fbmq import utils


class TemplateTest(unittest.TestCase):
    def test_button_web(self):
        btn = Template.ButtonWeb(title="title", url="https://test.com")
        self.assertEquals('{"title": "title", "type": "web_url", "url": "https://test.com"}', utils.to_json(btn))
        print(utils.to_json(btn))

    def test_button_postback(self):
        btn = Template.ButtonPostBack(title="title", payload="TEST_PAYLOAD")
        self.assertEquals('{"payload": "TEST_PAYLOAD", "title": "title", "type": "postback"}', utils.to_json(btn))
        print(utils.to_json(btn))

    def test_button_phone(self):
        btn = Template.ButtonPhoneNumber(title="title", payload="+82108011")
        self.assertEquals('{"payload": "+82108011", "title": "title", "type": "phone_number"}', utils.to_json(btn))
        print(utils.to_json(btn))

    def test_button_share(self):
        btn = Template.ButtonShare()
        self.assertEquals('{"type": "element_share"}', utils.to_json(btn))
        print(utils.to_json(btn))

    def test_buttons(self):
        btns1 = Template.Buttons(text="Title", buttons=[
            {'type': 'web_url', 'title': 'title', 'value': 'https://test.com'},
            {'type': 'postback', 'title': 'title', 'value': 'TEST_PAYLOAD'},
            {'type': 'phone_number', 'title': 'title', 'value': '+82108011'},
            {'type': 'element_share'},
        ])

        btns2 = Template.Buttons(text="Title", buttons=[
            Template.ButtonWeb(title="title", url="https://test.com"),
            Template.ButtonPostBack(title="title", payload="TEST_PAYLOAD"),
            Template.ButtonPhoneNumber(title="title", payload="+82108011"),
            Template.ButtonShare()
        ])

        self.assertEquals(utils.to_json(btns1), utils.to_json(btns2))

    def test_button_shortcut(self):
        btns = Template.Buttons.convert_shortcut_buttons([
            {'type': 'web_url', 'title': 'title', 'value': 'https://test.com'},
            {'type': 'postback', 'title': 'title', 'value': 'TEST_PAYLOAD'},
            {'type': 'phone_number', 'title': 'title', 'value': '+82108011'},
            Template.ButtonWeb(title="title", url="https://test.com"),
        ])
        self.assertEquals('[{"title": "title", "type": "web_url", "url": "https://test.com"},'
                          ' {"payload": "TEST_PAYLOAD", "title": "title", "type": "postback"},'
                          ' {"payload": "+82108011", "title": "title", "type": "phone_number"},'
                          ' {"title": "title", "type": "web_url", "url": "https://test.com"}]', utils.to_json(btns))

        with self.assertRaises(ValueError) as context:
            Template.Buttons.convert_shortcut_buttons([{'type': 'url', 'title': 'title', 'value': 'https://test.com'}])

        with self.assertRaises(ValueError) as context:
            Template.Buttons.convert_shortcut_buttons(['hello'])

        self.assertEquals(None, Template.Buttons.convert_shortcut_buttons(None))

    def test_generic(self):
        generic = Template.Generic(
            elements=[Template.GenericElement(title='generic', subtitle='subtitle', item_url='https://test.com',
                                              image_url='https://test.com/img',
                                              buttons=[
                                                  {'type': 'web_url', 'title': 'title', 'value': 'https://test.com'}])])
        self.assertEquals(
            '{"payload": {"elements": [{"buttons": [{"title": "title", "type": "web_url", "url": "https://test.com"}],'
            ' "image_url": "https://test.com/img", "item_url": "https://test.com", "subtitle": "subtitle",'
            ' "title": "generic"}], "image_aspect_ratio": "horizontal", "template_type": "generic"}, "type": "template"}', utils.to_json(generic))

    def test_generic_square_image(self):
        generic = Template.Generic(
            elements=[Template.GenericElement(title='generic', subtitle='subtitle', item_url='https://test.com',
                                              image_url='https://test.com/img',
                                              buttons=[
                                                  {'type': 'web_url', 'title': 'title', 'value': 'https://test.com'}])],
            square_image=True)
        self.assertEquals(
            '{"payload": {"elements": [{"buttons": [{"title": "title", "type": "web_url", "url": "https://test.com"}],'
            ' "image_url": "https://test.com/img", "item_url": "https://test.com", "subtitle": "subtitle",'
            ' "title": "generic"}], "image_aspect_ratio": "square", "template_type": "generic"}, "type": "template"}', utils.to_json(generic))

    def test_list(self):
        listt = Template.List(
            elements=[Template.GenericElement(title='generic1', subtitle='subtitle1', item_url='https://test1.com',
                                              image_url='https://test.com1/img',
                                              buttons=[
                                                  {'type': 'web_url', 'title': 'title', 'value': 'https://test1.com'}]),
                      Template.GenericElement(title='generic2', subtitle='subtitle2', item_url='https://test2.com',
                                              image_url='https://test.com2/img',
                                              buttons=[
                                                  {'type': 'web_url', 'title': 'title', 'value': 'https://test2.com'}])],
            top_element_style='large',
            buttons=[
                { "title": "View More", "type": "postback", "payload": "payload" }])

        self.assertEquals(
            '{"payload": {"buttons": [{"payload": "payload", "title": "View More", "type": "postback"}], '
            '"elements": [{"buttons": [{"title": "title", "type": "web_url", "url": "https://test1.com"}], '
            '"image_url": "https://test.com1/img", "item_url": "https://test1.com", "subtitle": "subtitle1", "title": "generic1"}, '
            '{"buttons": [{"title": "title", "type": "web_url", "url": "https://test2.com"}], '
            '"image_url": "https://test.com2/img", "item_url": "https://test2.com", "subtitle": "subtitle2", "title": "generic2"}], '
            '"template_type": "list", '
            '"top_element_style": "large"}, '
            '"type": "template"}', utils.to_json(listt))

        with self.assertRaises(IndexError) as context:
            listt = Template.List(
                elements=[Template.GenericElement(title='generic1', subtitle='subtitle1', item_url='https://test1.com',
                                                  image_url='https://test.com1/img')])

        with self.assertRaises(IndexError) as context:
            listt = Template.List(
                elements=[Template.GenericElement(title='generic1', subtitle='subtitle1', item_url='https://test1.com',
                                                  image_url='https://test.com1/img'),
                          Template.GenericElement(title='generic2', subtitle='subtitle2', item_url='https://test2.com',
                                                  image_url='https://test.com2/img')],
                buttons=[
                    {"title": "View More", "type": "postback", "payload": "payload"},
                    {"title": "View More", "type": "postback", "payload": "payload"}])

    def test_account_link(self):
        link = Template.AccountLink(text="title", account_link_url="http://test.com", account_unlink_button=True)
        self.assertEquals('{"payload": {"buttons": [{"type": "account_link", "url": "http://test.com"}, '
                          '{"type": "account_unlink"}], "template_type": "button", "text": "title"}, '
                          '"type": "template"}', utils.to_json(link))

    def test_receipt_template(self):
        receipt_id = "order1357"
        element = Template.ReceiptElement(title="Oculus Rift",
                                          subtitle="Includes: headset, sensor, remote",
                                          quantity=1,
                                          price=599.00,
                                          currency="USD",
                                          image_url="/assets/riftsq.png"
                                          )

        address = Template.ReceiptAddress(street_1="1 Hacker Way",
                                          street_2="",
                                          city="Menlo Park",
                                          postal_code="94025",
                                          state="CA",
                                          country="US")

        summary = Template.ReceiptSummary(subtotal=698.99,
                                          shipping_cost=20.00,
                                          total_tax=57.67,
                                          total_cost=626.66)

        adjustment = Template.ReceiptAdjustment(name="New Customer Discount", amount=-50)

        receipt = Template.Receipt(recipient_name='Peter Chang',
                                   order_number=receipt_id,
                                   currency='USD',
                                   payment_method='Visa 1234',
                                   timestamp="1428444852",
                                   elements=[element],
                                   address=address,
                                   summary=summary,
                                   adjustments=[adjustment])

        self.assertEquals('{"payload": {"address": {"city": "Menlo Park", "country": "US", '
                          '"postal_code": "94025", "state": "CA", "street_1": "1 Hacker Way", "street_2": ""}, '
                          '"adjustments": [{"amount": -50, "name": "New Customer Discount"}], "currency": "USD", '
                          '"elements": [{"currency": "USD", "image_url": "/assets/riftsq.png", "price": 599.0, '
                          '"quantity": 1, "subtitle": "Includes: headset, sensor, remote", "title": "Oculus Rift"}], '
                          '"order_number": "order1357", "payment_method": "Visa 1234", "recipient_name": '
                          '"Peter Chang", "summary": {"shipping_cost": 20.0, "subtotal": 698.99, "total_cost": 626.66, '
                          '"total_tax": 57.67}, "template_type": "receipt", "timestamp": "1428444852"}, '
                          '"type": "template"}', utils.to_json(receipt))
