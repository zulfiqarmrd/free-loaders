from offloaders.offloader import Offloader
# from threading import Timer
# from time import sleep
#
#
# class Repeat(Timer):
#     def run(self):
#         while not self.finished.wait(self.interval):
#             self.function(*self.args, **self.kwargs)
#
#
# t = Repeat(1.0, lambda: print("Hello, World!"))
# t.start()
# sleep(5)
# t.cancel()


offloader0 = Offloader(0)
# offloader0.offload()
# offloader0.send_feedback()
