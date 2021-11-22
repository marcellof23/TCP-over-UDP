import socket
import sys
import util
import os
from file import File
class Client():
    def __init__(self, port, file_path):

        self.localIP = "127.0.0.1"
        self.clientAddressPort = (self.localIP, 10001)
        self.bufferSize = 32768
        self.serverIP = None
        self.serverPort = port
        self.filePath = file_path
        self.current_seq = 200
        self.next_seq = 200
        self.file_writer = File(file_path,'ab+')

        # Create a datagram socket
        self.clientSocket = None

        self.socket_initilization()
        self.broadcast()

    def socket_initilization(self):
        # Create a UDP socket at client side
        self.clientSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.clientSocket.bind(self.clientAddressPort)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def broadcast(self):
        self.clientSocket.sendto(b"", ('255.255.255.255', self.serverPort))
        self.handshake()
        
    def handshake(self):
        while(True):
            seq, ack, flags, _, _, _, _, _ = self.receive()
            check_SYN = flags & util.SYN == util.SYN
            check_ACK = flags & util.ACK == util.ACK

            if (check_SYN):
                # send SYN and ACK, first handshake
                self.send(self.current_seq, seq+1, util.SYN + util.ACK)
                print('Segment SEQ=%s Sent SYN+ACK' % (self.current_seq))
            elif (check_ACK and ack == self.current_seq + 1):
                # send ACK, last handshake
                print("Segment SEQ=%s Acked" % (self.current_seq))
                self.current_seq = ack
                print("Connection established")
                break
    
    def send(self, seq_num, ack_num, flags):
        packet = util.pack(seq_num, ack_num, flags, False, None)
        self.clientSocket.sendto(packet.build(),(self.serverIP, self.serverPort))

    def receive(self):
        data, addr = self.clientSocket.recvfrom(34880)

        self.server_ip = addr[0]

        seq,ack,flags,_,checkSum,fileName,fileExtension,data = util.unpack(data)
        return seq,ack,flags,_,checkSum,fileName,fileExtension,data

    def listen(self):
        print('Waiting for transfer data to arrive...')
        requireMetadata = False
        self.current_seq = self.next_seq = 1
        

        while(True):
            seq,_,flags,_,checkSum,fileName,fileExtension,data = self.receive()
            fileExtension = fileExtension.decode('utf-8').replace("\0","")
            fileName = fileName.decode('utf-8').replace("\0","")
        
            if(not requireMetadata and fileName != ''):
                requireMetadata = True
                print("File Name: {}".format(fileName))
                print("File Extension: {}".format(fileExtension))
                
            check_FIN = flags & util.FIN
            check_FIN = util.FIN == check_FIN

            if (not check_FIN):
                if(checkSum == util.checkSum(data) and seq == self.next_seq): 
                    self.send(seq=0, ack=self.next_seq, flags=util.ACK)
                    self.file_writer.write(data)
                    print("Segment SEQ=%s Received, Ack Sent" % (self.next_seq))
                    self.next_seq += 1
                else:
                    print("Segment SEQ=%s Damaged, Ack Previous Sequence Number" % (self.next_seq))                  
                    self.send(seq_num=0, ack_num=self.next_seq - 1, flags= util.ACK)

            else:
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
    client = Client(port, file_path)


main()
