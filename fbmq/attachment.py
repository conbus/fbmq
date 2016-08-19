class Image(object):
    def __init__(self, url):
        self.type = 'image'
        self.payload = {'url': url}


class Audio(object):
    def __init__(self, url):
        self.type = 'audio'
        self.payload = {'url': url}


class Video(object):
    def __init__(self, url):
        self.type = 'video'
        self.payload = {'url': url}


class File(object):
    def __init__(self, url):
        self.type = 'file'
        self.payload = {'url': url}