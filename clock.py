import threading
import time


# таймер с выводом времени в заданный Label
class ClockThread(threading.Thread):
    def __init__(self,interval, labelTime):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.labelTime = labelTime

    def run(self):
        while True:
            try:
                self.labelTime.setText(time.ctime())
            except:
                pass
            time.sleep(self.interval)
