import json
import math
import time
from serial import *
from util import *
# def checkForAck():
    

time.sleep(2)
ser = Serial("COM4",baudrate=9600,timeout=2)

with open("image.png",'rb') as imageFile:
    content = imageFile.read()
    total_size = len(content)
    print(total_size)
    frame_size = 50
    noOfSend = math.ceil(total_size / frame_size)
    i = 0
    lastTime = 0
    startTime = time.time()
    while i < noOfSend:
        timeDiff = time.time() - lastTime
        lastTime = time.time()
        index_start = frame_size * i
        index_end = (frame_size * i) + frame_size
        transmit = encodeTx(content[index_start:index_end],i,noOfSend,'image')
        ser.write(transmit)
        # print(f"transmiting {i} {timeDiff :.2f} waiting {ser.in_waiting}")
        print(f"Send Packet {i} from {noOfSend} = {index_end / total_size*100 : .3f}% time diff : {timeDiff :.2f}s")
        if (i > 0 and i % num_packet_before_check == 0 or i == noOfSend - 1):
            print("waiting for checking reply")
            total_read : bytes = b''
            frame_len = 0
            last_frame_receive = 0
            ser.flush()
            while True:
                read = ser.read()
                if (read):
                    total_read += read
                    print(len(total_read))
                    if (len(total_read) == 9):
                        metaData = decodeMetaData(total_read)
                        # print("meta data decleared",total_read)
                        # print(metaData)
                    
                    if len(total_read) > 9 and metaData and len(total_read) >= metaData["packet_size"] + 9 + 2:
                        decoded = decodeTx(total_read)
                        # print(decoded['pass'])
                        if (decoded["pass"]):
                            # reply_message = encodeTx(f"ACK{last_frame_receive}",0,1,'text')
                            # ser.write(reply_message)
                            ack_package = decoded["packet_content"].decode().split("ACK")[1]
                            # print(ack_package,i)
                            if (int(ack_package) == i):
                                print("Check OK ✅")
                                break
                            else:
                                print("Reverting...")
                                # time.sleep(1)
                                i = int(ack_package) - 1
                                break
                        else:
                            total_read : bytes = b''   
                            # total_read = b''
                            
                else:
                    total_read = b''
                    pass
        # while (ser.in_waiting > 0):
        #     print("data coming")
            # read = ser.read()
            
        i+=1
        # print(transmit)
        
        # total_read : bytes = b''
        # frame_len = 0
        # while True:
        #     read = ser.read()
        #     total_read += read
        #     if (len(total_read) == 5):
        #         packet_no = int.from_bytes(total_read[0:2+1],byteorder="big")
        #         packet_len = int.from_bytes(total_read[3:4+1],byteorder="big")
        #         # print(packet_no,packet_len)
        #         frame_len = packet_len
        #     if (len(total_read) == 5 + frame_len + 2):
        #         fcs = total_read[-2:]
        #         packet = total_read[5:packet_len+5]
        #         all_packet = total_read[:packet_len+5]
        #         fcs_check = generateFCS(all_packet)
        #         try:
        #             ack_message = int(packet.decode().split("ACK")[1])
        #             if (fcs_check == fcs):
        #                 if ack_message == i:
        #                     print(f"Send Packet {i} from {noOfSend} = {index_end / total_size*100 : .3f}% time diff : {timeDiff :.2f}")
        #                     i+=1
        #                 else:
        #                     print(f"Failed sending Packet {ack_message} resending...")
        #                     i = ack_message
        #                 break
        #         except:
        #             break
    print(f"Total Time {time.time() - startTime : .2f}s")
        # break
        
    # for i in transmit:
    #     print(i.to_bytes(1,byteorder="big"))
    #     time.sleep(0.05)
    
    # for i in range(int(noOfSend)):
    #     transmit = encodeTx(content[i*frame_size:(i+1)*frame_size],i)
    #     ser.write(transmit)
    #     print(transmit)
        # time.sleep(0.3)
        # break

ser.close()
