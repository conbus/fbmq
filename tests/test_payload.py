import unittest
from fbmq import payload as Payload
from fbmq import attachment as Attachment
from fbmq import utils


class PayloadTest(unittest.TestCase):
    def test_quick_reply(self):
        q = Payload.QuickReply(title='Yes', payload='PICK_YES')
        self.assertEquals('{"content_type": "text", "payload": "PICK_YES", "title": "Yes"}',
                          utils.to_json(q))

    def test_quick_reply_shortcut(self):
        q = Payload.Message.convert_shortcut_quick_reply([{'title': 'Yes', 'payload': 'PICK_YES'}])
        q = Payload.Message.convert_shortcut_quick_reply(q)
        self.assertEquals('[{"content_type": "text", "payload": "PICK_YES", "title": "Yes"}]',
                          utils.to_json(q))

        with self.assertRaises(ValueError) as context:
            Payload.Message.convert_shortcut_quick_reply(['hello'])

        self.assertEquals(None, Payload.Message.convert_shortcut_quick_reply(None))

    def test_receipt(self):
        q = Payload.Recipient(id=123456, phone_number='+8210')
        self.assertEquals('{"id": 123456, "phone_number": "+8210"}', utils.to_json(q))

    def test_message(self):
        with self.assertRaises(Exception):
            m = Payload.Message(text="hello", attachment=Attachment.Image('img'))

        m = Payload.Message(text="hello", metadata="METADATA", quick_replies=[{'title': 'Yes', 'payload': 'PICK_YES'}])
        self.assertEquals('{"attachment": null, "metadata": "METADATA", '
                          '"quick_replies": [{"content_type": "text", "payload": "PICK_YES", "title": "Yes"}], '
                          '"text": "hello"}', utils.to_json(m))

    def test_payload(self):
        recipient = Payload.Recipient(id=123456, phone_number='+8210')
        message = Payload.Message(text="hello", metadata="METADATA",
                                  quick_replies=[{'title': 'Yes', 'payload': 'PICK_YES'}])

        with self.assertRaises(ValueError):
            Payload.Payload(recipient=recipient, message=message, sender_action='NEW_ACTION')

        p = Payload.Payload(recipient=recipient,
                            message=message,
                            sender_action='typing_off',
                            notification_type='REGULAR')

        self.assertEquals(
            '{"message": {"attachment": null, "metadata": "METADATA", "quick_replies": '
            '[{"content_type": "text", "payload": "PICK_YES", "title": "Yes"}], "text": "hello"},'
            ' "notification_type": "REGULAR", "recipient": {"id": 123456, "phone_number": "+8210"},'
            ' "sender_action": "typing_off"}', utils.to_json(p))

        self.assertTrue(p.__eq__(p))
        self.assertTrue(p.__eq__(utils.to_json(p)))
