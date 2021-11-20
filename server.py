
import socket


class Server():
    def __init__(self):
        self.localIP = "127.0.0.1"
        self.localPort = 20001
        self.bufferSize = 1024
        self.msgFromServer = "Hello UDP Client"

    def socket_initilization(self):
        bytesToSend = str.encode(self.msgFromServer)

        # Create a datagram socket

        UDPServerSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Bind to address and ip

        UDPServerSocket.bind((self.localIP, self.localPort))

        print(f'Server started at port {self.localPort}')
        print("Listening to broadcast address for clients.\n")

        # Listen for incoming datagrams

        clientIPList = []

        while(True):

            bytesAddressPair = UDPServerSocket.recvfrom(self.bufferSize)

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

            UDPServerSocket.sendto(bytesToSend, address)


server = Server()
server.socket_initilization()
