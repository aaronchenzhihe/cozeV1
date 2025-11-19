
import audio
import G711

singleton_media_obj  = None

def singleton_media(name, type):
    global singleton_media_obj
    if singleton_media_obj is None:
        singleton_media_obj = media(name, type)
        return singleton_media_obj

    if singleton_media_obj.is_idle():
        print('{} is using media'.format(singleton_media_obj.name))
        return None
    else:
        singleton_media_obj.set_media_config(name, type)
        return singleton_media_obj

class media:
    MEDIA_TYPE_AUDIO = 1
    MEDIA_TYPE_PCM = 2
    MEDIA_TYPE_RECORD = 3
    MEDIA_TYPE_PCMA = 4

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.pcm = None
        self.pcma = None

    def set_media_config(self, name, type):
        self.name = name
        self.type = type

    def is_idle(self):
        if self.pcma:
            return False
        return True

    def start(self):
        if  self.type == self.MEDIA_TYPE_PCMA:
            self.pcm = audio.Audio.PCM(0, 1, 8000, 2, 1, 5)
            self.pcma = G711(self.pcm)
        else:
            raise('unkown audio type')

    def stop(self):
        if self.type == self.MEDIA_TYPE_PCMA:
            if self.pcma:
                del self.pcma
                self.g711 = None
                self.pcm.close()
                del self.pcm
                self.pcm = None
        else:
            raise('wrong audio type')
        self.name = None
        self.type = None

    def pcma_read(self):
        return self.pcma.read(0)
    
    def pcma_write(self, payload):
        return self.pcma.write(payload, 0)

    def set_volume(self, value):
        if self.type == self.MEDIA_TYPE_PCMA:
            return self.pcm.setVolume(value)
        else:
            raise('wrong audio type')

    def get_volume(self):
        if self.type == self.MEDIA_TYPE_PCMA:
            return self.pcm.getVolume()
        else:
            raise('wrong audio type')
