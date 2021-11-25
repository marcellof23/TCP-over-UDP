
import struct

DATA = 0b00000000
SYN = 0b00000010
ACK = 0b00010000
FIN = 0b00000001


def check_packet(flags, target):
    checker = flags & target
    checker = target == checker
    return checker


def checksum(data):
    # Jumlah smua bit per 16
    checksum = 0
    data_length = len(data)
    if (data_length % 2):
        # data += b'\0'
        data_length += 1
        data += struct.pack('!B', 0)

    for i in range(0, data_length, 2):
        checksum += data[i] << 8 + data[i+1]

    # add carry
    checksum = (checksum >> 16) + (checksum & 0xffff)

    return ~checksum & 0xffff


def pack(seq, ack, flags, fileName='', fileExtension='', data=None):
    return (struct.pack(
        '!iibbH1024s1024s32768s',
        seq,
        ack,
        flags,
        0,
        checksum(data) if data != None else 0,
        fileName.encode('utf-8') if fileName != '' else b'',
        fileExtension.encode('utf-8') if fileExtension != '' else b'',
        data if data != None else b''))


def unpack(data):
    seq, ack, flags, _, checkSum, fileName, fileExtension, data = struct.unpack(
        '!iibbH1024s1024s32768s', data)
    return (seq, ack, flags, _, checkSum, fileName, fileExtension, data)
