# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket
import struct
from math import ceil
import hashlib

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

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=.0001, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        
        ack = struct.pack('s','ACK')
        ackchecksum = fletcher_chksum(ack)
        full_ack = str(ackchecksum) + ack
        filesize = 0
        while filesize == 0:
            try:
                received_data = self.simulator.u_receive()
                data = received_data[32:len(received_data)]
                data = str(data)
                check = fletcher_chksum(data)
                if str(check) == received_data[0:32]:
                    #print 'Receiver:the data is correct'
                    #print received_data[0:32]
                    filesize = struct.unpack('l',data)[0]
                    self.simulator.u_send(bytearray(full_ack))
                else:
                    pass
                    #print 'Receiver:Something done fucked up'
            except socket.timeout:
                pass

        #print filesize
        received_file = {}
        packetsreceived = 0
        received_data = list()
        #print filesize
        while packetsreceived < filesize/float(980):
            received_data = list()
            if packetsreceived == ceil(filesize/float(980)):
                break
                #print "Receiver Debug: " + str(packetsreceived)
            try:
                while True:
                    received_data.append(self.simulator.u_receive())
            except socket.timeout:
                self.logger.info("this is a check")
                for x in received_data:
                    data = x[40:len(x)]
                    checker = x[32:len(x)]
                    check = hashlib.md5(checker).hexdigest()#fletcher_chksum(checker)
                    if check == x[0:32]:
                #print 'Receiver:the data is correct'
                        seqnum = struct.unpack('l',x[32:40])[0]
                    #print seqnum
                        if seqnum < filesize/float(980):
                            if seqnum not in received_file:
                            #print seqnum
                            #print "BAIDNAKFJ"
                                received_file[seqnum] = data
                                packetsreceived +=1
                            ackseq = struct.pack('l',seqnum)
                            full_ack = ackseq + "ACK"
                            ackchecksum = hashlib.md5(full_ack).hexdigest()#fletcher_chksum(full_ack)
                            full_ack = ackchecksum + full_ack
                            self.simulator.u_send(bytearray(full_ack))
                            self.logger.info("Receiving {}th packet on port: {} and replying with ACK on port: {}".format(seqnum,self.inbound_port, self.outbound_port))
                   #print 'Receiver:Something done fucked up'
        j = long(0)
        #file = open("output.txt","wb")
        while j < packetsreceived:
            #file.write(received_file[j])
            sys.stdout.write(received_file[j])
            j+=1

        k = 0
        while k<5:
            ackseq = struct.pack('l',-1)
            full_ack = ackseq + "ACK"
            ackchecksum = hashlib.md5(full_ack).hexdigest()#fletcher_chksum(full_ack)
            full_ack = ackchecksum + full_ack
            self.simulator.u_send(bytearray(full_ack))
            k+=1



        #raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive()  # receive data
                 self.logger.info("Got data from socket: {}".format(
                     data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
	         sys.stdout.write(data)
                 self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()

if __name__ == "__main__":
    # test out BogoReceiver
    #rcvr = BogoReceiver()
    #rcvr.receive()
    re = Receiver()
    re.receive()
