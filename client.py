import socket


class Client():
    def __init__(self):

        self.localIP = "127.0.0.1"
        self.serverAddressPort = (self.localIP, 20001)
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

        # Send to server using created UDP socket

        self.clientSocket.sendto(bytesToSend, self.serverAddressPort)

        msgFromServer = self.clientSocket.recvfrom(self.bufferSize)

        msg = "Message from Server {}".format(msgFromServer[0])

        print(msg)

    def broadcast(self):
        self.sock.sendto(b'', ('255.255.255.255', self.server_port))
        self.handle_handshake_request()


def main():
    client = Client()
    client.socket_initilization()


main()
