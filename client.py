import socket
import sys


class Client():
    def __init__(self, port):

        self.broadcastIP = "255.255.255.255"
        self.localIP = '127.0.0.1'
        self.serverAddressPort = (self.broadcastIP, port)
        self.clientAddressPort = (self.localIP, 10001)
        self.bufferSize = 32768

        # Create a datagram socket
        self.clientSocket = None

    def socket_initilization(self):
        # Create a UDP socket at client side

        msgFromClient = "Hello UDP Server"
        bytesToSend = str.encode(msgFromClient)

        self.clientSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.clientSocket.bind(self.clientAddressPort)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def broadcast(self):
        msgFromClient = "Hello UDP Server"
        bytesToSend = str.encode(msgFromClient)
        self.clientSocket.sendto(bytesToSend, self.serverAddressPort)
        msgFromServer = self.clientSocket.recvfrom(self.bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)


def main():
    port = int(sys.argv[1])
    filepath = int(sys.argv[2])
    client = Client(port, filepath)
    client.socket_initilization()
    client.broadcast()


main()
