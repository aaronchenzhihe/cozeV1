import uwebsocket
import _thread
from usr import packet #update, append
import ujson
import ubinascii
from usr.media import singleton_media
import utime
from queue import Queue

class cozews():
    def __init__(self, url, auth, callback=None):

        self.media = singleton_media('pcma', 4)
        if self.media is None:
            print('media is busy, please stop it first')
            return
        self.audio_queue = Queue()
        
        self.url = url
        self.headers = {"Authorization": "Bearer " + auth}

        self.ws_recv_task_id = None
        self.ws_audio_uplink_handler_id = None
        self.ws_audio_downlink_handler_id = None
        self.isactive = False
        self.volume = 8
        self.callback = callback

        if self.callback:
            self.event_queue = Queue()
            self.ws_callback_event_id = _thread.start_new_thread(self.ws_server_event_handler, ())

    def start(self):
        if self.media.is_idle() is False:
            print('media is busy, please stop it first')
            return
        self.client = uwebsocket.Client.connect(self.url, self.headers)
        msg = ujson.dumps(packet.update)
        self.client.send(msg)

        # ws recv task
        self.ws_recv_task_id = _thread.start_new_thread(self.ws_recv_task, ())

    def stop(self):
        self.stop_audio_stream()

        if self.ws_recv_task_id:
            _thread.stop_thread(self.ws_recv_task_id)
            self.ws_recv_task_id = None

        self.client.close()
        self.isactive = False

    def ws_audio_uplink_handler(self):
        msg = packet.append
        
        while True:
            try:
                data = b"".join([self.media.pcma_read() for _ in range(5)])
                if len(data) > 0:
                    msg['data']['delta'] = ubinascii.b2a_base64(data).strip()
                    payload = ujson.dumps(msg)
                    self.client.send(payload)
                utime.sleep_ms(1)
            except Exception as e:
                print("Error in ws_audio_uplink_handler: {}".format(e))

    def ws_audio_downlink_handler(self):
        while True:
            recv_data = self.audio_queue.get()
            start,end = ujson.search(recv_data, 'content')
            data = ubinascii.a2b_base64(recv_data[start:end])
            self.media.pcma_write(data)
            utime.sleep_ms(1)

    def ws_server_event_handler(self):
        while True:
            recv_data = self.event_queue.get()
            self.callback(self, recv_data)
            utime.sleep_ms(1)

    def start_audio_stream(self):
        self.media.start()
        self.media.set_volume(self.volume)

        self.ws_audio_uplink_handler_id = _thread.start_new_thread(self.ws_audio_uplink_handler, ())
        self.ws_audio_downlink_handler_id = _thread.start_new_thread(self.ws_audio_downlink_handler, ())
        self.isactive = True

    def stop_audio_stream(self):
        if self.ws_audio_uplink_handler_id:
            _thread.stop_thread(self.ws_audio_uplink_handler_id)
            self.ws_audio_uplink_handler_id = None
        if self.ws_audio_downlink_handler_id:
            _thread.stop_thread(self.ws_audio_downlink_handler_id)
            self.ws_audio_downlink_handler_id = None
        self.media.stop()

    def ws_recv_task(self):
        while True:
            try:
                recv_data = self.client.recv(4096)
                #print('recv_data_{}: {}'.format(len(recv_data), recv_data))
                if recv_data is None or len(recv_data) <= 1:
                    print('illegal data {}'.format(recv_data))
                    continue
                if  packet.EventType.CONVERSATION_AUDIO_DELTA in recv_data:
                    self.audio_queue.put(recv_data)
                else:
                    if self.callback:
                        self.event_queue.put(recv_data)
            except Exception as e:
                if "EIO" in str(e):
                    if self.isactive:
                        self.stop_audio_stream()
                        self.client.close()
                        self.isactive = False
                    msg = '{"event_type": "client.disconnected"}'
                    if self.callback:
                        #self.callback(self, msg)
                        self.event_queue.put(msg)
                    break
                else:
                    if recv_data is not None:
                        print('recv error[{}] |{}|'.format(len(recv_data), recv_data))
                    print('ws error |{}|'.format(e))
            utime.sleep_ms(1)

    def active(self):
        return self.isactive

    def config(self, arg = None, **kwargs):
        if arg != None:
            if arg == 'volume':
                if self.isactive is False:
                    return self.volume
                return self.media.get_volume()

        for key, value in kwargs.items():
            if key == 'volume':
                self.volume = value
                if self.isactive is False:
                    continue
                self.media.set_volume(value)

    def interrupted(self):
        if self.isactive is False:
            return
        # 打断对话
        msg = ujson.dumps(packet.cancel)
        self.client.send(msg)

    def update(self, data):
        if self.isactive is False:
            return
        msg = ujson.dumps(data)
        print('update: {}'.format(msg))
        self.client.send(msg)
        print("-----------------------------------------")
