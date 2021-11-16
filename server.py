
import socket


localIP = "127.0.0.1"

localPort = 20001

bufferSize = 1024


msgFromServer = "Hello UDP Client"

bytesToSend = str.encode(msgFromServer)


# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))


print(f'Server started at port {localPort}!')
print("Listening to broadcast address for clients.\n")

# Listen for incoming datagrams

clientIPList = []

while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientIP = "[!] Client {} found".format(address)

    address_merge = "%s:%s" % (address[0], address[1])
    clientIPList.append(address_merge)

    print(clientIP)
    serverInput = input("[?] Listen more? (y/n)")

    if(serverInput.lower() != 'y' and serverInput.lower() == 'n'):
        print(f'{len(clientIPList)} clients found:')
        for idx, IpClient in enumerate(clientIPList):
            print("%s. %s" % (str(idx+1), IpClient))
        break

    UDPServerSocket.sendto(bytesToSend, address)
