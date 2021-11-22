
import struct

SYN = 0b00000010
ACK = 0b00010000
FIN = 0b00000001
DATA = 0b00000000

def checksum(data):
    data_length = len(data)
    if (data_length % 2 == 1):
      data += b'\0'

    # Jumlah smua bit per 16
    result = 0
    for i in range(0, data_length, 2):
        result += data[i] << 8 + data[i+1]

    # add carry
    result = (result >> 16) + (result & 0xffff)

    return ~result & 0xffff
    

def pack(seq, ack, flags, fileName='', fileExtension='', data=None):
    return (struct.pack(
        '!4s4s1s1s2s1024s1024s32768s',
        seq,
        ack,
        flags,
        0,
        checksum(data),
        fileName.encode('utf-8') if fileName != '' else b'',
        fileExtension.encode('utf-8') if fileExtension != '' else b'',
        data if data != None else b''))

def unpack(data):
    seq,ack,flags,_,checkSum,fileName,fileExtension,data = struct.unpack('!4s4s1s1s2s1024s1024s32768s', data)
    return (seq,ack,flags,_,checkSum,fileName,fileExtension,data)
