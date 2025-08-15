import threading
import errno
import socket
import serial


class Transport (threading.Thread):
    def __init__(self, callback): 
        threading.Thread.__init__(self)
        
        self.callback = callback
    




