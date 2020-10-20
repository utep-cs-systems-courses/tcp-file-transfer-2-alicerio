#! /usr/bin/env python3

import os, re, socket, sys
from framedSock import framedSend, framedReceive

#sys.path.append("../lib") # for params
from lib import params


PATH = "Send/"

def client():
    switchesVarDefaults = ( # Default switches.
        (('1', '--server'), 'server', "127.0.0.1:50001"),
        (('?', '--usage'), 'usage', False),
        (('d', '--debug'), 'debug', False),
    )

    parameterMap = params.parseParams(switchesVarDefaults)
    server, usage, debug = parameterMap['server'], parameterMap['usage'], parameterMap['debug']

    if usage:
        params.usage() # Calls method from given file params.

    try:
        serverHost, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server) # Server could not be found.
        sys.exit(1)

    port = (serverHost, serverPort)

    # create socket
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenSocket.connect(port)

    while True:
        fileName = input("> ")
        fileName.strip()

        if fileName == "exit": #Exit program if file name matches condition.
            sys.exit(0)
        else:
            if not fileName:
                continue
            elif os.path.exists(PATH + fileName):
                f = open(PATH + fileName, "rb")
                contents = f.read()

                if len(contents) <= 0: # Error if the file is empty.
                    print("Error: File %s is empty" % fileName)
                    continue
                
                framedSend(listenSocket, fileName, contents, debug)

                # Checks if server received the file.
                status = int(listenSocket.recv(1024).decode())

                if status:
                    print("File %s received by server." % fileName)
                    sys.exit(0)
                else: # File not received and exit with error.
                    print("File Transfer Error: File %s was not received by server." % fileName)
                    sys.exit(1)
            else: # File was not found. Repeat loop.
                print("File Not Found Error: File %s not found!" % fileName)

if __name__ == "__main__":
    client()