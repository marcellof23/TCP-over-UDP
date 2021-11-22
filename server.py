import socket
import sys


class Server():
    def __init__(self, port, file_path):
        self.localIP = "127.0.0.1"
        self.localPort = port
        self.bufferSize = 32768
        self.filePath = file_path
        self.clientList = []

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
            [message, address] = self.serverSocket.recvfrom(self.bufferSize)

            address_formatted = "(%s:%s)" % (address[0], address[1])

            print("[!] Client %s found" % (address_formatted))

            self.clientList.append(address)

            serverInput = input("[?] Listen more? (y/n) ")

            if(serverInput.lower() != 'y' and serverInput.lower() == 'n'):
                print(f'{len(self.clientList)} clients found:')
                for idx, client in enumerate(self.clientList):
                    print("%s. %s:%s" % (str(idx+1), client[0], client[1]))
                self.serverSocket.sendto(bytesToSend, address)
                break


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
