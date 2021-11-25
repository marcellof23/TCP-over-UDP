import socket
import sys
import util
import os
from file import File


class Client():
    def __init__(self, port, file_path):
        self.localIP = "0.0.0.0"
        self.clientAddressPort = (self.localIP, 10002)
        self.bufferSize = 32768
        self.serverIP = None
        self.serverPort = port
        self.filePath = file_path
        self.current_seq = 200
        self.next_seq = 200

        try:
            os.remove(file_path)
        except:
            _ = 1

        self.file_writer = File(file_path, 'ab+')

        # Create a datagram socket
        self.clientSocket = None

        self.socket_initilization()
        self.broadcast()
        self.listen()

    def socket_initilization(self):
        # Create a UDP socket at client side
        self.clientSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.clientSocket.bind(self.clientAddressPort)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def broadcast(self):
        self.clientSocket.sendto(b"", ('255.255.255.255', self.serverPort))
        self.second_handshake()

    def second_handshake(self):
        # waiting for the first handshake
        while(True):
            seq, ack, flags, _, _, _, _, _ = self.receive()
            if (util.check_packet(flags, util.SYN)):
                print('[Segment SEQ=%s] Sent SYN+ACK' % (self.current_seq))
                # send SYN and ACK for the first handshake
                self.send(self.current_seq, seq+1, util.SYN + util.ACK)
                break
        self.finalize_handshake()

    def finalize_handshake(self):
        while(True):
            _, ack, flags, _, _, _, _, _ = self.receive()

            if (util.check_packet(flags, util.ACK) and ack == self.current_seq + 1):
                # send ACK, last handshake
                print("[Segment SEQ=%s] Acked" % (self.current_seq))
                break
        self.current_seq = ack
        print("Connection established")

    def send(self, seq, ack, flags, data=None):
        packet = util.pack(seq, ack, flags, data=data)
        self.clientSocket.sendto(packet, (self.serverIP, self.serverPort))

    def receive(self):
        data, addr = self.clientSocket.recvfrom(self.bufferSize + 64*2 + 12)

        self.serverIP = addr[0]

        seq, ack, flags, _, checkSum, fileName, fileExtension, data = util.unpack(
            data)
        return seq, ack, flags, _, checkSum, fileName, fileExtension, data

    def listen(self):
        print('Waiting for transfer data to arrive...')
        requireMetadata = False
        self.current_seq = self.next_seq = 1

        while(True):
            seq, _, flags, _, checkSum, fileName, fileExtension, data = self.receive()
            fileExtension = fileExtension.decode('utf-8').replace("\0", "")
            fileName = fileName.decode('utf-8').replace("\0", "")

            if(not requireMetadata and fileName != ''):
                requireMetadata = True
                print("File Name: {}".format(fileName))
                print("File Extension: {}".format(fileExtension))
                self.file_writer.writeMetadata(fileName, fileExtension)

            if (not util.check_packet(flags, util.FIN)):
                if(checkSum == util.checksum(data) and seq == self.next_seq):
                    self.send(0, self.next_seq, util.ACK)
                    self.file_writer.write(data)
                    print("[Segment SEQ=%s] Received, Ack Sent" %
                          (self.next_seq))
                    self.next_seq += 1
                else:
                    print("[Segment SEQ=%s] Damaged, Ack Previous Sequence Number" % (
                        self.next_seq))
                    self.send(0, self.next_seq -
                              1, util.ACK)

            else:
                self.clientSocket.close()
                break


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
    Client(port, file_path)


main()
