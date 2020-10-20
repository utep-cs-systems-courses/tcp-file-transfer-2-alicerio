import re

def framedSend(sock, filename, payload, debug=0):
    if debug:
        print("framedSend: sending %d byte message" % len(payload))
    msg = str(len(payload)).encode() + b':' + filename.encode() + b':' + payload
    while len(msg):
        nsent = sock.send(msg)
        msg = msg[nsent:]

rbuf = b""  # Buffer

def framedReceive(sock, debug=0):
    global rbuf
    state = "getLength"
    msgLength = -1 # Default length.
    while True:
        if (state == "getLength"):
            match = re.match(b'([^:]+):(.*):(.*)', rbuf, re.DOTALL | re.MULTILINE)  # Regex to find colon. ":"
            if match:
                lengthStr, filename, rbuf = match.groups()
                try:
                    msgLength = int(lengthStr) # Parses to integer to find length.
                except:
                    if len(rbuf):
                        print("badly formed message length:", lengthStr) # Error
                        return None, None
                state = "getPayload"
        if state == "getPayload":
            if len(rbuf) >= msgLength:
                payload = rbuf[0:msgLength]
                rbuf = rbuf[msgLength:]
                return filename, payload
        r = sock.recv(100)
        rbuf += r
        if len(r) == 0:
            if len(rbuf) != 0: # Incomplete message found. Throw error.
                print("FramedReceive: incomplete message. \n  state=%s, length=%d, rbuf=%s" % (state, msgLength, rbuf))
            return None
        if debug: print("FramedReceive: state=%s, length=%d, rbuf=%s" % (state, msgLength, rbuf))