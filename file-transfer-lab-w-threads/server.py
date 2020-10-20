#! /usr/bin/env python3

# Alan Licerio
# File Transfer
# 10-18-20

import os, socket, sys, threading, time

#sys.path.append("../lib") # for params
from lib import params
from threading import Thread
from encapFramedSock import EncapFramedSock

PATH = "./Receive" 
HOST = "127.0.0.1" # LOCALHOST

switchesVarDefaults = ( # Default switckes.
    (('1', '--listenPort'), 'listenPort', 50001),
    (('?', '--usage'), 'usage', False),
    (('d', '--debug'), 'debug', False),
)

parameterMap = params.parseParams(switchesVarDefaults)
listenPort, debug = parameterMap['listenPort'], parameterMap['debug']

if parameterMap['usage']:
    params.usage()

bindAddress = (HOST, listenPort)

# creating listening socket
listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listenSocket.bind(bindAddress)

listenSocket.listen(10) # 10 connections
print("Listening on: ", bindAddress)

# create lock
lock = threading.Lock()

class Server(Thread):

    def __init__(self, sockAddress):
        Thread.__init__(self)
        self.sock, self.address = sockAddress
        self.fsock = EncapFramedSock(sockAddress)

    def run(self):
        print("new thread handling connection from", self.address)
        while True:
            try:
                fileName, contents = self.fsock.receive(debug)
            except:
                print("Error: File transfer was not successful!")
                self.fsock.sendStatus(0, debug)
                self.fsock.close()
                sys.exit(1)

            if debug:
                print("Received", contents)

            # Data not received. Exit system.
            if fileName is None or contents is None:
                print ("Client ", self.address, " has disconnected")
                sys.exit(0)
            
            lock.acquire()
            if debug:
                time.sleep(5)
            
            fileName = fileName.decode()
            self.writeFile(fileName, contents)

            self.fsock.sendStatus(1, debug)
            lock.release()

    def writeFile(self, fileName, contents):
        if fileName is None:
            raise TypeError
        if contents is None:
            raise TypeError
        try:
            # Check if there is a directory to receive files.
            if not os.path.exists(PATH):
                os.makedirs(PATH)
            os.chdir(PATH)

            # New file to open.
            writer = open(fileName, 'w+b')
            writer.write(contents)
            writer.close()
            print("File %s received from %s" % (fileName, self.address)) # Prints output to ensure the file was received.
        except FileNotFoundError:
            print("File Not Found Error: File %s not found" % fileName) # File not found error. Exit.
            self.fsock.Status(0, debug)
            sys.exit(1)

def main():
    while True:
        sockAddress = listenSocket.accept()
        server = Server(sockAddress)
        server.start()

if __name__ == "__main__":
    main()