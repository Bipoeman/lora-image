import json
import math
import time
from serial import *
from util import *
import zlib
# def checkForAck():
    

time.sleep(2)
ser = Serial("COM44",baudrate=9600,timeout=5)

with open("image.jpg",'rb') as imageFile:
    time.sleep(1)
    content = imageFile.read()
    total_size = len(content)
    print(total_size)
    frame_size = 1500
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
        print(f"Send Packet {i} from {noOfSend - 1} = {index_end / total_size*100 : .3f}% time diff : {timeDiff :.4f}s total of {len(transmit)} bytes")
        if (i >= 0 and i % num_packet_before_check == 0 or i == noOfSend - 1):
            print("waiting for checking reply")
            total_read : bytes = b''
            frame_len = 0
            last_frame_receive = 0
            ser.flush()
            while True:
                read = ser.read()
                if (read):
                    total_read += read
                    # print(len(total_read))
                    if (len(total_read) == 9):
                        metaData = decodeMetaData(total_read)
                    if len(total_read) > 9 and metaData and len(total_read) >= metaData["packet_size"] + 9 + 4:
                        decoded = decodeTx(total_read)
                        print(f"return message {decoded["packet_content"]}")
                        ask_state = "ACK"
                        if (decoded["pass"]):
                            if (decoded["packet_content"].decode().find("ASK") != -1):
                                ack_package = decoded["packet_content"].decode().split("ASK")[1]
                                ask_state = "ASK"
                            elif (decoded["packet_content"].decode().find("ACK") != -1):
                                ack_package = decoded["packet_content"].decode().split("ACK")[1]
                                ask_state = "ACK"
                            if (ask_state == "ACK"):
                                if (int(ack_package) == i):
                                    print("Check OK ✅")
                                    break
                                else:
                                    print("Reverting...")
                                    i = int(ack_package) - 1
                                    break
                            elif (ask_state == "ASK"):
                                print("Ask Reverting...")
                                i = int(ack_package) - 1
                                break
                        else:
                            total_read : bytes = b''   
                            # total_read = b''
                            
                else:
                    print("No ACK received, retrying...")
                    i = max(-1, i - 1)  # Retry the last packet
                    break
        i+=1
        
    print(f"Total Time {time.time() - startTime : .2f}s")


ser.close()
