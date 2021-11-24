import socket
import sys
import util
import os
import concurrent.futures
import requests
from file import File

WINDOW_SZ = 10
MAXIMUM_CLIENTS = 5


class Server():
    def __init__(self, port, file_path, activate_conccurent):
        self.localIP = "127.0.0.1"
        self.localPort = port
        self.bufferSize = 32768
        self.filePath = file_path
        self.clientList = []
        self.sendMetadata = False
        self.activate_conccurent = activate_conccurent
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
            [message, address] = self.serverSocket.recvfrom(32832)

            address_formatted = "(%s:%s)" % (address[0], address[1])

            print("[!] Client %s found" % (address_formatted))

            self.clientList.append(address)

            serverInput = input("[?] Listen more? (y/n) ")

            if(serverInput.lower() != 'y' and serverInput.lower() == 'n'):
                serverInput = input("[?] Do you want to send metadata? (y/n)")
                self.sendMetadata = serverInput.lower() == 'y'
                self.print_clients()
                if(self.activate_conccurent):
                    self.handle_transfer_with_thread()
                else:
                    self.handle_transfer()
                break

                # Eric is here

    def print_clients(self):
        print(f'{len(self.clientList)} clients found:')
        for idx, client in enumerate(self.clientList):
            print("%s. %s:%s" % (str(idx+1), client[0], client[1]))

    def handle_transfer(self):
        for address in self.clientList:
            Handler(address[0], address[1], self.serverSocket,
                    self.filePath, self.sendMetadata)
        self.serverSocket.close()

    def handle_transfer_with_thread(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAXIMUM_CLIENTS) as executor:
            futures = []
            for client_address in self.clientList:
                client_address_ip = client_address[0]
                client_address_port = client_address[1]
                futures.append(
                    executor.submit(
                        Handler, client_address_ip, client_address_port, self.serverSocket,
                        self.filePath, self.sendMetadata
                    )
                )
            for future in concurrent.futures.as_completed(futures):
                print(future.result())
        self.serverSocket.close()


class Handler():
    def __init__(self, ip, port, socket, file_path, sendMetadata):
        self.targetIP = ip
        self.targetPort = port
        self.socket = socket
        self.current_seq = 700
        self.next_seq = 700
        self.file_metadata = os.path.splitext(
            file_path) if sendMetadata else None
        self.file_reader = File(file_path, 'rb', step=32678)

        self.first_handshake()
        self.file_transfer()

    def first_handshake(self):
        self.send(self.current_seq, 0, util.SYN)
        print('Segment SEQ=%s Sent' % (self.current_seq))
        self.third_handshake()

    def third_handshake(self):
        # waiting for the second handshake
        while(True):
            seq, ack, flags, _, _, _, _, _ = self.receive()
            if (flags == util.SYN + util.ACK and ack == self.current_seq + 1):
                print('Segment SEQ=%s Acked' % self.current_seq)
                break
        # send the last ack
        self.send(ack, seq+1, util.ACK)
        self.current_seq = ack
        print('Segment SEQ=%s Sent' % self.current_seq)
        print('Connection established')

    def send(self, seq, ack, flags, data=None):
        if (self.file_metadata != None):
            packet = util.pack(seq, ack, flags, data=data,
                               fileName=self.file_metadata[0], fileExtension=self.file_metadata[1])
        else:
            packet = util.pack(seq, ack, flags, data=data)
        print((self.targetIP, self.targetPort))
        self.socket.sendto(packet, (self.targetIP, self.targetPort))

    def receive(self):
        data, _ = self.socket.recvfrom(34880)
        seq_num, ack_num, flags, _, checksum, fileName, file_extension, data = util.unpack(
            data)
        return seq_num, ack_num, flags, _, checksum, fileName, file_extension, data

    def go_back_N_algorithm(self):
        print('Commencing Go Back N protocol with WINDOW SIZE={}'.format(WINDOW_SZ))
        if(self.file_reader.offset > self.file_reader.step * 3):
            self.file_reader.offset -= (WINDOW_SZ * self.file_reader.step)
            self.next_seq = self.current_seq

    def read_file(self):
        return self.file_reader.read()

    def send_file_packets(self, data_block):
        self.send(seq=self.next_seq, ack=0,
                  flags=util.DATA, data=data_block)
        print('[Segment SEQ={}] Sent'.format(self.next_seq))
        self.next_seq = self.next_seq + 1

    def check_transfer_finished(self):
        return self.current_seq == self.next_seq and self.file_reader.is_EOF()

    def file_transfer(self):
        print('Initiate to transfer the file...')
        self.timeout = 1
        self.socket.settimeout(self.timeout)
        self.current_seq = self.next_seq = 1

        while(True):
            if(self.next_seq < self.current_seq + WINDOW_SZ):
                data_block = self.read_file()
                if(not data_block):
                    pass
                else:
                    self.send_file_packets(data_block)
            try:
                _, ack, flags, _, _, _, _, _ = self.receive()
                if(util.check_packet(flags, util.ACK)):
                    self.current_seq = ack + 1
                    finished = self.check_transfer_finished()
                    if (finished):
                        break
                    else:
                        self.timeout = 1
                        self.socket.settimeout(self.timeout)

            except socket.timeout:
                print('[Segment SEQ={}] NOT ACKED. SOCKET TIMEOUT or DUPLICATE ACK FOUND'.format(
                    self.current_seq))
                self.timeout = min(self.timeout << 1, 10)
                self.socket.settimeout(self.timeout)
                self.go_back_N_algorithm()

        print('Closing connection with client...')
        self.file_reader.close()
        self.send(seq=self.current_seq, ack=0, flags=util.FIN)


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
    server = Server(port, file_path, True)


main()
