# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys
import struct


def gen_packet(seq,data,packetsize):
    packet = data[packetsize*seq:packetsize*seq + packetsize]
    sequenceNum = struct.pack('l',seq)
    fullpacket = sequenceNum + packet
    checksum = fletcher_chksum(fullpacket)
    return checksum + fullpacket

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

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=.01, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    



    def send(self, data):
        #Need max sequence number, really large so don't need to deal with window
        #split into packets to send then send them
        #packet size max = 1024
        #generate a checksum --> Fletchers checksum
        #convert current sequence number to bits
        #append the sequence number and the checksum to the byte_data
        #send the data through the channel as well as start timers for each frame sent
        #receive the ACKs from the receiver
        #if either the ACKs are corrupted by checking the checksum or the ACK times out, resend the correct packet
        #repeat until done
        #need to make it so that the sequence numbers
        #Packets_to_send = {}
        #Sequence_Number = list(range(0,256))
        #Sequence_Number_bytes = 
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
        packets = {}
        packets_to_send = {}
        acks = {}
        waiting_for_acks = {}
#Testing going through 10 different packets and storing them in a dictionary based on a sequence number for easy access and deletion
        while sequence_number*packet_size < sizeofdata:
            packet = gen_packet(sequence_number,data,packet_size)
            packets[sequence_number] = packet
            sequence_number +=1
        #print sequence_number
        #print "Packet type " + str(type(packets[0]))
        i = 0
        while i<10:
            if i in packets:
                packets_to_send[i] = packets[i]
            i +=1
# #Testing the channel
        sent = 0
        seq = 9
        while sent < sequence_number-1:
            try:
                #print "Sender: SENT: " + str(sent)
                for seque,pkt in packets_to_send.items():
                    self.simulator.u_send(bytearray(pkt))
                    #print "Sender: Packet Sent!"
                    waiting_for_acks[seque] = pkt
                for pkt in waiting_for_acks:
                    received = self.simulator.u_receive()
                    checker = str(received[32:len(received)])
                    check = fletcher_chksum(checker)
                    if check == received[0:32]:
                        ackseq = struct.unpack('l',received[32:40])[0]
                        #print 'Sender:the ACK ' + str(ackseq)+ ' is correct'
                    if ackseq in waiting_for_acks:
                        del waiting_for_acks[ackseq]
                        del packets_to_send[ackseq]
                        sent = sent + 1
                        seq = seq + 1
                        if seq in packets:
                            packets_to_send[seq] = packets[seq]
                        break
                    else:
                        pass
                        #print 'Sender:Something done fucked up with the ACK'
            except socket.timeout:
                pass



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
    #DATA = bytearray(sys.stdin.read())
    #sndr = BogoSender()
    #sndr.send(DATA)
    #filename = input("File to send:")
    file = open("file_1MB.txt","r")
    input = file.read()
    se = Sender()
    se.send(input)
