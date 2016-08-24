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

    def test_button_shortcut(self):
        btns = Template.Buttons.convert_shortcut_buttons([
            {'type': 'web_url', 'title': 'title', 'value': 'https://test.com'},
            {'type': 'postback', 'title': 'title', 'value': 'TEST_PAYLOAD'},
            {'type': 'phone_number', 'title': 'title', 'value': '+82108011'},
        ])
        self.assertEquals('[{"title": "title", "type": "web_url", "url": "https://test.com"},'
                          ' {"payload": "TEST_PAYLOAD", "title": "title", "type": "postback"},'
                          ' {"payload": "+82108011", "title": "title", "type": "phone_number"}]', utils.to_json(btns))

        with self.assertRaises(ValueError) as context:
            Template.Buttons.convert_shortcut_buttons([{'type': 'url', 'title': 'title', 'value': 'https://test.com'}])

    def test_generic(self):
        generic = Template.Generic(
            elements=[Template.GenericElement(title='generic', subtitle='subtitle', item_url='https://test.com',
                                              image_url='https://test.com/img',
                                              buttons=[
                                                  {'type': 'web_url', 'title': 'title', 'value': 'https://test.com'}])])

        self.assertEquals(
            '{"payload": {"elements": [{"buttons": [{"title": "title", "type": "web_url", "url": "https://test.com"}],'
            ' "image_url": "https://test.com/img", "item_url": "https://test.com", "subtitle": "subtitle",'
            ' "title": "generic"}], "template_type": "generic"}, "type": "template"}', utils.to_json(generic))
