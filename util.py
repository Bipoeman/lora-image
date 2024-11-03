import json
from typing import Literal
num_packet_before_check = 100

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

def encodeTx(byteInput: bytes,packetNo : int,totalPacket : int,packetType : Literal["image","text","json"]) -> bytes:
    typeLookup = {
        "image" : 0,
        "text" : 1,
        "json" : 2,
    }
    if (isinstance(byteInput,str)):
        byteInput = byteInput.encode()
        packetType = "text"
    if (isinstance(byteInput,dict)):
        byteInput = json.dumps(byteInput).encode()
        packetType = "json"
    packet_num = packetNo.to_bytes(3,byteorder='big')
    packet_total = totalPacket.to_bytes(3,byteorder='big')
    packet_type = typeLookup[packetType].to_bytes(1,byteorder='big')
    packet_length = len(byteInput).to_bytes(2,byteorder='big')
    output = packet_num + packet_type + packet_total + packet_length + byteInput
    output += generateFCS(output)
    return output

def decodeTx(byteInput: bytes) -> dict[Literal[
    "packet_num",
    "packet_type",
    "total_packet_count",
    "packet_size",
    "packet_content",
    "pass",
]]:
    packetTypeLookup = {
        0 : "image",
        1 : "text",
        2 : "json",
    }
    if (len(byteInput) >= 9):
        packet_num = int.from_bytes(byteInput[0:3],byteorder='big')
        packet_type = int.from_bytes(byteInput[3:4],byteorder='big')
        total_packet_count = int.from_bytes(byteInput[4:7],byteorder='big')
        packet_size = int.from_bytes(byteInput[7:9],byteorder='big')
        
        if (len(byteInput) >= 9 + packet_size + 2):
            packet_content = byteInput[9:-2]
            checkFCS = generateFCS(byteInput[:-2])
            fcs = byteInput[-2:]
            # print(packet_num,packetTypeLookup[packet_type],total_packet_count,packet_size,packet_content,fcs == checkFCS)
    return {
        "packet_num" : packet_num,
        "packet_type": packetTypeLookup[packet_type],
        "total_packet_count": total_packet_count,
        "packet_size": packet_size,
        "packet_content": packet_content,
        "pass" : fcs == checkFCS
    }

def decodeMetaData(byteInput: bytes) -> dict[Literal[
    "packet_num",
    "packet_type",
    "total_packet_count",
    "packet_size",
]]:
    packetTypeLookup = {
        0 : "image",
        1 : "text",
        2 : "json",
    }
    
    packet_num = int.from_bytes(byteInput[0:3],byteorder='big')
    packet_type = int.from_bytes(byteInput[3:4],byteorder='big')
    total_packet_count = int.from_bytes(byteInput[4:7],byteorder='big')
    packet_size = int.from_bytes(byteInput[7:9],byteorder='big')
    if (packet_type in packetTypeLookup):
        return {
            "packet_num" : packet_num,
            "packet_type": packetTypeLookup[packet_type],
            "total_packet_count": total_packet_count,
            "packet_size": packet_size,
        }
    elif (packet_type not in packetTypeLookup):
        return {
            "packet_num" : packet_num,
            "packet_type": "err",
            "total_packet_count": total_packet_count,
            "packet_size": packet_size,
        }
