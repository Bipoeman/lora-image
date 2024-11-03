|Byte No.|Data|
|--------|----|
|0 to 2|Packet No.|
|3|Packet Type|
|4 to 6|Total Number of Packet|
|7 to 8|Packet Length|
|9 to (9 + Packet Length)|Packet Content|
|last 2-4 bytes|FCS|

![Protocol Diagram](RepeaterCommunication.svg)