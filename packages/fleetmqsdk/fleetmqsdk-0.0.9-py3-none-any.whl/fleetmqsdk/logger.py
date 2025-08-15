import zmq
from .utils import _getAddress
        
class Logger:
    _instance = None

    def __new__(cls, context, port="5550", ipc=False):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._topic = "sdk-logger"
            cls._topicBytes = cls._topic.encode()
            cls._pushSocket = context.socket(zmq.PUSH)
            address = _getAddress(port, ipc)
            try:
                cls._pushSocket.connect(address)
            except zmq.ZMQError as e:
                print(f"Failed to open logging socket: {e}")
                exit(1)
            print(f"Bound to logging socket: {address}")
        return cls._instance
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._pushSocket.close()

    def writeLine(self, message, args=None):
        if args is None:
            pass
        elif isinstance(args, (list, tuple)):
            message = message.format(*args)
        else:
            message = message.format(args)
        self._pushSocket.send_multipart([self._topicBytes, message.encode()])
