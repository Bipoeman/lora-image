|Byte No.|Data|
|--------|----|
|0 to 2|Packet No.|
|3 to 5|Total Packet|
|6 to 7|Packet Length|
|6 to (6 + Packet Length)|Packet Content|
|last 2-4 bytes|FCS|

![Protocol Diagram](RepeaterCommunication.svg)