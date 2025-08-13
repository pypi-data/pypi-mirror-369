from MQTTNetLyzer.running_stats import StreamingStats
from MQTTNetLyzer import variables
from MQTTNetLyzer.helper_functions import add_or_initialize, total_seconds, update_or_initialize_streamingstats

class Session:

    def __init__(self, packet=None, empty_session=False, connect_packet=True):

        if empty_session:
            return
        
        self.connect_packet = connect_packet

        self.mqtt_packets_count_start = self.mqtt_packets_count_last_seen = variables.total_mqtt_packets_count

        self.start_time = packet['timeStamp']
        self.srcIP = packet['srcIP']
        self.dstIP = packet['dstIP']
        self.srcPort = packet['srcPort']
        self.dstPort = packet['dstPort']
        
        self.clientID = packet.get('clientID', '')
        self.clientIDLen = packet.get('clientIDLen', 0)
        self.username = packet.get('username', '')
        self.userLen = packet.get('userLen', 0)

        # Forward
        self.fwdWindowSize = StreamingStats(packet['windowSize'])
        self.fwdPacketLength = StreamingStats(packet['packetLength'])
        self.fwdTCPSegmentLen = StreamingStats(packet['TCPSegmentLen'])
        self.fwdIPLength = StreamingStats(packet['IPLength'])
        self.fwdTCPLength = StreamingStats(packet['TCPLength'])

        # TCP flags
        self.fwdTCPFIN = packet['tcpFIN']  # FIN flag
        self.fwdTCPSYN = packet['tcpSYN']  # SYN flag
        self.fwdTCPRST = packet['tcpRST']  # RST flag
        self.fwdTCPPSH = packet['tcpPSH']  # PSH flag
        self.fwdTCPACK = packet['tcpACK']  # ACK flag
        self.fwdTCPURG = packet['tcpURG']  # URG flag
        self.fwdTCPECE = packet['tcpECE']  # ECE flag
        self.fwdTCPCWR = packet['tcpCWR']  # CWR flag
        self.fwdTCPReserved = packet['tcpReserved']  # CWR flag

        # IP flags
        self.fwdDFFlag = packet['dfFlag'] # Don't fragment flag
        self.fwdMFFlag = packet['mfFlag'] # More fragment flag
        self.fwdRBFlag = packet['rbFlag'] # Reserved bit flag

        self.fwdTTL = StreamingStats(packet['ttl']) # Time to live- Max duration a message can be retained in a queue

        self.fwdMQTTMsgLength = StreamingStats(packet['msgLen'])
        self.fwdDUPFlag = packet['DUP']
        self.fwdQoS0 = 0
        self.fwdQoS1 = 0
        self.fwdQoS2 = 0
        if packet['QoS'] == 0:
            self.fwdQoS0 = 1
        elif packet['QoS'] == 1:
            self.fwdQoS1 = 1
        elif packet['QoS'] == 2:
            self.fwdQoS2 = 1

        # CONNECT-specific features
        if connect_packet:
            self.keepAlive = int(packet['keepAlive'])
            self.cleanSession = packet['cleanSession']
            self.willFlag = packet['willFlag']
            self.willQoS = packet['willQoS']
            self.willRetain = packet['willRetain']
            self.willmsgLen = packet['willmsgLen']
            self.willtopicLen = packet['willtopicLen']
            self.passwordFlag = packet['passwordFlag']
            self.reserved = packet['reserved']
            self.protocolName = packet['protoName']

        self.sessionID = str(self.srcIP) + '_' + str(self.srcPort) + '_' + str(self.dstIP) + '_' + str(self.dstPort)

        self.last_seen = self.start_time
        self.fwd_last_seen = self.start_time

        # IAT
        self.fwdIAT = StreamingStats()
        self.bwdIAT = StreamingStats()
        self.IAT = StreamingStats()

        self.isActive = True # Did it receive another CONNECT?
        self.isComplete = False # Did it receive DISCONNECT?
        self.connectionRefused = False
        self.fwdPacketsCount = 1
        self.bwdPacketsCount = 0
        self.fwdCommandsCount = 1
        self.bwdCommandsCount = 0

    def add_packet(self, packet, forward=True, multiple_commands_packet=False):

        if not multiple_commands_packet:
            self.check_activeness(packet['timeStamp'])
            if not self.isActive:
                return False
        else:
            if not self.isActive:
                return False
        
        if packet['type'] == 'CONNECT':
            self.isActive = False
            return False
        if packet['type'] == 'DISCONNECT':
            self.isComplete = True
        
        if not multiple_commands_packet: # First Packet

            if forward:
                update_or_initialize_streamingstats(self, 'fwdWindowSize', packet['windowSize'])
                update_or_initialize_streamingstats(self, 'fwdPacketLength', packet['packetLength'])
                update_or_initialize_streamingstats(self, 'fwdTCPSegmentLen', packet['TCPSegmentLen'])
                update_or_initialize_streamingstats(self, 'fwdIPLength', packet['IPLength'])
                update_or_initialize_streamingstats(self, 'fwdTCPLength', packet['TCPLength'])
            else:
                update_or_initialize_streamingstats(self, 'bwdWindowSize', packet['windowSize'])
                update_or_initialize_streamingstats(self, 'bwdPacketLength', packet['packetLength'])
                update_or_initialize_streamingstats(self, 'bwdTCPSegmentLen', packet['TCPSegmentLen'])
                update_or_initialize_streamingstats(self, 'bwdIPLength', packet['IPLength'])
                update_or_initialize_streamingstats(self, 'bwdTCPLength', packet['TCPLength'])

            # TCP flags
            if forward:
                add_or_initialize(self, 'fwdTCPFIN', packet['tcpFIN'])
                add_or_initialize(self, 'fwdTCPSYN', packet['tcpSYN'])
                add_or_initialize(self, 'fwdTCPRST', packet['tcpRST'])
                add_or_initialize(self, 'fwdTCPPSH', packet['tcpPSH'])
                add_or_initialize(self, 'fwdTCPACK', packet['tcpACK'])
                add_or_initialize(self, 'fwdTCPURG', packet['tcpURG'])
                add_or_initialize(self, 'fwdTCPECE', packet['tcpECE'])
                add_or_initialize(self, 'fwdTCPCWR', packet['tcpCWR'])
                add_or_initialize(self, 'fwdTCPReserved', packet['tcpReserved'])
            else:
                add_or_initialize(self, 'bwdTCPFIN', packet['tcpFIN'])
                add_or_initialize(self, 'bwdTCPSYN', packet['tcpSYN'])
                add_or_initialize(self, 'bwdTCPRST', packet['tcpRST'])
                add_or_initialize(self, 'bwdTCPPSH', packet['tcpPSH'])
                add_or_initialize(self, 'bwdTCPACK', packet['tcpACK'])
                add_or_initialize(self, 'bwdTCPURG', packet['tcpURG'])
                add_or_initialize(self, 'bwdTCPECE', packet['tcpECE'])
                add_or_initialize(self, 'bwdTCPCWR', packet['tcpCWR'])
                add_or_initialize(self, 'bwdTCPReserved', packet['tcpReserved'])

            # IP flags
            if forward:
                add_or_initialize(self, 'fwdDFFlag', packet['dfFlag'])
                add_or_initialize(self, 'fwdMFFlag', packet['mfFlag'])
                add_or_initialize(self, 'fwdRBFlag', packet['rbFlag'])
                update_or_initialize_streamingstats(self, 'fwdTTL', packet['ttl']) 
            else:
                add_or_initialize(self, 'bwdDFFlag', packet['dfFlag'])
                add_or_initialize(self, 'bwdMFFlag', packet['mfFlag'])
                add_or_initialize(self, 'bwdRBFlag', packet['rbFlag'])
                update_or_initialize_streamingstats(self, 'bwdTTL', packet['ttl'])

            if forward:
                self.fwdPacketsCount += 1
            else:
                self.bwdPacketsCount += 1
            
        if forward:
            self.fwdCommandsCount += 1
        else:
            self.bwdCommandsCount += 1

        if forward:
            update_or_initialize_streamingstats(self, 'fwdMQTTMsgLength', packet['msgLen'])
            add_or_initialize(self, 'fwdDUPFlag', packet['DUP'])
            if packet['QoS'] == 0:
                add_or_initialize(self, 'fwdQoS0', 1)
            elif packet['QoS'] == 1:
                add_or_initialize(self, 'fwdQoS1', 1)
            elif packet['QoS'] == 2:
                add_or_initialize(self, 'fwdQoS2', 1)
        else:
            update_or_initialize_streamingstats(self, 'bwdMQTTMsgLength', packet['msgLen'])
            add_or_initialize(self, 'bwdDUPFlag', packet['DUP'])

            if packet['QoS'] == 0:
                add_or_initialize(self, 'bwdQoS0', 1)
            elif packet['QoS'] == 1:
                add_or_initialize(self, 'bwdQoS1', 1)
            elif packet['QoS'] == 2:
                add_or_initialize(self, 'bwdQoS2', 1)

        # CONNACK-specific features
        if packet['type'] == 'CONNACK':
            self.connackSessionPresent = packet['sessionPresent']
            self.connackReturnCode = packet['returnCode'] # 0- Successful
            if self.connackReturnCode:
                self.isActive = False
                self.isComplete = True
                self.connectionRefused = True
            self.connackDelay = total_seconds(packet['timeStamp'], self.start_time)

        # PUBLISH-specific features
        if packet['type'] == 'PUBLISH':
            topic = packet['topic']
            if hasattr(self, 'last_seen_publish'):
                update_or_initialize_streamingstats(self, 'interPublishTime', total_seconds(packet['timeStamp'], getattr(self, 'last_seen_publish')))
            add_or_initialize(self, 'publishCount', 1)
            add_or_initialize(self, 'pubackNotReceived', 1)
            update_or_initialize_streamingstats(self, 'publishTopicLen', packet['topicLen'])
            update_or_initialize_streamingstats(self, 'publishMsgLen', len(packet['payload']))
            self.last_seen_publish = packet['timeStamp']

        # PUBACK
        if packet['type'] == 'PUBACK':
            add_or_initialize(self, 'pubackNotReceived', -1)

        # SUBSCRIBE-specific features
        if packet['type'] == 'SUBSCRIBE':
            for topic in packet['topics']:
                if isinstance(topic, tuple): # Scapy issue
                    topic = topic[0]
                update_or_initialize_streamingstats(self, 'subscribeTopicLen', len(topic))
                if hasattr(self, 'last_seen_subscribe'):
                    update_or_initialize_streamingstats(self, 'interSubscribeTime', total_seconds(packet['timeStamp'], getattr(self, 'last_seen_subscribe')))
                add_or_initialize(self, 'subscribeCount', 1)
                add_or_initialize(self, 'subackNotReceived', 1)
                self.last_seen_subscribe = packet['timeStamp']
                if '#' in topic or '+' in topic:
                    add_or_initialize(self, 'wildcardTopicCount', 1)
               
        # SUBACK-specific features
        if packet['type'] == 'SUBACK':
            add_or_initialize(self, 'subackNotReceived', -1*len(packet['returnCodes']))
            for code in packet['returnCodes']:
                if code: # 0- Successful
                    add_or_initialize(self, 'subscriptionDenied', 1)
            update_or_initialize_streamingstats(self, 'subackDelay', total_seconds(getattr(self, 'last_seen_subscribe', packet['timeStamp']), packet['timeStamp']))

        # PINGREQ
        if packet['type'] == 'PINGREQ':
            add_or_initialize(self, 'pingreqCount', 1)

        # PINGRESP
        if packet['type'] == 'PINGRESP':
            add_or_initialize(self, 'pingrespCount', 1)

        # Restricted topics    
        if len(variables.restricted_topics):
            if packet['type'] == 'PUBLISH':
                if packet['topic'] in variables.restricted_topics or '$SYS' in packet['topic']:
                    add_or_initialize(self, 'publishRestrictedTopics', 1)
            if packet['type'] == 'SUBSCRIBE':
                for topic in packet['topics']:
                    if topic in variables.restricted_topics or '$SYS' in topic:
                        add_or_initialize(self, 'subscribeRestrictedTopics', 1)

        if forward:
            self.fwdIAT.update(total_seconds(packet['timeStamp'], self.fwd_last_seen))
            self.fwd_last_seen = packet['timeStamp']
        else:
            if not hasattr(self, 'bwd_last_seen'):
                self.bwd_start_time = packet['timeStamp']
            else:
                self.bwdIAT.update(total_seconds(packet['timeStamp'], self.bwd_last_seen))
            self.bwd_last_seen = packet['timeStamp']

        self.mqtt_packets_count_last_seen = variables.total_mqtt_packets_count
        self.IAT.update(total_seconds(packet['timeStamp'], self.last_seen))
        self.last_seen = packet['timeStamp']

        return True

    def check_activeness(self, current_time):
        if not self.connect_packet:
            return True
        if total_seconds(current_time, self.last_seen) > 2*self.keepAlive:
            self.isActive = False
            return False
        return True
                
    def __str__(self):
        return f'ID: {self.sessionID}'

