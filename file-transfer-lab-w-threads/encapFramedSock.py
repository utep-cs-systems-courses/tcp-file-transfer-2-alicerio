# Alan Licerio
# File Transfer
# 10-18-20

import re

class EncapFramedSock:
    def __init__(self, sockAddress):
        self.sock, self.address = sockAddress
        self.rbuf = b"" 

    def close(self):
        return self.sock.close()

    def send(self, fileName, payload, debugPrint=0):
        if debugPrint: print("framedSend: sending %d byte message" % len(payload))
        message = str(len(payload)).encode() + b':' + fileName.encode() + b':' + payload

        while len(message): # Run if there is a message sent.
            sent = self.sock.send(message)
            message = message[sent:]

    def receive(self, debugPrint=0):
        state = "getLength"
        msgLength = -1

        while True:
            if (state == "getLength"):
                match = re.match(b'([^:]+):(.*):(.*)', self.rbuf, re.DOTALL | re.MULTILINE)  # Regex to find colon. ":"
                if match:
                    lengthStr, fileName, self.rbuf = match.groups()
                    try:
                        msgLength = int(lengthStr) # Parses to integer to find length.
                    except:
                        if len(self.rbuf):
                            print("badly formed message length:", lengthStr)
                            return None, None
                    state = "getPayload"
            if state == "getPayload":
                if len(self.rbuf) >= msgLength:
                    payload = self.rbuf[0:msgLength]
                    self.rbuf = self.rbuf[msgLength:]
                    return fileName, payload

            r = self.sock.recv(100)
            self.rbuf += r
            if len(r) == 0:
                if len(self.rbuf) != 0: # Incomplete message found. Throw error.
                    print("FramedReceive: incomplete message. \n state=%s, length=%d, self.rbuf=%s" % (
                    state, msgLength, self.rbuf))
                return None, None
            if debugPrint: print("FramedReceive: state=%s, length=%d, self.rbuf=%s" % (state, msgLength, self.rbuf))

    def sendStatus(self, status, debugPrint=0):
        if debugPrint:
            print("framedSend: sending status %s" % str(status)) # Current status
        self.sock.sendall(str(status).encode())

    def Status(self):
        status = self.sock.recv(128)
        return status