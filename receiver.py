import time
from serial import *
import os

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

def encodeTx(byteInput: bytes,packetNo : int) -> bytes:
    if (isinstance(byteInput,str)):
        byteInput = byteInput.encode()
    packet_num = packetNo.to_bytes(3,byteorder='big')
    packet_length = len(byteInput).to_bytes(2,byteorder='big')
    
    output = packet_num + packet_length + byteInput
    output += generateFCS(output)
    return output

ser = Serial("COM10",timeout=5,baudrate=115200)
try:
    ser.close()
except:
    print("Port Not Open")
try:
    os.remove("output.jpg")
    # with open("output.jpg",'wb') as file:
    #     file.write(b"")
except:
    print("File empty so not remove")
time.sleep(1)
ser.open()
total_read : bytes = b''
frame_len = 0
last_frame_receive = 0
while True:
    read = ser.read()
    if read:
        total_read += read
        if (len(total_read) == 5):
            packet_no = int.from_bytes(total_read[0:2+1],byteorder="big")
            packet_len = int.from_bytes(total_read[3:4+1],byteorder="big")
            # print(packet_no,packet_len)
            frame_len = packet_len
        if (len(total_read) == 5 + frame_len + 2):
            fcs = total_read[-2:]
            packet = total_read[5:packet_len + 5]
            all_packet = total_read[:packet_len + 5]
            fcs_check = generateFCS(all_packet)
            if (fcs_check == fcs):
                print(f"packet {packet_no} pass")
                # print(packet)
                with open("output.jpg",'ab') as output:
                    output.write(packet)
            frame_len = 0
            total_read = b''
            last_frame_receive = packet_no
            reply_message = encodeTx(f"ACK{packet_no}",0)
            ser.write(reply_message)
    else:
        reply_message = encodeTx(f"ACK{last_frame_receive}",0)
        ser.write(reply_message)
        # print("Not read")