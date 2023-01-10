from setup.settings import client
import threading

class SmsMessageThread(threading.Thread):

    def __init__(self, body, from_, to):
        self.body = body
        self.from_ = from_
        self.to = to
        threading.Thread.__init__(self)

    def run(self):
        try:
            client.messages.create(
                body = self.body,
                from_ = self.from_,
                to = self.to
            )
        except:
            pass