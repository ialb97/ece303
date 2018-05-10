# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

def fletcher_chksum(data):
        sum1 = 0
        sum2 = 0
        i = 0

        while i < len(data):
            sum1 = (sum1 + data[i])%65535
            sum2 = (sum2 + sum1)%65535
            i+=1
        x = sum1*65536 + sum2
        checksum = bytearray.fromhex('{:08x}'.format(x))
        pad = bytearray(32-len(checksum))
        return pad + checksum

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
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
        ack = bytearray('ACK')
        ackchecksum = fletcher_chksum(ack)
        full_ack = ackchecksum + ack
        while True:
            try:
                received_data = self.simulator.u_receive()
                data = received_data[32:len(received_data)]
                check = fletcher_chksum(data)
                print check
                print received_data[0:32]
                if check == received_data[0:32]:
                    print 'the data is correct'
                    self.simulator.u_send(full_ack)
                else:
                    print 'Something done fucked up'
                print data
            except socket.timeout:
                sys.exit()

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
