import json
from config import CONFIG
from fbmq import Attachment, Template, QuickReply, Page
USER_SEQ = {}
fbpage = Page(CONFIG['FACEBOOK_TOKEN'])


def messaging_events(payload):
    data = json.loads(payload)

    # Make sure this is a page subscription
    if data.get("object") == "page":
        # Iterate over each entry
        # There may be multiple if batched
        for entry in data.get("entry"):
            for event in entry.get("messaging"):
                yield event


def received_authentication(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    time_of_auth = event.get("timestamp")

    pass_through_param = event.get("optin", {}).get("ref")

    print("Received authentication for user %s and page %s with pass "
          "through param '%s' at %s" % (sender_id, recipient_id, pass_through_param, time_of_auth))

    fbpage.send(sender_id, "Authentication successful")


def received_message(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    time_of_message = event.get("timestamp")
    message = event.get("message", {})
    print("Received message for user %s and page %s at %s with message:"
          % (sender_id, recipient_id, time_of_message))
    print(message)

    seq = message.get("seq", 0)
    is_echo = message.get("is_echo")
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")

    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    seq_id = sender_id + ':' + recipient_id
    if USER_SEQ.get(seq_id, -1) >= seq:
        print("Ignore duplicated request")
        return None
    else:
        USER_SEQ[seq_id] = seq

    if is_echo:
        print("Received echo for message %s and app %s with metadata %s" % (message_id, app_id, metadata))
        return None
    elif quick_reply:
        quick_reply_payload = quick_reply.get('payload')
        print("quick reply for message %s with payload %s" % (message_id, quick_reply_payload))

        fbpage.send(sender_id, "Quic reply tapped")

    if message_text:
        send_message(sender_id, message_text)
    elif message_attachments:
        fbpage.send(sender_id, "Message with attachment received")


def received_delivery_confirmation(event):
    delivery = event.get("delivery", {})
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")

    if message_ids:
        for message_id in message_ids:
            print("Received delivery confirmation for message ID: %s" % message_id)

    print("All message before %s were delivered." % watermark)


def received_postback(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    time_of_postback = event.get("timestamp")

    payload = event.get("postback", {}).get("payload")

    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))

    fbpage.send(sender_id, "Postback called")


def received_message_read(event):
    watermark = event.get("read", {}).get("watermark")
    seq = event.get("read", {}).get("seq")

    print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))


def received_account_link(event):
    sender_id = event.get("sender", {}).get("id")
    status = event.get("account_linking", {}).get("status")
    auth_code = event.get("account_linking", {}).get("authorization_code")

    print("Received account link event with for user %s with status %s and auth code %s "
          % (sender_id, status, auth_code))


def send_message(recipient_id, text):
    # If we receive a text message, check to see if it matches any special
    # keywords and send back the corresponding example. Otherwise, just echo
    # the text we received.
    special_keywords = {
        "image": send_image,
        "gif": send_gif,
        "audio": send_audio,
        "video": send_video,
        "file": send_file,
        "button": send_button,
        "generic": send_generic,
        "receipt": send_receipt,
        "quick reply": send_quick_reply,
        "read receipt": send_read_receipt,
        "typing on": send_typing_on,
        "typing off": send_typing_off,
        "account linking": send_account_linking
    }

    if text in special_keywords:
        special_keywords[text](recipient_id)
    else:
        fbpage.send(recipient_id, text)


def send_image(recipient):
    fbpage.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "/assets/rift.png"))


def send_gif(recipient):
    fbpage.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "/assets/instagram_logo.gif"))


def send_audio(recipient):
    fbpage.send(recipient, Attachment.Audio(CONFIG['SERVER_URL'] + "/assets/sample.mp3"))


def send_video(recipient):
    fbpage.send(recipient, Attachment.Video(CONFIG['SERVER_URL'] + "/assets/allofus480.mov"))


def send_file(recipient):
    fbpage.send(recipient, Attachment.File(CONFIG['SERVER_URL'] + "/assets/test.txt"))


def send_button(recipient):
    fbpage.send(recipient, Template.Buttons("hello", [
        Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
        Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
        Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
    ]))


def send_generic(recipient):
    fbpage.send(recipient, Template.Generic([
        Template.GenericElement("rift",
                                subtitle="Next-generation virtual reality",
                                item_url="https://www.oculus.com/en-us/rift/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/rift.png",
                                buttons=[
                                    Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                                    Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                                    Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                                ]),
        Template.GenericElement("touch",
                                subtitle="Your Hands, Now in VR",
                                item_url="https://www.oculus.com/en-us/touch/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/touch.png",
                                buttons=[
                                    Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                                    Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                                    Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                                ])
    ]))


def send_receipt(recipient):
    receipt_id = "order1357"
    element = Template.ReceiptElement(title="Oculus Rift",
                                      subtitle="Includes: headset, sensor, remote",
                                      quantity=1,
                                      price=599.00,
                                      currency="USD",
                                      image_url=CONFIG['SERVER_URL'] + "/assets/riftsq.png"
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

    fbpage.send(recipient, Template.Receipt(recipient_name='Peter Chang',
                                            order_number=receipt_id,
                                            currency='USD',
                                            payment_method='Visa 1234',
                                            timestamp="1428444852",
                                            elements=[element],
                                            address=address,
                                            summary=summary,
                                            adjustments=[adjustment]))


def send_quick_reply(recipient):
    fbpage.send(recipient, "What's your favorite movie genre?",
              quick_replies=[QuickReply(title="Action", payload="PICK_ACTION"),
                             QuickReply(title="Comedy", payload="PICK_COMEDY")],
              metadata="DEVELOPER_DEFINED_METADATA")


def send_read_receipt(recipient):
    fbpage.mark_seen(recipient)


def send_typing_on(recipient):
    fbpage.typing_on(recipient)


def send_typing_off(recipient):
    fbpage.typing_off(recipient)


def send_account_linking(recipient):
    fbpage.send(recipient, Template.AccountLink(text="Welcome. Link your account.",
                                                account_link_url=CONFIG['SERVER_URL'] + "/authorize",
                                                account_unlink_button=True))


def send_text_message(recipient, text):
    fbpage.send(recipient, text, metadata="DEVELOPER_DEFINED_METADATA")
