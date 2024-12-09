import time
from serial import *
import os
from util import *

ser = Serial("COM8",timeout=1,baudrate=250000)
output_file = "output1.txt"
try:
    ser.close()
except:
    print("Port Not Open")
try:
    os.remove(output_file)
except:
    print("File empty so not remove")
time.sleep(1)
ser.open()
total_read : bytes = b''
frame_len = 0
last_frame_receive = 0
while True:
    read = ser.read()
    # print(read)
    if read:
        total_read += read
        if (len(total_read) == 9):
            metaData = decodeMetaData(total_read)
        if len(total_read) > 9 and metaData and len(total_read) >= metaData["packet_size"] + 9 + 2:
            try:
                decoded = decodeTx(total_read)
                if (not decoded["pass"]):
                    print("error, replying")
                    reply_message = encodeTx(f"ACK{last_frame_receive+1}",0,1,'text')
                    ser.write(reply_message)
                    total_read = b''
                else:
                    last_frame_receive = decoded["packet_num"]
                    # print(last_frame_receive)
                    if decoded["packet_num"] > 0 and (decoded["packet_num"] % num_packet_before_check == 0 or decoded["packet_num"] == decoded["total_packet_count"]) :
                        reply_message = encodeTx(f"ACK{last_frame_receive}",0,1,'text')
                        ser.write(reply_message)
                    print(f"received {decoded['packet_num'] / decoded['total_packet_count'] * 100 :.2f}% packet no {last_frame_receive}")
                    if decoded["packet_type"] == 'image':
                        with open(output_file,'ab') as file:
                            file.write(decoded['packet_content'])
                    total_read = b''
            except:
                print(total_read)
                print(f"decode error trying to ask for {last_frame_receive+1} packet")
                reply_message = encodeTx(f"ACK{last_frame_receive+1}",0,1,'text')
                ser.write(reply_message)  
                total_read = b''
                # ser.reset_input_buffer()
                # ser.reset_output_buffer()
                # ser.flush()
            

    else:
        print(f"trying to ask for {last_frame_receive} packet")
        reply_message = encodeTx(f"ACK{last_frame_receive+1}",0,1,'text')
        ser.write(reply_message)
        total_read = b''
        # ser.reset_input_buffer()
        # ser.reset_output_buffer()
        # ser.flush()