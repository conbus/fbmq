import unittest
from fbmq.events import *

class TestEvents(unittest.TestCase):
    def test_message_event(self):
        quick_reply_payload = {
              "sender":{
                "id":"PSID"
              },
              "recipient":{
                "id":"PAGE_ID"
              },
              "timestamp":1458692752478,
              "message":{
                "mid":"mid.1457764197618:41d102a3e1ae206a38",
                "text":"hello, world!",
                "quick_reply": {
                  "payload": "<DEVELOPER_DEFINED_PAYLOAD>"
                }
              }
            }
        event = MessageEvent.new_from_json_dict(quick_reply_payload)

        self.assertEqual(event.sender_id, 'PSID')
        self.assertEqual(event.recipient_id, 'PAGE_ID')
        self.assertEqual(event.text, 'hello, world!')
        self.assertEqual(event.quick_reply_payload, '<DEVELOPER_DEFINED_PAYLOAD>')
        self.assertTrue(event.is_quick_reply)
        self.assertFalse(event.attachments)

        attachments_payload = {
              "sender":{
                "id":"PSID"
              },
              "recipient":{
                "id":"PAGE_ID"
              },
              "timestamp":1458692752478,
              "message":{
                "mid":"mid.1458696618141:b4ef9d19ec21086067",
                "attachments":[
                  {
                    "type":"image",
                    "payload":{
                      "url":"IMAGE_URL"
                    }
                  }
                ]
              }
            }
        event2 = MessageEvent.new_from_json_dict(attachments_payload)

        self.assertEqual(event2.sender_id, 'PSID')
        self.assertEqual(event2.recipient_id, 'PAGE_ID')
        self.assertEqual(event2.text, None)
        self.assertEqual(event2.quick_reply_payload, None)
        self.assertFalse(event2.is_quick_reply)
        self.assertEqual(
            event2.attachments,
            [
                {
                    "type": "image",
                    "payload": {
                        "url": "IMAGE_URL"
                    }
                }
            ]
        )

    def test_account_linking_event(self):
        linked_payload = {
              "sender":{
                "id":"USER_ID"
              },
              "recipient":{
                "id":"PAGE_ID"
              },
              "timestamp":1234567890,
              "account_linking":{
                "status":"linked",
                "authorization_code":"PASS_THROUGH_AUTHORIZATION_CODE"
              }
            }

        event = AccountLinkingEvent.new_from_json_dict(linked_payload)
        self.assertEqual(event.sender_id, 'USER_ID')
        self.assertEqual(event.recipient_id, 'PAGE_ID')
        self.assertEqual(event.status, 'linked')
        self.assertTrue(event.is_linked)
        self.assertEqual(event.authorization_code, "PASS_THROUGH_AUTHORIZATION_CODE")

        unlinked_payload = {
              "sender":{
                "id":"USER_ID"
              },
              "recipient":{
                "id":"PAGE_ID"
              },
              "timestamp":1234567890,
              "account_linking":{
                "status":"unlinked"
              }
            }
        event = AccountLinkingEvent.new_from_json_dict(unlinked_payload)
        self.assertEqual(event.sender_id, 'USER_ID')
        self.assertEqual(event.recipient_id, 'PAGE_ID')
        self.assertEqual(event.status, 'unlinked')
        self.assertFalse(event.is_linked)
        self.assertEqual(event.authorization_code, None)

    def test_deliveries_event(self):
        payload = {
              "sender":{
                "id":"<PSID>"
              },
              "recipient":{
                "id":"<PAGE_ID>"
              },
               "delivery":{
                  "mids":[
                     "mid.1458668856218:ed81099e15d3f4f233"
                  ],
                  "watermark":1458668856253,
                  "seq":37
               }
            }
        event = DeliveriesEvent.new_from_json_dict(payload)
        self.assertEqual(event.watermark, 1458668856253)
        self.assertEqual(event.seq, 37)
        self.assertEqual(event.mids, ["mid.1458668856218:ed81099e15d3f4f233"])

    def test_echo_event(self):
        payload = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1457764197627,
            "message": {
                "is_echo": True,
                "app_id": 1517776481860111,
                "metadata": "<DEVELOPER_DEFINED_METADATA_STRING>",
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!"
            }
        }

        event = EchoEvent.new_from_json_dict(payload)
        self.assertEqual(event.sender_id, 'USER_ID')
        self.assertEqual(event.recipient_id, 'PAGE_ID')
        self.assertEqual(event.app_id, 1517776481860111)
        self.assertEqual(event.metadata, "<DEVELOPER_DEFINED_METADATA_STRING>")
        self.assertEqual(event.text, "hello, world!")
        self.assertEqual(event.attachments, None)

    def test_optin_event(self):
        """
        Need Payload Information...
        """
        pass

    def test_postback_event(self):
        payload = {
            "sender": {
                "id": "<PSID>"
            },
            "recipient": {
                "id": "<PAGE_ID>"
            },
            "timestamp": 1458692752478,
            "postback": {
                "title": "<TITLE_FOR_THE_CTA>",
                "payload": "<USER_DEFINED_PAYLOAD>",
                "referral": {
                    "ref": "<USER_DEFINED_REFERRAL_PARAM>",
                    "source": "<SHORTLINK>",
                    "type": "OPEN_THREAD",
                }
            }
        }

        event = PostBackEvent.new_from_json_dict(payload)
        self.assertEqual(event.sender_id, "<PSID>")
        self.assertEqual(event.recipient_id, "<PAGE_ID>")
        self.assertEqual(event.timestamp, 1458692752478)
        self.assertEqual(event.title, '<TITLE_FOR_THE_CTA>')
        self.assertEqual(event.payload, '<USER_DEFINED_PAYLOAD>')

    def test_read_event(self):
        payload = {
            "sender": {
                "id": "<PSID>"
            },
            "recipient": {
                "id": "<PAGE_ID>"
            },
            "timestamp": 1458668856463,
            "read": {
                "watermark": 1458668856253,
                "seq": 38
            }
        }

        event = ReadEvent.new_from_json_dict(payload)
        self.assertTrue(isinstance(event, ReadEvent))
        self.assertEqual(event.sender_id, '<PSID>')
        self.assertEqual(event.recipient_id, '<PAGE_ID>')
        self.assertEqual(event.timestamp, 1458668856463)
        self.assertEqual(event.seq, 38)
        self.assertEqual(event.watermark, 1458668856253)