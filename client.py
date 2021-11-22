import socket
import sys


class Client():
    def __init__(self, port, file_path):

        self.localIP = "127.0.0.1"
        self.clientAddressPort = (self.localIP, 10001)
        self.bufferSize = 32768
        self.serverIP = None
        self.serverPort = port
        self.filePath = file_path

        # Create a datagram socket
        self.clientSocket = None

    def socket_initilization(self):
        # Create a UDP socket at client side
        self.clientSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.clientSocket.bind(self.clientAddressPort)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def broadcast(self):
        self.clientSocket.sendto(b"", ('255.255.255.255', self.serverPort))
        [message, address] = self.clientSocket.recvfrom(self.bufferSize)
        self.serverIP = address[0]
        print("Message from Server {}".format(message))


def main():
    if (len(sys.argv) != 3):
        print("[Usage]: python client.py [port] [save file path]")
        return

    try:
        port = int(sys.argv[1])
    except:
        print("Make sure port is an integer")
        return

    file_path = sys.argv[2]
    client = Client(port, file_path)
    client.socket_initilization()
    client.broadcast()


main()
