from MQTTNetLyzer import variables
from MQTTNetLyzer.helper_functions import get_stats, get_value, total_seconds
from MQTTNetLyzer.running_stats import StreamingStats

def calculate_features(session):

    session_features = {}

    session_features.update({
        'ID' : get_value(session, 'sessionID'),
        'srcIP' : get_value(session, 'srcIP'),
        'dstIP' : get_value(session, 'dstIP'),
        'srcPort' : get_value(session, 'srcPort'),
        'dstPort' : get_value(session, 'dstPort'),
        'startTime' : get_value(session, 'start_time'),
        'endTime' : get_value(session, 'last_seen'),
        'duration' : total_seconds(get_value(session, 'last_seen'), get_value(session, 'start_time')),
        'fwdPacketsCount' : get_value(session, 'fwdPacketsCount', 0),
        'bwdPacketsCount' : get_value(session, 'bwdPacketsCount', 0),
        'packetsCount' : get_value(session, 'fwdPacketsCount', 0) + get_value(session, 'bwdPacketsCount', 0),
        'fwdCommandsCount' : get_value(session, 'fwdCommandsCount', 0),
        'bwdCommandsCount' : get_value(session, 'bwdCommandsCount', 0),
        'commandsCount' : get_value(session, 'fwdCommandsCount', 0) + get_value(session, 'bwdCommandsCount', 0),
        'clientID' : get_value(session, 'clientID', ''),
        'clientIDLen' : get_value(session, 'clientIDLen', ''),
        'username' : get_value(session, 'username', ''),
        'usernameLen' : get_value(session, 'userLen', ''),
        'isComplete' : get_value(session, 'isComplete'),
    })

    session_features.update({
        'connectionRefused' : get_value(session, 'connectionRefused', False),
    })

    fwd_duration = total_seconds(get_value(session, 'fwd_last_seen'), get_value(session, 'start_time'))
    bwd_duration = total_seconds(get_value(session, 'bwd_last_seen'), get_value(session, 'bwd_start_time'))
    duration = total_seconds(get_value(session, 'last_seen'), get_value(session, 'start_time'))
    session_features.update({
        'fwdThroughput' : int(get_value(session, 'fwdPacketLength', StreamingStats()).get_total()/fwd_duration) if fwd_duration else 0,
        'bwdThroughput' : int(get_value(session, 'bwdPacketLength', StreamingStats()).get_total()/bwd_duration) if bwd_duration else 0,
        'throughput' : int(get_value(session, 'fwdPacketLength', 0).merge(get_value(session, 'bwdPacketLength', 0)).get_total()/duration) if duration else 0,
    })

    features = {
        'fwdWindowSize' : get_value(session, 'fwdWindowSize', 0),
        'bwdWindowSize' : get_value(session, 'bwdWindowSize', 0),
        'windowSize' : get_value(session, 'fwdWindowSize', 0).merge(get_value(session, 'bwdWindowSize', 0)),

        'fwdPacketLength' : get_value(session, 'fwdPacketLength', 0),
        'bwdPacketLength' : get_value(session, 'bwdPacketLength', 0),
        'packetLength' : get_value(session, 'fwdPacketLength', 0).merge(get_value(session, 'bwdPacketLength', 0)),

        'fwdTCPSegmentLen' : get_value(session, 'fwdTCPSegmentLen', 0),
        'bwdTCPSegmentLen' : get_value(session, 'bwdTCPSegmentLen', 0),
        'TCPSegmentLen' : get_value(session, 'fwdTCPSegmentLen', 0).merge(get_value(session, 'bwdTCPSegmentLen', 0)),

        'fwdIPLength' : get_value(session, 'fwdIPLength', 0),
        'bwdIPLength' : get_value(session, 'bwdIPLength', 0),
        'IPLength' : get_value(session, 'fwdIPLength', 0).merge(get_value(session, 'bwdIPLength', 0)),

        'fwdTCPLength' : get_value(session, 'fwdTCPLength', 0),
        'bwdTCPLength' : get_value(session, 'bwdTCPLength', 0),
        'TCPLength' : get_value(session, 'fwdTCPLength', 0).merge(get_value(session, 'bwdTCPLength', 0)),
    }
    session_features.update(get_stats(features))

    features = {
        'fwdMQTTMsgLength' : get_value(session, 'fwdMQTTMsgLength', 0),
        'bwdMQTTMsgLength' : get_value(session, 'bwdMQTTMsgLength', 0),
        'MQTTMsgLength' : get_value(session, 'fwdMQTTMsgLength', 0).merge(get_value(session, 'bwdMQTTMsgLength', 0)),
    }
    session_features.update(get_stats(features))

    session_features.update({
        'fwdDUPFlag' : get_value(session, 'fwdDUPFlag', 0),
        'bwdDUPFlag' : get_value(session, 'bwdDUPFlag', 0),
        'DUPFlag' : get_value(session, 'fwdDUPFlag', 0) + get_value(session, 'bwdDUPFlag', 0),

        'fwdQoS0' : get_value(session, 'fwdQoS0', 0),
        'bwdQoS0' : get_value(session, 'bwdQoS0', 0),
        'QoS0' : get_value(session, 'fwdQoS0', 0) + get_value(session, 'bwdQoS0', 0),

        'fwdQoS1' : get_value(session, 'fwdQoS1', 0),
        'bwdQoS1' : get_value(session, 'bwdQoS1', 0),
        'QoS1' : get_value(session, 'fwdQoS1', 0) + get_value(session, 'bwdQoS1', 0),

        'fwdQoS2' : get_value(session, 'fwdQoS2', 0),
        'bwdQoS2' : get_value(session, 'bwdQoS2', 0),
        'QoS2' : get_value(session, 'fwdQoS2', 0) + get_value(session, 'bwdQoS2', 0),
    })

    # TCP flags
    session_features.update({
        'fwdTCPFIN' : get_value(session, 'fwdTCPFIN', 0),
        'bwdTCPFIN' : get_value(session, 'bwdTCPFIN', 0),
        'TCPFIN' : get_value(session, 'fwdTCPFIN', 0) + get_value(session, 'bwdTCPFIN', 0),

        'fwdTCPSYN' : get_value(session, 'fwdTCPSYN', 0),
        'bwdTCPSYN' : get_value(session, 'bwdTCPSYN', 0),
        'TCPSYN' : get_value(session, 'fwdTCPSYN', 0) + get_value(session, 'bwdTCPSYN', 0),

        'fwdTCPRST' : get_value(session, 'fwdTCPRST', 0),
        'bwdTCPRST' : get_value(session, 'bwdTCPRST', 0),
        'TCPRST' : get_value(session, 'fwdTCPRST', 0) + get_value(session, 'bwdTCPRST', 0),

        'fwdTCPPSH' : get_value(session, 'fwdTCPPSH', 0),
        'bwdTCPPSH' : get_value(session, 'bwdTCPPSH', 0),
        'TCPPSH' : get_value(session, 'fwdTCPPSH', 0) + get_value(session, 'bwdTCPPSH', 0),

        'fwdTCPACK' : get_value(session, 'fwdTCPACK', 0),
        'bwdTCPACK' : get_value(session, 'bwdTCPACK', 0),
        'TCPACK' : get_value(session, 'fwdTCPACK', 0) + get_value(session, 'bwdTCPACK', 0),

        'fwdTCPURG' : get_value(session, 'fwdTCPURG', 0),
        'bwdTCPURG' : get_value(session, 'bwdTCPURG', 0),
        'TCPURG' : get_value(session, 'fwdTCPURG', 0) + get_value(session, 'bwdTCPURG', 0),

        'fwdTCPECE' : get_value(session, 'fwdTCPECE', 0),
        'bwdTCPECE' : get_value(session, 'bwdTCPECE', 0),
        'TCPECE' : get_value(session, 'fwdTCPECE', 0) + get_value(session, 'bwdTCPECE', 0),

        'fwdTCPCWR' : get_value(session, 'fwdTCPCWR', 0),
        'bwdTCPCWR' : get_value(session, 'bwdTCPCWR', 0),
        'TCPCWR' : get_value(session, 'fwdTCPCWR', 0) + get_value(session, 'bwdTCPCWR', 0),

        'fwdTCPReserved' : get_value(session, 'fwdTCPReserved', 0),
        'bwdTCPReserved' : get_value(session, 'bwdTCPReserved', 0),
        'TCPReserved' : get_value(session, 'fwdTCPReserved', 0) + get_value(session, 'bwdTCPReserved', 0),
    })

    # IP flags
    session_features.update({
        'fwdDFFlag' : get_value(session, 'fwdDFFlag', 0),
        'bwdDFFlag' : get_value(session, 'bwdDFFlag', 0),
        'DFFlag' : get_value(session, 'fwdDFFlag', 0) + get_value(session, 'bwdDFFlag', 0),

        'fwdMFFlag' : get_value(session, 'fwdMFFlag', 0),
        'bwdMFFlag' : get_value(session, 'bwdMFFlag', 0),
        'MFFlag' : get_value(session, 'fwdMFFlag', 0) + get_value(session, 'bwdMFFlag', 0),

        'fwdRBFlag' : get_value(session, 'fwdRBFlag', 0),
        'bwdRBFlag' : get_value(session, 'bwdRBFlag', 0),
        'RBFlag' : get_value(session, 'fwdRBFlag', 0) + get_value(session, 'bwdRBFlag', 0),
    })

    features = {
        'fwdTTL' : get_value(session, 'fwdTTL', 0),
        'bwdTTL' : get_value(session, 'bwdTTL', 0),
        'TTL' : get_value(session, 'fwdTTL', 0).merge(get_value(session, 'bwdTTL', 0)),
    }
    session_features.update(get_stats(features))

    # CONNECT-specific features
    session_features.update({
        'keepAlive' : get_value(session, 'keepAlive', 0),
        'cleanSession' : get_value(session, 'cleanSession', 0),
        'willFlag' : get_value(session, 'willFlag', 0),
        'willQoS' : get_value(session, 'willQoS', 0),
        'willRetain' : get_value(session, 'willRetain', 0),
        'willmsgLen' : get_value(session, 'willmsgLen', 0),
        'willtopicLen' : get_value(session, 'willtopicLen', 0),
        'passwordFlag' : get_value(session, 'passwordFlag', 0),
        'passwordLen' : get_value(session, 'passLen', 0),
        'reserved' : get_value(session, 'reserved', 0),
        'protocolName' : get_value(session, 'protocolName', ''),
        'protocolNameLength' : len(get_value(session, 'protocolName', '')),
    })

    session_features.update({
        # CONNACK-specific
        'connackSessionPresent' : get_value(session, 'connackSessionPresent', 0),
        'connackReturnCode' : get_value(session, 'connackReturnCode', 0), # Successful connection count
    })

    session_features.update({
        # PUB-SUB
        'publishCount' : get_value(session, 'publishCount', 0),
        'pubackNotReceived' : get_value(session, 'pubackNotReceived', 0),
        'subscribeCount' : get_value(session, 'subscribeCount', 0),
        'subackNotReceived' : get_value(session, 'subackNotReceived', 0),
        'subscriptionDenied' : get_value(session, 'subscriptionDenied', 0),
        'wildcardTopicCount' : get_value(session, 'wildcardTopicCount', 0),
        'publishRestrictedTopics' : get_value(session, 'publishRestrictedTopics', 0),
        'subscribeRestrictedTopics' : get_value(session, 'subscribeRestrictedTopics', 0),
    })

    features = {
        'publishMsgLen' : get_value(session, 'publishMsgLen', 0),
        'publishTopicLen' : get_value(session, 'publishTopicLen', 0),
        'interPublishTime' : get_value(session, 'interPublishTime', 0),
        'subscribeTopicLen' : get_value(session, 'subscribeTopicLen', 0),
        'interSubscribeTime' : get_value(session, 'interSubscribeTime', 0),
        'subackDelay' : get_value(session, 'subackDelay', 0),
    }
    session_features.update(get_stats(features))

    session_features.update({
        'pingreqCount' : get_value(session, 'pingreqCount', 0),
        'pingrespCount' : get_value(session, 'pingrespCount', 0),
    })

    features = {
        'fwdIAT' : get_value(session, 'fwdIAT', 0),
        'bwdIAT' : get_value(session, 'bwdIAT', 0),
        'IAT' : get_value(session, 'IAT', 0),
    }
    session_features.update(get_stats(features))

    return session_features