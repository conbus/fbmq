import unittest
from fbmq import attachment as Attachment
from fbmq import utils


class AttachmentTest(unittest.TestCase):
    def test_image(self):
        image = Attachment.Image('https://test.com/resource')
        self.assertEquals('{"payload": {"url": "https://test.com/resource"}, "type": "image"}', utils.to_json(image))

    def test_audio(self):
        audio = Attachment.Audio('https://test.com/resource')
        self.assertEquals('{"payload": {"url": "https://test.com/resource"}, "type": "audio"}', utils.to_json(audio))

    def test_video(self):
        video = Attachment.Video('https://test.com/resource')
        self.assertEquals('{"payload": {"url": "https://test.com/resource"}, "type": "video"}', utils.to_json(video))

    def test_file(self):
        file = Attachment.File('https://test.com/resource')
        self.assertEquals('{"payload": {"url": "https://test.com/resource"}, "type": "file"}', utils.to_json(file))
