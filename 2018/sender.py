# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys
import struct
from math import ceil
import hashlib


def gen_packet(seq,data,packetsize):
    packet = data[packetsize*seq:packetsize*seq + packetsize]
    sequenceNum = struct.pack('l',seq)
    fullpacket = sequenceNum + packet
    #checksum = fletcher_chksum(fullpacket)
    #return checksum + fullpacket
    out =hashlib.md5(bytearray(fullpacket)).hexdigest()
    #print len(out)
    #print type(fullpacket)
    #print "Sent " + str(out)
    return hashlib.md5(bytearray(fullpacket)).hexdigest()+fullpacket

def fletcher_chksum(data):
        sum1 = 0
        sum2 = 0
        i = 0
        while i < len(data):
            sum1 = (sum1 + ord(data[i]))%65535
            sum2 = (sum2 + sum1)%65535
            i+=1
        x = sum1*65536 + sum2
        checksum = bytearray.fromhex('{:08x}'.format(x))
        pad = bytearray(32-len(checksum))
        return pad + checksum

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=.0001, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    



    def send(self, data):
        packet_size = 980
        location_in_data = 0
        byte_data = bytearray(data)
        sizeofdata = len(data)
#need to generate a packet which contains the size of the file to tell the receiver how much it is getting
        #sizeofmessage = len(byte_data)
        sizeofmessagebytes = struct.pack('l',sizeofdata)#bytearray([sizeofmessage])
        size_checksum = fletcher_chksum(sizeofmessagebytes)
        size_checksum = str(size_checksum)
        firstpacket = size_checksum + sizeofmessagebytes
        ackofsize = None
        while not ackofsize:
            try:
                self.simulator.u_send(bytearray(firstpacket))
                ackofsize = self.simulator.u_receive()
                #print 'Sender: Connection established'
            except socket.timeout:
                pass
            
        
        sequence_number = long(0)
        packets_to_send = {}
        acks = {}
        waiting_for_acks = {}
#Testing going through 10 different packets and storing them in a dictionary based on a sequence number for easy access and deletion
        #while sequence_number*packet_size < sizeofdata:
         #   packet = gen_packet(sequence_number,data,packet_size)
          #  packets[sequence_number] = packet
           # sequence_number +=1
        #print sequence_number
        #print "Packet type " + str(type(packets[0]))
        i = 0
        seq = 0
        sequence_number = ceil(sizeofdata/float(packet_size))
        while i<10:
            if i < sequence_number:
                packets_to_send[i] = gen_packet(i,data,packet_size)#packets[i]
                seq+=1
            i +=1
# #Testing the channel
        sent = 0
        seq-=1
        while sent < sequence_number:
            #print "Sender: SENT: " + str(sent)
            self.logger.info("TEST")
            waiting_for_acks.clear()
            for seque,pkt in packets_to_send.items():
                self.simulator.u_send(bytearray(pkt))
                self.logger.info("Sending {}th packet on port: {}".format(seque,self.outbound_port))
                #print "Sender: Packet Sent!"
                waiting_for_acks[seque] = pkt
            for pack in waiting_for_acks:
                try:
                    self.logger.info("THIS IS A CHECK")
                    received = self.simulator.u_receive()
                    checker = str(received[32:len(received)])
                    check = hashlib.md5(checker).hexdigest()#fletcher_chksum(checker)
                    if check == received[0:32]:
                        ackseq = struct.unpack('l',received[32:40])[0]
                        self.logger.info("Receiving {}th ACK on port: {}".format(ackseq,self.inbound_port, ))
                    if ackseq == -1:
                        sys.exit()
                    #print "Sender: " + str(ackseq)
                            #print 'Sender:the ACK ' + str(ackseq)+ ' is correct'
                    if ackseq in packets_to_send:
                        #del waiting_for_acks[ackseq]
                        del packets_to_send[ackseq]
                        sent = sent + 1
                        seq = seq + 1
                        if seq < sequence_number:
                            packets_to_send[seq] = gen_packet(seq,data,packet_size)
                        #waiting_for_acks[seq]= packets_to_send[seq]
                            #self.simulator.u_send(bytearray(packets_to_send[seq]))
                    else:
                        pass
                except socket.timeout:
                    pass
                        #print 'Sender:Something done fucked up with the ACK'
        #raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass


if __name__ == "__main__":
    # test out BogoSender
    DATA = sys.stdin.read()
    #sndr = BogoSender()
    #filename = input("File to send:")
    #file = open("re10MB.txt","r")
    #input = file.read()
    se = Sender()
    se.send(DATA)
