from scapy.contrib.mqtt import MQTT
from scapy.utils import PcapReader
from MQTTNetLyzer.csv_writer import csv_writer
from MQTTNetLyzer.helper_functions import time_to_str
from MQTTNetLyzer.session import Session
from MQTTNetLyzer.extract_features import extract_mqtt_data
from MQTTNetLyzer import variables
import time

def analyze():
    
    print('Reading the packets...')
    batch = 1
    with PcapReader(variables.input_pcap_file) as pcap_reader:
        
        start_time = time.time()
        
        while True:

            packets = pcap_reader.read_all(count=variables.batch_size)
            if not packets:
                break

            if variables.display_batch_status:
                print(f'Reading batch {batch}')
                batch += 1
                if variables.display_batch_stats:
                    batch_count = 0
                    batch_mqtt_count = 0
                    for _ in packets:
                        batch_count += 1
                        if MQTT in _:
                            batch_mqtt_count += 1
                    print(f'Total number of packets: {batch_count}')
                    print(f'Total number of MQTT packets: {batch_mqtt_count}')
                    print('Analyzing the packets...')

            # CHECKPOINT
            current_time = time_to_str(packets[0].time)
            for session in variables.active_sessions.copy().values():
                if not session.check_activeness(current_time):
                    variables.completed_sessions.append(session)
                    del variables.active_sessions[session.sessionID]

            # CSV WRITER
            if len(variables.completed_sessions) >= variables.csv_writer_batch_size:
                csv_writer()

            for packet in packets:
                variables.total_packets_count += 1
                try:
                    if MQTT in packet:

                        variables.total_mqtt_packets_count += 1
                        packet_info_list = extract_mqtt_data(packet)

                        first_packet = packet_info_list[0]

                        fwd_sessionID = f"{first_packet['srcIP']}_{first_packet['srcPort']}_{first_packet['dstIP']}_{first_packet['dstPort']}"
                        bwd_sessionID = f"{first_packet['dstIP']}_{first_packet['dstPort']}_{first_packet['srcIP']}_{first_packet['srcPort']}"
                       
                        # Forward session
                        if variables.active_sessions.get(fwd_sessionID):
                            session = variables.active_sessions[fwd_sessionID]
                            if session.add_packet(first_packet):
                                if len(packet_info_list) > 1:
                                    for packet_info in packet_info_list[1:]:
                                        session.add_packet(packet_info, multiple_commands_packet=True)
                                continue

                        # Backward session
                        if variables.active_sessions.get(bwd_sessionID):
                            session = variables.active_sessions[bwd_sessionID]
                            if session.add_packet(first_packet, forward=False):
                                if len(packet_info_list) > 1:
                                    for packet_info in packet_info_list[1:]:
                                        session.add_packet(packet_info, forward=False, multiple_commands_packet=True)
                                continue

                        if first_packet['type'] == 'CONNECT':
                            new_session = Session(first_packet)
                            if variables.active_sessions.get(new_session.sessionID):
                                variables.completed_sessions.append(variables.active_sessions[new_session.sessionID])
                            variables.active_sessions[new_session.sessionID] = new_session
                            if len(packet_info_list) > 1:
                                for packet_info in packet_info_list[1:]:
                                    new_session.add_packet(packet_info, multiple_commands_packet=True)

                        else:
                            new_session = Session(first_packet, connect_packet=False)
                            if variables.active_sessions.get(new_session.sessionID):
                                variables.completed_sessions.append(variables.active_sessions[new_session.sessionID])
                            variables.active_sessions[new_session.sessionID] = new_session
                            if len(packet_info_list) > 1:
                                for packet_info in packet_info_list[1:]:
                                    new_session.add_packet(packet_info, multiple_commands_packet=True)

                except Exception as e:
                    pass

            if variables.display_batch_status and variables.display_batch_stats:
                print(f'Average Analyzing Rate: {int(variables.total_mqtt_packets_count/(time.time()-start_time))} packets/s')
                print('-'*50)

        # Incomplete Sessions
        variables.completed_sessions.extend(variables.active_sessions.values())
        csv_writer()