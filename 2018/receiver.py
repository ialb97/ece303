# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket
import struct

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

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=.02, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        #receive the data from the sender
        #check the data using the checksum
        #if it's error free, save it in a buffer according to the sequence number
        #if you get a duplicate ignore it
        #if not drop it, and wait until the sender times out to send it again
        #repeat until done
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
                    filesize = struct.unpack('l',data)[0]
                    self.simulator.u_send(full_ack)
                else:
                    pass
                    #print 'Receiver:Something done fucked up'
            except socket.timeout:
                pass

        #print filesize
        received_file = {}
        packetsreceived = 0

        while packetsreceived < filesize/float(980):
            try:
                #print "Receiver Debug: " + str(packetsreceived)
                received_data = self.simulator.u_receive()
                data = received_data[40:len(received_data)]
                data = str(data)    
                checker = str(received_data[32:len(received_data)])
                check = fletcher_chksum(checker)
                if check == received_data[0:32]:
                    #print 'Receiver:the data is correct'
                    seqnum = struct.unpack('l',received_data[32:40])[0]
                    #print seqnum
                    if seqnum not in received_file:
                        #print "BAIDNAKFJ"
                        received_file[seqnum] = data
                        packetsreceived +=1
                    ackseq = struct.pack('l',seqnum)
                    full_ack = ackseq + "ACK"
                    ackchecksum = fletcher_chksum(full_ack)
                    full_ack = str(ackchecksum) + full_ack
                    self.simulator.u_send(bytearray(full_ack))
                else:
                    pass
                   #print 'Receiver:Something done fucked up'
            except socket.timeout:
                pass
        j = long(0)
        file = open("output.txt","wb")
        while j < packetsreceived:
            file.write(received_file[j])
            j+=1

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
