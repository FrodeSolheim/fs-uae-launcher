import socket
import threading
import time
import traceback

from fsbc.application import call_after
from ..launcher_config import LauncherConfig
from ..launcher_signal import LauncherSignal


class ConnectionTester:
    def __init__(self):
        self.host_info = ("", 0)
        self.running = False
        self.stopping = False
        self.connection_attempt = 0

        LauncherConfig.add_listener(self)
        LauncherSignal.add_listener("quit", self)

    def on_quit_signal(self):
        print("on_quit_signal")
        self.stopping = True

    def on_config(self, key, _):
        if key in ["__netplay_addresses", "__netplay_port"]:
            addresses = LauncherConfig.get("__netplay_addresses")
            port = LauncherConfig.get("__netplay_port")
            host_info = (addresses, port)
            if host_info != self.host_info:
                self.host_info = host_info
            if not self.running:
                threading.Thread(target=self.thread_main,
                                 name="ConnectionTesterThread").start()
                self.running = True

    def thread_main(self):
        try:
            self._thread_main()
        except Exception:
            traceback.print_exc()

    def set_host(self, host, last_error):
        if last_error:
            last_error = "attempt {1} {0}".format(
                    last_error, self.connection_attempt)
        values = [("__netplay_host", host),
                  ("__netplay_host_last_error", last_error)]
        if last_error or not host:
            # force not ready when we cannot connect to server
            values.append(("__netplay_ready", "0"))

        def function():
            LauncherConfig.set_multiple(values)

        call_after(function)

    def _thread_main(self):
        last_host_info = None
        last_check_time = 0
        while not self.stopping:
            t = time.time()
            host_info = self.host_info
            time_diff = t - last_check_time
            time_for_new_test = time_diff > 30.0 or host_info != last_host_info
            if host_info[0] and host_info[1] and time_for_new_test:
                last_check_time = t
                last_host_info = host_info
                try:
                    result, error = self.test_connection(host_info)
                    self.set_host(result, error)
                except Exception as e:
                    traceback.print_exc()
                    # FIXME: handle problem...
                    self.set_host("", repr(e))
            time.sleep(1.0)

    def test_connection(self, host_info):
        addresses, port = host_info
        port = int(port)
        addresses = addresses.split(",")
        verified_host = ""
        last_error = ""
        for host in addresses:
            self.connection_attempt += 1
            host = host.strip()
            s = None
            try:
                try:
                    print("trying", host, port)
                    s = socket.create_connection((host, port))
                    s.send(b"PING")
                    # FIXME: set timeout, don't want to wait forever here...
                    data = s.recv(4)
                    if data == b"PONG":
                        verified_host = host
                        last_error = ""
                        break
                    else:
                        last_error = "Wrong PING response"
                except Exception:
                    last_error = traceback.format_exc()
                    print(last_error)
            finally:
                if s is not None:
                    try:
                        s.close()
                    except Exception:
                        pass
        print("test connection - verified host:", verified_host)
        return verified_host, last_error
