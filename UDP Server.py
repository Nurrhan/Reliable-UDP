import socket
import threading
import hashlib
import time
import datetime
import random

serverPort = 12000
serverAddress = "localhost"
delimiter = "|:|:|"
packetLoss = False
sequenceFlag = 0

class packet():
    message = 0
    sequenceNumber = 0
    checksum = 0
    length = 0

    def makePacket(self, data):
        self.message = data
        self.length = str(len(data))
        self.checksum = hashlib.sha1(data).hexdigest()
        print "Message Length: %s\nSequence Number: %s" % (self.length, self.sequenceNumber)


def connection(address, data):
    packet_dropped = 0
    packet_count = 0
    time.sleep(0.5)
    if packetLoss:
        packet_loss_percentage = float(raw_input("Set Packet Loss Percentage (0-99)%: "))/100.0
        while packet_loss_percentage < 0 or packet_loss_percentage >= 1:
          packet_loss_percentage = float(raw_input("Enter a valid Packet Loss Percentage value."
                                                   " Set Packet Loss Percentage (0-99)%: "))/100.0
    else:
        packet_loss_percentage = 0
    pkt = packet()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:

        try:
            print "Opening file %s" % data
            inFile = open(data, 'r')
            data = inFile.read()
            inFile.close()
        except:
            message = "NONE"
            pkt.makePacket(message)
            lastPacket = str(pkt.checksum) + delimiter + str(pkt.sequenceNumber) + delimiter + str(pkt.length) \
                         + delimiter + pkt.message
            serverSocket.sendto(lastPacket, address)
            print "Requested file could not be found, replied with NONE"
            return

        x = 0
        while x < (len(data) / 500) + 1:
            packet_count += 1
            randomised_plp = random.random()
            if packet_loss_percentage < randomised_plp:
                message = data[x * 500:x * 500 + 500]
                pkt.makePacket(message)
                lastPacket = str(pkt.checksum) + delimiter + str(pkt.sequenceNumber) + delimiter + str(
                    pkt.length) + delimiter + pkt.message

                sent = serverSocket.sendto(lastPacket, address)
                print 'Sent %s bytes back to %s, awaiting acknowledgment..' % (sent, address)
                serverSocket.settimeout(2)
                try:
                    ack, address = serverSocket.recvfrom(100)
                except:
                    print "Time out reached, resending ...%s" % x
                    continue
                if ack.split(",")[0] == str(pkt.sequenceNumber):
                    pkt.sequenceNumber = int(not pkt.sequenceNumber)
                    print "Acknowledged by: " + ack
                    x += 1
            else:
                print "\n----------\n\t\tDropped packet\n-------------\n"
                packet_dropped += 1
        print "Packets served: " + str(packet_count)
        if packetLoss:
            print "Dropped packets: " + str(packet_dropped)+"\nComputed drop rate: %.2f" \
                  % float(float(packet_dropped)/float(packet_count)*100.0)
    except:
        print "Internal server error"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (serverAddress, serverPort)
print 'Starting up on %s port %s' % server_address
sock.bind(server_address)
while True:
    print 'Waiting to receive message'
    data, address = sock.recvfrom(600)
    connectionThread = threading.Thread(target=connection, args=(address, data))
    connectionThread.start()
    print 'Received %s bytes from %s' % (len(data), address)
