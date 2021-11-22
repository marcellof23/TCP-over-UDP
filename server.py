import socket
import sys


class Server():
<<<<<<< HEAD
    def __init__(self, port):
        self.localIP = ''
        self.serverAddressPort = (self.localIP, port)
=======
    def __init__(self, port, file_path):
        self.localIP = "127.0.0.1"
        self.localPort = port
>>>>>>> 4ade557030f7cfb7e8223a6c7573cea6d0328a83
        self.bufferSize = 32768
        self.filePath = file_path
        self.clientIPList = []

        # Create a datagram socket
        self.serverSocket = None

    def socket_initilization(self):
        self.serverSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.serverSocket.bind(self.serverAddressPort)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f'Server started at port {self.serverAddressPort}')
        print("Listening to broadcast address for clients.\n")

    def listen_clients(self):
        msgFromServer = "Hello UDP Client"
        bytesToSend = str.encode(msgFromServer)

        # Listen for incoming datagrams
        while(True):
            bytesAddressPair = self.serverSocket.recvfrom(self.bufferSize)

            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            address_merge = "%s:%s" % (address[0], address[1])

            clientIP = "[!] Client {} found".format(address_merge)

            self.clientIPList.append(address_merge)

            print(clientIP)
            serverInput = input("[?] Listen more? (y/n)")

            if(serverInput.lower() != 'y' and serverInput.lower() == 'n'):
                print(f'{len(self.clientIPList)} clients found:')
                for idx, IpClient in enumerate(self.clientIPList):
                    print("%s. %s" % (str(idx+1), IpClient))
                break

            self.serverSocket.sendto(bytesToSend, address)


def main():
    if (len(sys.argv) != 3):
        print("[Usage]: python server.py [port] [file path]")
        return

    try:
        port = int(sys.argv[1])
    except:
        print("Make sure port is an integer")
        return

    file_path = sys.argv[2]
    server = Server(port, file_path)
    server.socket_initilization()
    server.listen_clients()


main()
