import threading
import time
import common_data as cd

# таймер с выводом времени в заданный Label
class ClockThread(threading.Thread):
    formaparent = None
    exist = None
    needStop = False
    label_connect = None
    time_login = time.time()

    def __init__(self, formaparent, label_connect):
        threading.Thread.__init__(self)
        self.daemon = True
        self.formaparent = formaparent
        self.exist = cd.txt_error_connection == ''
        self.label_connect = label_connect

    def run(self):
        while True:
            if self.needStop:
                break
            d = {}
            data, result = cd.send_rest('MDMProxy.Inform', show_error=False)
            interval = cd.interval_connection
            try:
                if result:
                    # есть соединение
                    self.label_connect.setText('')
                    cd.txt_error_connection = ''
                    if not self.exist:  # восстановление соединения
                        self.exist = True
                        cd.login(show_error=False)
                        print('check_connect_yes', cd.expires, time.ctime(cd.expires), cd.token)
                        cd.send_evt(cd.evt_refresh_connect, self.formaparent)
                    if cd.inform_from_proxy != data:
                        #  смена базы или смена версии
                        cd.inform_from_proxy = data
                        cd.send_evt(cd.evt_change_database, self.formaparent)

                    k = data.partition('{')
                    txt = k[2]
                    k = txt.partition('}')
                    txt = k[0]  # перечень @параметр=значение через запятую
                    s = txt.split(",")
                    for i in range(0, len(s)):
                        txt = s[i]  # @параметр=значение
                        k = txt.partition(':')
                        d[k[0].strip()] = k[2].strip()
                else:
                    # нет соединения
                    self.label_connect.setText('No connect with PROXY ' + data)
                    cd.txt_error_connection = data
                    interval = max(1, cd.interval_connection // 10)
                    if self.exist:  # пропажа соединения
                        self.exist = False
                        cd.send_evt(cd.evt_cancel_connect, self.formaparent)
                        cd.inform_from_proxy = ''
                        cd.send_evt(cd.evt_change_database, self.formaparent)
            except:
                pass
            # ожидаем
            if time.time() - self.time_login >= 3600:
                cd.login(show_error=False)
                print('check_connect_time', cd.expires, time.ctime(cd.expires), cd.token)
                self.time_login = time.time()
            time.sleep(interval)
