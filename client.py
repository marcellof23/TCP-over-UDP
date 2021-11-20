
import socket


class Client():
    def __init__(self):

        msgFromClient = "Hello UDP Server"

        self.localIP = "127.0.0.1"
        self.bytesToSend = str.encode(msgFromClient)
        self.serverAddressPort = (self.localIP, 20001)
        self.clientAddressPort = (self.localIP, 10001)
        self.bufferSize = 1024

    def socket_initilization(self):
        # Create a UDP socket at client side

        UDPClientSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        UDPClientSocket.bind(self.clientAddressPort)

        # Send to server using created UDP socket

        UDPClientSocket.sendto(self.bytesToSend, self.serverAddressPort)

        msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)

        msg = "Message from Server {}".format(msgFromServer[0])

        print(msg)

    def broadcast(self):
        self.sock.sendto(b'', ('255.255.255.255', self.server_port))
        self.handle_handshake_request()


def main():
    client = Client()
    client.socket_initilization()


main()
