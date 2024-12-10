import time
from serial import *
import os
from util import *

ser = Serial("COM45",timeout=5,baudrate=9600)
output_file = "output.jpg"
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
expected_size : int = 1
done = False
request_again = False

frame_size = 1500
f = open(output_file, "w")
f.close()
while True:
    read = ser.read(frame_size + 13)
    if read:
        done = False
        # print(f"read {len(read)} bytes")
        metaData = decodeMetaData(read[0:9])
        try:
            decoded = decodeTx(read)
            if (not decoded["pass"]):
                print("error, replying")
                reply_message = encodeTx(f"ASK{last_frame_receive}",0,1,'text')
                ser.write(reply_message)
                total_read = b''
            else:
                last_frame_receive = decoded["packet_num"]
                # if decoded["packet_num"] > 0 and (decoded["packet_num"] % num_packet_before_check == 0 or decoded["packet_num"] == decoded["total_packet_count"]) :
                #     reply_message = encodeTx(f"ACK{last_frame_receive}",0,1,'text')
                #     ser.write(reply_message)
                print(f"\033[32mreceived {(decoded['packet_num']) / (decoded['total_packet_count'] - 1) * 100 :.2f}% packet no {last_frame_receive} from {decoded['total_packet_count'] - 1}\033[39m")
                if decoded["packet_type"] == 'image':
                    with open(output_file,'rb+') as file:
                        # if (last_frame_receive > 0 and request_again == True):
                        file.seek(decoded['packet_num'] * frame_size,0)
                        print(f"\033[33mFile wrote at {decoded['packet_num'] * frame_size} for {len(decoded['packet_content'])} bytes\033[39m")
                            # request_again = False
                        file.write(decoded['packet_content'])
                        ser.flush()
                        reply_message = encodeTx(f"ACK{last_frame_receive}",0,1,'text')
                        ser.write(reply_message)
                total_read = b''
                if (decoded['packet_num'] + 1) == decoded['total_packet_count']:
                    done = True
                    reply_message = encodeTx(f"ACK{last_frame_receive}", 0, 1, 'text')
                    ser.write(reply_message)  # Acknowledge final packet
        except Exception as e:
            print(e)

    else:
        if not done:
            print(f"trying to ask for {max(last_frame_receive-1,0)} packet")
            reply_message = encodeTx(f"ASK{max(last_frame_receive-1,0)}",0,1,'text')
            ser.write(reply_message)
            # request_again = True
        total_read = b''
        # ser.reset_input_buffer()
        # ser.reset_output_buffer()
        # ser.flush()