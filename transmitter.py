import math
import time
from serial import *

def generateFCS(data_in : bytes,poly: int = 0x1021, initial_value: int = 0xFFFF):
    crc = initial_value
    for byte in data_in:
        crc ^= byte << 8  # Move byte to upper 8 bits of crc
        for _ in range(8):  # Process each bit
            if crc & 0x8000:  # If the leftmost bit is set
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF  # Ensure crc stays within 16 bits

    # HDLC AX.25 uses a bitwise inversion of the CRC before appending it to the frame
    crc ^= 0xFFFF
    # Return the FCS as 2 bytes (big-endian)
    return crc.to_bytes(2,byteorder="big")  # Little-endian is used for AX.25

def encodeTx(byteInput: bytes,packetNo : int,totalPacket : int) -> bytes:
    if (isinstance(byteInput,str)):
        byteInput = byteInput.encode()
    packet_num = packetNo.to_bytes(3,byteorder='big')
    packet_total = totalPacket.to_bytes(3,byteorder='big')
    packet_length = len(byteInput).to_bytes(2,byteorder='big')
    
    output = packet_num + packet_total + packet_length + byteInput
    output += generateFCS(output)
    return output

# def checkForAck():
    

time.sleep(2)
ser = Serial("COM7",baudrate=115200,timeout=2)

with open("image.jpg",'rb') as imageFile:
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
        transmit = encodeTx(content[index_start:index_end],i,noOfSend)
        ser.write(transmit)
        # print(transmit)
        
        total_read : bytes = b''
        frame_len = 0
        while True:
            read = ser.read()
            total_read += read
            if (len(total_read) == 5):
                packet_no = int.from_bytes(total_read[0:2+1],byteorder="big")
                packet_len = int.from_bytes(total_read[3:4+1],byteorder="big")
                # print(packet_no,packet_len)
                frame_len = packet_len
            if (len(total_read) == 5 + frame_len + 2):
                fcs = total_read[-2:]
                packet = total_read[5:packet_len+5]
                all_packet = total_read[:packet_len+5]
                fcs_check = generateFCS(all_packet)
                try:
                    ack_message = int(packet.decode().split("ACK")[1])
                    if (fcs_check == fcs):
                        if ack_message == i:
                            print(f"Send Packet {i} from {noOfSend} = {index_end / total_size*100 : .3f}% time diff : {timeDiff :.2f}")
                            i+=1
                        else:
                            print(f"Failed sending Packet {ack_message} resending...")
                            i = ack_message
                        break
                except:
                    break
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
