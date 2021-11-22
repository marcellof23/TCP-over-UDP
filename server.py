import socket
import sys


class Server():
    def __init__(self, port):
        self.localIP = ''
        self.serverAddressPort = (self.localIP, port)
        self.bufferSize = 32768

        # Create a datagram socket
        self.serverSocket = None

    def socket_initilization(self):

        msgFromServer = "Hello UDP Client"
        bytesToSend = str.encode(msgFromServer)

        # Bind to address and ip
        self.serverSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.serverSocket.bind(self.serverAddressPort)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f'Server started at port {self.serverAddressPort}')
        print("Listening to broadcast address for clients.\n")

        # Listen for incoming datagrams

        clientIPList = []

        while(True):

            bytesAddressPair = self.serverSocket.recvfrom(self.bufferSize)

            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            address_merge = "%s:%s" % (address[0], address[1])

            clientIP = "[!] Client {} found".format(address_merge)

            clientIPList.append(address_merge)

            print(clientIP)
            serverInput = input("[?] Listen more? (y/n)")

            if(serverInput.lower() != 'y' and serverInput.lower() == 'n'):
                clientIPList.pop()
                print(f'{len(clientIPList)} clients found:')
                for idx, IpClient in enumerate(clientIPList):
                    print("%s. %s" % (str(idx+1), IpClient))
                break

            self.serverSocket.sendto(bytesToSend, address)


def main():
    port = int(sys.argv[1])
    server = Server(port)
    server.socket_initilization()


main()
