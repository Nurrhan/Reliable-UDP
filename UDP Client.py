import socket
import hashlib
import os

serverPort = 12000
serverAddress = "localhost"
delimiter = "|:|:|"

while 1:
    clientSocekt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocekt.settimeout(10)
    server_address = (serverAddress, serverPort)
    userIn = raw_input("\nRequested file: ")
    message = userIn
    seqNumberFlag = 0
    f = open("r_" + userIn, 'w')

    try:
        connection_count = 0
        print 'Requesting %s' % message
        sent = clientSocekt.sendto(message, server_address)
        while 1:
            print '\nWaiting to receive..'
            try:
                data, server = clientSocekt.recvfrom(2048)
                connection_count = 0
            except:
                connection_count += 1
                if connection_count < 5:
                    print "\nConnection time out, retrying"
                    continue
                else:
                    print "\nMaximum connection trials reached, skipping request\n"
                    os.remove("r_" + userIn)
                    break
            sequenceNumber = data.split(delimiter)[1]
            clientHash = hashlib.sha1(data.split(delimiter)[3]).hexdigest()
            if data.split(delimiter)[0] == clientHash and seqNumberFlag == int(sequenceNumber == True):
                packetLength = data.split(delimiter)[2]
                if data.split(delimiter)[3] == "NONE":
                    print ("Requested file could not be found on the server")
                    os.remove("r_" + userIn)
                else:
                    f.write(data.split(delimiter)[3])
                print "Message Length: %s\nSequence Number: %s" % (packetLength, sequenceNumber)
                print "Server: %s on port %s" % server
                sent = clientSocekt.sendto(str(sequenceNumber) + "," + packetLength, server)
            else:
                print "Checksum mismatch detected, dropping packet"
                print "Server: %s on port %s" % server
                continue
            if int(packetLength) < 500:
                sequenceNumber = int(not sequenceNumber)
                break

    finally:
        print "Closing socket"
        clientSocekt.close()
        f.close()





