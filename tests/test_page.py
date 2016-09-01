import unittest
import json
import mock
from fbmq.fbmq import Page
from fbmq import payload as Payload
from fbmq import attachment as Attachment
from fbmq import template as Template
from fbmq import utils


class PageTest(unittest.TestCase):
    def setUp(self):
        self.page = Page('TOKEN')
        self.page._send = mock.MagicMock()
        self.page._send_thread_settings = mock.MagicMock()
        self.page._fetch_page_info = mock.MagicMock()

    def test_send(self):
        self.page.send(12345, "hello world", quick_replies=[{'title': 'Yes', 'payload': 'YES'}], callback=1)
        self.page._send.assert_called_once_with('{"message": {"attachment": null, "metadata": null, '
                                                '"quick_replies": '
                                                '[{"content_type": "text", "payload": "YES", "title": "Yes"}], '
                                                '"text": "hello world"},'
                                                ' "notification_type": null, '
                                                '"recipient": {"id": 12345, "phone_number": null}, '
                                                '"sender_action": null}', callback=1)

    def test_typingon(self):
        self.page.typing_on(1004)
        self.page._send.assert_called_once_with('{"message": null, "notification_type": null, '
                                                '"recipient": {"id": 1004, "phone_number": null}, '
                                                '"sender_action": "typing_on"}')

    def test_typingoff(self):
        self.page.typing_off(1004)
        self.page._send.assert_called_once_with('{"message": null, "notification_type": null, '
                                                '"recipient": {"id": 1004, "phone_number": null}, '
                                                '"sender_action": "typing_off"}')

    def test_markseen(self):
        self.page.mark_seen(1004)
        self.page._send.assert_called_once_with('{"message": null, "notification_type": null, '
                                                '"recipient": {"id": 1004, "phone_number": null}, '
                                                '"sender_action": "mark_seen"}')

    def test_handle_webhook_errors(self):
        payload = """
        {
            "object":"not_a_page",
            "entry":[
                {"id":"1691462197845448","time":1472026867114,
                "messaging":[
                    {"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026867080,
                     "message":{"mid":"mid.1472026867074:cfb5e1d4bde07a2a55","seq":812,"text":"hello world"}}
                ]}
            ]
        }
        """
        self.assertFalse(self.page.handle_webhook(payload))

        payload = """
        {
            "object":"page",
            "entry":[
                {"id":"1691462197845448","time":1472026867114,
                "messaging":[
                    {"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026867080,
                     "unknown":{"mid":"mid.1472026867074:cfb5e1d4bde07a2a55","seq":812,"text":"hello world"}}
                ]}
            ]
        }
        """

        self.page.handle_webhook(payload)

        @self.page.callback
        def unknown():
            pass

    def test_page_info(self):
        self.assertEquals(0, self.page._fetch_page_info.call_count)
        self.page.page_id
        self.assertEquals(1, self.page._fetch_page_info.call_count)
        self.page.page_name
        self.assertEquals(2, self.page._fetch_page_info.call_count)

        self.page._page_id = 1
        self.page._page_name = 'name'
        print(self.page.page_id, self.page.page_name)

        self.assertEquals(2, self.page._fetch_page_info.call_count)


    def test_handle_webhook_message(self):
        payload = """
        {
            "object":"page",
            "entry":[
                {"id":"1691462197845448","time":1472026867114,
                "messaging":[
                    {"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026867080,
                     "message":{"mid":"mid.1472026867074:cfb5e1d4bde07a2a55","seq":812,"text":"hello world"}}
                ]}
            ]
        }
        """
        counter = mock.MagicMock()
        self.page.handle_webhook(payload)

        @self.page.handle_message
        def handler1(event):
            self.assertTrue(event.is_message)
            self.assertTrue(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertFalse(event.is_quick_reply)
            self.assertFalse(event.is_echo)
            self.assertFalse(event.is_read)
            self.assertFalse(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertFalse(event.is_delivery)
            self.assertFalse(event.is_account_linking)
            self.assertEquals(event.timestamp, 1472026867080)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.message_text, 'hello world')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, message=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_read(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472026870339,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026869186,
            "read":{"watermark":1472026868763,"seq":814}}]
        }]}
        """
        counter = mock.MagicMock()

        @self.page.handle_read
        def handler1(event):
            self.assertFalse(event.is_message)
            self.assertFalse(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertFalse(event.is_quick_reply)
            self.assertFalse(event.is_echo)
            self.assertTrue(event.is_read)
            self.assertFalse(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertFalse(event.is_delivery)
            self.assertFalse(event.is_account_linking)
            self.assertEquals(event.timestamp, 1472026869186)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.message_text, None)
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, read=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_echo(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472026869143,
        "messaging":[{
            "sender":{"id":"1691462197845448"},"recipient":{"id":"1134343043305865"},"timestamp":1472026868763,
            "message":{"is_echo":true,"app_id":950864918368986,"mid":"mid.1472026868734:832ecbdfc1ffc30139","seq":813,
            "text":"hello"}}]
        }]}
        """
        counter = mock.MagicMock()

        @self.page.handle_echo
        def handler1(event):
            self.assertTrue(event.is_message)
            self.assertTrue(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertFalse(event.is_quick_reply)
            self.assertTrue(event.is_echo)
            self.assertFalse(event.is_read)
            self.assertFalse(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertFalse(event.is_delivery)
            self.assertFalse(event.is_account_linking)
            self.assertEquals(event.timestamp, 1472026868763)
            self.assertEquals(event.sender_id, '1691462197845448')
            self.assertEquals(event.recipient_id, '1134343043305865')
            self.assertEquals(event.message_text, 'hello')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, echo=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_delivery(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028396029,
            "messaging":[{"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":0,
            "delivery":{"mids":["mid.1472028395154:917e24ea99bc7d8f11"],"watermark":1472028395190,"seq":821}}
            ]}]}
        """
        counter = mock.MagicMock()

        @self.page.handle_delivery
        def handler1(event):
            self.assertFalse(event.is_message)
            self.assertFalse(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertFalse(event.is_quick_reply)
            self.assertFalse(event.is_echo)
            self.assertFalse(event.is_read)
            self.assertFalse(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertTrue(event.is_delivery)
            self.assertFalse(event.is_account_linking)
            self.assertEquals(event.timestamp, 0)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.message_text, None)
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, delivery=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_account_linking(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028542079,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028542079,
            "account_linking":{"authorization_code":"1234567890","status":"linked"}}]}]}
        """
        counter = mock.MagicMock()

        @self.page.handle_account_linking
        def handler1(event):
            self.assertFalse(event.is_message)
            self.assertFalse(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertFalse(event.is_quick_reply)
            self.assertFalse(event.is_echo)
            self.assertFalse(event.is_read)
            self.assertFalse(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertFalse(event.is_delivery)
            self.assertTrue(event.is_account_linking)
            self.assertEquals(event.timestamp, 1472028542079)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.message_text, None)
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, account_linking=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_postback(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"DEVELOPED_DEFINED_PAYLOAD"}}]
        }]}
        """
        counter1 = mock.MagicMock()

        @self.page.handle_postback
        def handler1(event):
            self.assertFalse(event.is_message)
            self.assertFalse(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertFalse(event.is_quick_reply)
            self.assertFalse(event.is_echo)
            self.assertFalse(event.is_read)
            self.assertTrue(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertFalse(event.is_delivery)
            self.assertFalse(event.is_account_linking)
            self.assertEquals(event.timestamp, 1472028006107)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.message_text, None)
            self.assertEquals(event.postback_payload, 'DEVELOPED_DEFINED_PAYLOAD')
            self.assertEquals(event.postback_payload, event.postback.get('payload'))
            counter1()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter1.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, postback=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_postback_button_callback(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"DEVELOPED_DEFINED_PAYLOAD"}}]
        }]}
        """
        counter1 = mock.MagicMock()
        counter2 = mock.MagicMock()

        def handler1(event):
            self.assertFalse(event.is_message)
            self.assertFalse(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertFalse(event.is_quick_reply)
            self.assertFalse(event.is_echo)
            self.assertFalse(event.is_read)
            self.assertTrue(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertFalse(event.is_delivery)
            self.assertFalse(event.is_account_linking)
            self.assertEquals(event.timestamp, 1472028006107)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.message_text, None)
            self.assertEquals(event.postback_payload, event.postback.get('payload'))
            counter1()

        @self.page.callback(['DEVELOPED_DEFINED_PAYLOAD'], types=['POSTBACK'])
        def button_callback(payload, event):
            counter2()

        self.page.handle_webhook(payload, postback=handler1)

        self.assertEquals(1, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"DEVELOPED_DEFINED_PAYLOAD2"}}]
        }]}
        """
        self.page.handle_webhook(payload, postback=handler1)
        self.assertEquals(2, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_quickreply_callback(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"PICK_ACTION"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """
        counter1 = mock.MagicMock()
        counter2 = mock.MagicMock()

        @self.page.handle_message
        def handler1(event):
            self.assertTrue(event.is_message)
            self.assertTrue(event.is_text_message)
            self.assertFalse(event.is_attachment_message)
            self.assertTrue(event.is_quick_reply)
            self.assertFalse(event.is_echo)
            self.assertFalse(event.is_read)
            self.assertFalse(event.is_postback)
            self.assertFalse(event.is_optin)
            self.assertFalse(event.is_delivery)
            self.assertFalse(event.is_account_linking)
            self.assertEquals(event.timestamp, 1472028637825)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.message_text, 'Action')
            self.assertEquals(event.quick_reply_payload, event.quick_reply.get('payload'))
            counter1()

        @self.page.callback(['PICK_ACTION'], types=['QUICK_REPLY'])
        def button_callback(payload, event):
            counter2()

        self.page.handle_webhook(payload, postback=handler1)

        self.assertEquals(1, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"PICK_COMEDY"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """
        self.page.handle_webhook(payload, postback=handler1)
        self.assertEquals(2, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

    def test_callback_regex_pattern(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"ACTION/1"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """

        counter1 = mock.MagicMock()

        @self.page.callback(['ACTION'], types=['QUICK_REPLY'])
        def callback(payload, event):
            counter1()

        self.page.handle_webhook(payload)

        self.assertEquals(0, counter1.call_count)

        @self.page.callback(['ACTION/(.+)'], types=['QUICK_REPLY'])
        def callback2(payload, event):
            counter1()

        self.page.handle_webhook(payload)

        self.assertEquals(1, counter1.call_count)

    def test_callback_types(self):
        counter1 = mock.MagicMock()
        counter2 = mock.MagicMock()
        counter3 = mock.MagicMock()

        quickreply_payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"ACTION/1"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """

        button_payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"ACTION/100"}}]
        }]}
        """

        @self.page.callback(['ACTION/(.+)'])
        def callback(payload, event):
            counter1()

        @self.page.callback(['ACTION(.+)'], types=['QUICK_REPLY'])
        def callback2(payload, event):
            counter2()

        @self.page.callback(['ACTIO(.+)'], types=['POSTBACK'])
        def callback3(payload, event):
            counter3()

        self.page.handle_webhook(quickreply_payload)
        self.assertEquals(1, counter1.call_count)
        self.assertEquals(1, counter2.call_count)
        self.assertEquals(0, counter3.call_count)
        self.page.handle_webhook(button_payload)
        self.assertEquals(2, counter1.call_count)
        self.assertEquals(1, counter2.call_count)
        self.assertEquals(1, counter3.call_count)

        with self.assertRaises(ValueError):
            @self.page.callback(['ACTIO(.+)'], types=['LSKDJFLKSJFD'])
            def callback4(payload, event):
                counter3()

    def test_greeting(self):
        self.page.greeting("hello")
        self.page._send_thread_settings.assert_called_once_with(json.dumps(json.loads("""
        {
            "setting_type": "greeting",
            "greeting": {
                "text": "hello"
            }
        }
        """)))

        with self.assertRaises(ValueError):
            self.page.greeting(1)

    def test_starting_button(self):
        self.page.show_starting_button("PAYLOAD")
        self.page._send_thread_settings.assert_called_once_with(json.dumps({
            "setting_type": "call_to_actions",
            "thread_state": "new_thread",
            "call_to_actions": [{
                "payload": "PAYLOAD"
            }]
        }))

        self.page.hide_starting_button()
        self.page._send_thread_settings.assert_called_with(json.dumps({
            "setting_type": "call_to_actions",
            "thread_state": "new_thread"
        }))

        with self.assertRaises(ValueError):
            self.page.show_starting_button(1)

    def test_persistent_menu(self):
        self.page.show_persistent_menu([{'type':'postback', 'title':'yes', 'payload':'hobbang'},
                                        {'type':'web_url', 'title':'url', 'value':'url'},
                                        Template.ButtonPostBack('ho', 'bbang')])

        self.page._send_thread_settings.assert_called_with(json.dumps({
            "setting_type": "call_to_actions",
            "thread_state": "existing_thread",
            "call_to_actions": [{'type':'postback', 'title':'yes', 'payload':'hobbang'},
                                {'type':'web_url', 'title':'url', 'url':'url'},
                                {'type':'postback', 'title':'ho', 'payload':'bbang'}]
        }))

        self.page.show_persistent_menu([Template.ButtonPostBack('ho', 'bbang'),
                                        Template.ButtonWeb('title', 'url')])

        self.page._send_thread_settings.assert_called_with(json.dumps({
            "setting_type": "call_to_actions",
            "thread_state": "existing_thread",
            "call_to_actions": [{'type':'postback', 'title':'ho', 'payload':'bbang'},
                                {'type':'web_url', 'title':'title', 'url':'url'}]
        }))

        with self.assertRaises(ValueError):
            self.page.show_persistent_menu("hi")

        with self.assertRaises(ValueError):
            self.page.show_persistent_menu([Template.ButtonPhoneNumber('ho', 'bbang'),
                                            Template.ButtonWeb('title', 'url')])

        with self.assertRaises(ValueError):
            self.page.show_persistent_menu([{'type':'ho'}])

        self.page.hide_persistent_menu()
        self.page._send_thread_settings.assert_called_with(json.dumps({
            "setting_type": "call_to_actions",
            "thread_state": "existing_thread"
        }))
