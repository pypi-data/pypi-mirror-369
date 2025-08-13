import re
from scapy.all import TCP, IP
from scapy.contrib.mqtt import * 
from scapy.contrib.mqtt import MQTTConnect, MQTTPublish, MQTTSubscribe, MQTTUnsuback, MQTTDisconnect, MQTTPuback, MQTTPubrec, MQTTPubrel, MQTTPubcomp, MQTTSuback, MQTTUnsubscribe, MQTTConnack
from MQTTNetLyzer import variables
from datetime import datetime, timezone

COMMAND_DICT = {
        1 : MQTTConnect,
        2 : MQTTConnack,
        3 : MQTTPublish,
        4 : MQTTPuback,
        5 : MQTTPubrec,
        6 : MQTTPubrel,
        7 : MQTTPubcomp,
        8 : MQTTSubscribe,
        9 : MQTTSuback,
        10 : MQTTUnsubscribe,
        11 : MQTTUnsuback,
        14 : MQTTDisconnect,
    }

def extract_mqtt_data(packet):

    ip_layer  = packet[IP]
    tcp_layer = packet[TCP]

    window_size = tcp_layer.window
    window_scale = 1
    if tcp_layer.options:
        for option in tcp_layer.options:
            if option[0] == 'WScale':
                window_scale = 2 ** option[1]
                break
    
    calculated_window_size = window_size * window_scale

    packet_info = {
        'timeStamp': datetime.fromtimestamp(float(packet.time), timezone.utc).strftime('%d-%m-%Y %H:%M:%S.%f'),
        'srcIP' : ip_layer.src,
        'dstIP' : ip_layer.dst,
        'srcPort' : ip_layer.sport,
        'dstPort' : ip_layer.dport,
    }

    packet_info.update({
        'windowSize': calculated_window_size, # Window Size
        'packetLength': len(packet),
        'TCPSegmentLen': ip_layer.len - (ip_layer.ihl * 4) - (tcp_layer.dataofs * 4),
        'IPLength': ip_layer.len,
        'TCPLength': ip_layer.len - (ip_layer.ihl * 4),
    })

    flags = tcp_layer.flags
    flag_values = [(flags >> i) & 1 for i in range(9)]

    # TCP flags
    packet_info.update({
        'tcpFIN' : flag_values[0],  # FIN flag
        'tcpSYN' : flag_values[1],  # SYN flag
        'tcpRST' : flag_values[2],  # RST flag
        'tcpPSH' : flag_values[3],  # PSH flag
        'tcpACK' : flag_values[4],  # ACK flag
        'tcpURG' : flag_values[5],  # URG flag
        'tcpECE' : flag_values[6],  # ECE flag
        'tcpCWR' : flag_values[7],  # CWR flag
        'tcpReserved' : flag_values[8],  # CWR flag
    })
    
    # IP flags
    packet_info.update({
        'dfFlag' : int(ip_layer.flags.DF), # Don't fragment flag
        'mfFlag' : int(ip_layer.flags.MF), # More fragment flag
        'rbFlag' : (ip_layer.flags >> 2) & 0x1, # Reserved bit flag
        'ttl' : ip_layer.ttl, # Time to live
    })

    mqtt_layers = []
    mqtt_layer = packet[MQTT]
    while True:
        mqtt_layers.append(mqtt_layer)
        try:
            mqtt_layer = mqtt_layer[COMMAND_DICT[mqtt_layer.type]][MQTT]
        except Exception as e:
            break

    packet_info_list = []

    for mqtt_layer in mqtt_layers:
        try:
            packet_temp = packet_info.copy()

            packet_temp['type'] = mqtt_layer.type

            packet_temp['QoS'] = int(mqtt_layer.QOS)
            packet_temp['msgLen'] = mqtt_layer.len if mqtt_layer.len else 0
            packet_temp['DUP'] = int(mqtt_layer.DUP)

            if mqtt_layer.type == 1 and MQTTConnect in mqtt_layer:  # CONNECT
                connect_layer = mqtt_layer[MQTTConnect]    

                try:
                    client_id = getattr(connect_layer, 'clientId', '').decode('utf-8') if getattr(connect_layer, 'clientId', '') else ''
                except UnicodeDecodeError:
                    client_id = '?'.join([x.decode('utf-8') for x in re.findall(b'[ -~]+', connect_layer.clientId)])
                try:
                    username = getattr(connect_layer, 'username', '').decode('utf-8') if getattr(connect_layer, 'username', '') else ''
                except UnicodeDecodeError:
                    username = '?'.join([x.decode('utf-8') for x in re.findall(b'[ -~]+', connect_layer.username)])
                try:
                    protoname = getattr(connect_layer, 'protoname', '').decode('utf-8') if getattr(connect_layer, 'protoname', '') else ''
                except UnicodeDecodeError:
                    protoname = '?'.join([x.decode('utf-8') for x in re.findall(b'[ -~]+', connect_layer.protoname)])

                packet_temp.update({
                    'type': 'CONNECT',
                    'clientID': client_id,
                    'clientIDLen': getattr(connect_layer, 'clientIdlen', 'N/A'),
                    'username': username,
                    'userLen': getattr(connect_layer, 'userlen', 'N/A'),
                    'keepAlive': int(getattr(connect_layer, 'klive', variables.default_keep_alive)),
                    'cleanSession': getattr(connect_layer, 'cleansess', 'N/A'),
                    'willFlag': getattr(connect_layer, 'willflag', 'N/A'),
                    'willQoS': getattr(connect_layer, 'willQOSflag', 'N/A'),
                    'willRetain': getattr(connect_layer, 'willretainflag', 'N/A'),
                    'willmsgLen': getattr(connect_layer, 'wmsglen', 0),
                    'willtopicLen': getattr(connect_layer, 'wtoplen', 0),
                    'passwordFlag': getattr(connect_layer, 'passwordflag', 'N/A'),
                    'passLen': getattr(connect_layer, 'passlen', 'N/A'),
                    'reserved': getattr(connect_layer, 'reserved', 'N/A'),
                    'protoName': protoname,
                })

            elif mqtt_layer.type == 2 and MQTTConnack in mqtt_layer:  # CONNACK
                connack_layer = mqtt_layer[MQTTConnack]
                packet_temp.update({
                    'type': 'CONNACK',
                    'sessionPresent': getattr(connack_layer, 'sessPresentFlag', 'N/A'),
                    'returnCode': getattr(connack_layer, 'retcode', 'N/A'), # 1- Connected 0- Refused
                })

            elif mqtt_layer.type == 3 and MQTTPublish in mqtt_layer:  # PUBLISH
                publish_layer = mqtt_layer[MQTTPublish]
                try:
                    topic = getattr(publish_layer, 'topic', '').decode('utf-8') if getattr(publish_layer, 'topic', '') else ''
                except UnicodeDecodeError:
                    topic = '?'.join([x.decode('utf-8') for x in re.findall(b'[ -~]+', publish_layer.topic)])
                packet_temp.update({
                    'type': 'PUBLISH',
                    'topic': topic,
                    'topicLen': getattr(publish_layer, 'length', 0),
                    'messageID': publish_layer.msgid,
                    'payload': getattr(publish_layer, 'value', '')})

            elif mqtt_layer.type == 4 and MQTTPuback in mqtt_layer:  # PUBACK
                packet_temp.update({
                    'type': 'PUBACK',
                    'messageID': mqtt_layer[MQTTPuback].msgid
                })

            elif mqtt_layer.type == 5 and MQTTPubrec in mqtt_layer:  # PUBREC
                packet_temp.update({
                    'type': 'PUBREC',
                    'messageID': mqtt_layer[MQTTPubrec].msgid
                })

            elif mqtt_layer.type == 6 and MQTTPubrel in mqtt_layer:  # PUBREL
                packet_temp.update({
                    'type': 'PUBREL',
                    'messageID': mqtt_layer[MQTTPubrel].msgid
                })

            elif mqtt_layer.type == 7 and MQTTPubcomp in mqtt_layer:  # PUBCOMP
                packet_temp.update({
                    'type': 'PUBCOMP',
                    'messageID': mqtt_layer[MQTTPubcomp].msgid
                })

            elif mqtt_layer.type == 8 and MQTTSubscribe in mqtt_layer:  # SUBSCRIBE
                try:
                    topics = [(topic.topic.decode('utf-8'), topic.QOS) for topic in mqtt_layer[MQTTSubscribe].topics]
                except UnicodeDecodeError:
                    topics = [('?'.join([x.decode('utf-8') for x in re.findall(b'[ -~]+', topic.topic)]), topic.QOS) for topic in mqtt_layer[MQTTSubscribe].topics]
                packet_temp.update({
                    'type': 'SUBSCRIBE',
                    'topics': topics,
                    'messageID': mqtt_layer[MQTTSubscribe].msgid
                })

            elif mqtt_layer.type == 9 and MQTTSuback in mqtt_layer:  # SUBACK
                suback_layer = mqtt_layer[MQTTSuback]
                packet_temp.update({
                    'type': 'SUBACK',
                    'messageID': getattr(suback_layer, 'msgid', 'N/A'),  # Safe access
                    'returnCodes': [int(code) for code in getattr(suback_layer, 'retcodes', [])],
                })

            elif mqtt_layer.type == 10 and MQTTUnsubscribe in mqtt_layer:  # UNSUBSCRIBE
                try:
                    topics = [topic.topic.decode('utf-8') for topic in mqtt_layer[MQTTUnsubscribe].topics]
                except UnicodeDecodeError:
                    topics = ['?'.join([x.decode('utf-8') for x in re.findall(b'[ -~]+', topic.topic)]) for topic in mqtt_layer[MQTTUnsubscribe].topics]
                packet_temp.update({
                    'type': 'UNSUBSCRIBE',
                    'topics': topics,
                    'messageID': mqtt_layer[MQTTUnsubscribe].msgid
                })

            elif mqtt_layer.type == 11 and MQTTUnsuback in mqtt_layer:  # UNSUBACK
                packet_temp.update({
                    'type': 'UNSUBACK',
                    'messageID': mqtt_layer[MQTTUnsuback].msgid
                })

            elif mqtt_layer.type == 12:  # PINGREQ 
                packet_temp.update({     
                    'type': 'PINGREQ' 
                })

            elif mqtt_layer.type == 13:  # PINGRESP
                packet_temp.update({
                    'type': 'PINGRESP'
                })

            elif mqtt_layer.type == 14:  # DISCONNECT
                packet_temp.update({
                    'type': 'DISCONNECT'
                })
            
            packet_info_list.append(packet_temp.copy())
            
        except Exception as e:
            continue

    return packet_info_list