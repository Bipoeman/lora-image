import time
from serial import *
import os
from util import *

ser = Serial("COM8",timeout=5,baudrate=9600)
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
while True:
    read = ser.read(1513)
    if read:
        done = False
        print(f"read {len(read)} bytes")
        metaData = decodeMetaData(read[0:9])
        try:
            decoded = decodeTx(read)
            if (not decoded["pass"]):
                print("error, replying")
                reply_message = encodeTx(f"ACK{last_frame_receive}",0,1,'text')
                ser.write(reply_message)
                total_read = b''
            else:
                last_frame_receive = decoded["packet_num"]
                # print(decoded)
                if decoded["packet_num"] > 0 and (decoded["packet_num"] % num_packet_before_check == 0 or decoded["packet_num"] == decoded["total_packet_count"]) :
                    reply_message = encodeTx(f"ACK{last_frame_receive}",0,1,'text')
                    ser.write(reply_message)
                print(f"received {(decoded['packet_num']) / (decoded['total_packet_count'] - 1) * 100 :.2f}% packet no {last_frame_receive} from {decoded['total_packet_count'] - 1}")
                if decoded["packet_type"] == 'image':
                    with open(output_file,'ab') as file:
                        if (last_frame_receive > 0 and request_again == True):
                            file.seek(-1500,2)
                            request_again = False
                        file.write(decoded['packet_content'])
                        print(f"Wrote {len(decoded['packet_content'])} bytes")
                total_read = b''
                if (decoded['packet_num'] + 1) == decoded['total_packet_count']:
                    done = True
                    reply_message = encodeTx(f"ACK{last_frame_receive}", 0, 1, 'text')
                    ser.write(reply_message)  # Acknowledge final packet
        except :
            pass

    else:
        if not done:
            print(f"trying to ask for {last_frame_receive} packet")
            reply_message = encodeTx(f"ACK{last_frame_receive}",0,1,'text')
            ser.write(reply_message)
            request_again = True
        total_read = b''
        # ser.reset_input_buffer()
        # ser.reset_output_buffer()
        # ser.flush()