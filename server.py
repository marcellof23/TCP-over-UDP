import socket
import sys
import util
import os
from file import File

WINDOW_SZ = 3
class Server():
    def __init__(self, port, file_path):
        self.localIP = "127.0.0.1"
        self.localPort = port
        self.bufferSize = 32768
        self.filePath = file_path
        self.clientList = []
        self.sendMetadata = False

        # Create a datagram socket
        self.serverSocket = None

        # Call methods
        self.socket_initilization()
        self.listen_clients()

    def socket_initilization(self):
        self.serverSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.serverSocket.bind(('0.0.0.0', self.localPort))
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f'Server started at port {self.localPort}')
        print("Listening to broadcast address for clients.\n")

    def listen_clients(self):
        # Listen for incoming datagrams
        while(True):
            [message, address] = self.serverSocket.recvfrom(self.bufferSize)

            address_formatted = "(%s:%s)" % (address[0], address[1])

            print("[!] Client %s found" % (address_formatted))

            self.clientList.append(address)

            serverInput = input("[?] Listen more? (y/n) ")

            if(serverInput.lower() != 'y' and serverInput.lower() == 'n'):
                serverInput = input("[?] Do you want to send metadata? (y/n)")
                self.sendMetadata = serverInput.lower() == 'y'
                self.print_clients()
                self.handle_transfer()
                break
    
    def print_clients(self):
        print(f'{len(self.clientList)} clients found:')
        for idx, client in enumerate(self.clientList):
            print("%s. %s:%s" % (str(idx+1), client[0], client[1]))

    def handle_transfer(self):
        msgFromServer = "Hello UDP Client"
        bytesToSend = str.encode(msgFromServer)
        for address in self.clientList:
            self.serverSocket.sendto(bytesToSend, address)


class Handler():
    def __init__(self, ip, port, socket, file_path, sendMetadata):
      self.targetIP = ip
      self.targetPort = port
      self.socket = socket
      self.current_seq = 700
      self.next_seq = 700
      self.file_metadata = os.path.splitext(file_path) if sendMetadata else None
      self.file_reader = File(file_path, 'rb',step = 32678)

      self.handshake()
      self.file_transfer()

    def handshake(self):
        print("Starting 3 Way Handshake")
        # start with sending syn
        self.send(self.current_seq, 0, util.SYN)
        print('Segment SEQ=%s Sent' % (self.current_seq))
        while(True):
            seq, ack, flags, _, _, _, _, _  = self.receive()

            # send the last ack
            if (flags == util.SYN + util.ACK and ack == self.current_seq + 1):
                print('Segment SEQ=%s Acked' % self.current_seq)
                self.send(ack, seq+1, util.ACK)
                self.current_seq = ack
                print('Segment SEQ=%s Sent' % self.current_seq)
                print('Connection established')
                break

    def send(self, seq, ack, flags, data=None):
        if (self.file_metadata != None):          
            packet = util.pack(seq, ack, flags, data=data, fileName=self.file_metadata[0], fileExtension=self.file_metadata[1])
        else:
            packet = util.pack(seq, ack, flags, data=data)
        self.sock.sendto(packet.build(data),(self.ip, self.port))

    def receive(self):
        data, _ = self.sock.recvfrom(34880)
        seq_num,ack_num,flags,_,checksum,file_name,file_extension,data = util.unpack(data)
        return seq_num,ack_num,flags,_,checksum,file_name,file_extension,data

    def go_back_N_algorithm(self):
        print('Commencing Go Back N protocol with WINDOW SIZE={}'.format(WINDOW_SZ))
        self.file_reader.offset = self.file_reader.offset - WINDOW_SZ
        self.next_seq = self.current_seq

    def file_transfer(self):
        print('Initiate to transfer the file...')
        self.socket.settimeout(1)
        self.current_seq = self.next_seq = 1
        
        while(True):
            if(self.next_seq < self.current_seq + WINDOW_SZ):
                data_block = self.file_reader.read()
                if(not data_block):
                    pass
                else:
                    self.send(seq_num=self.next_seq, ack_num=0,
                              flags=util.DATA , data=data_block)
                    print('[Segment SEQ={}] Sent'.format(self.next_seq))
                    self.next_seq = self.next_seq + 1
            try:
                seq_num, ack_num, flags, _, checksum, file_name, file_extension, data = self.receive()
                check_ACK = flags & util.ACK
                check_ACK = util.ACK == check_ACK

                if(check_ACK):
                    print('[Segment SEQ={}] Acked'.format(self.curr_seq))
                    self.curr_seq_num = ack_num + 1
                    if(self.curr_seq == self.next_seq and self.file_reader.EOF()):
                        break
                    else:
                        self.socket.settimeout(1)

            except socket.timeout:
                print('[Segment SEQ={}] NOT ACKED. SOCKET TIMEOUT or DUPLICATE ACK FOUND'.format(
                    self.curr_seq_num))
                timeout = min(timeout << 1, 10)
                self.socket.settimeout(timeout)
                self.go_back_N_algorithm()

            except:
                print('Something went wrong between file transfer..')
        
        print('Closing connection with client...')
        self.file_reader.close()
        self.send(seq_num=self.current_seq, ack_num=0, flags=util.FIN)
        self.socket.close()


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

main()
