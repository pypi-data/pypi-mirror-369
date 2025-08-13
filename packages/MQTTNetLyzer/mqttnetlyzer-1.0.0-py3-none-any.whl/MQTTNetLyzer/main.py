if __name__ == '__main__':
    import os, sys
    sys.path.append(os.getcwd())

import os
import json
import argparse
from MQTTNetLyzer import variables
from MQTTNetLyzer.analyzer import analyze

def main():

    variables.module_dir = os.path.dirname(__file__)

    parser = argparse.ArgumentParser(prog='MQTTNetLyzer', description="The MQTT Layer Session Analyzer")
    parser.add_argument('-v', '--version', action='version', version='MQTTNetLyzer 0.1.0', help='Latest released version')
    parser.add_argument('-c', '--config-file', type=str, help='Path/to/config.json', required=False)
    parser.add_argument('-i', '--input-file', type=str, help='Path/to/input.pcap', required=False)
    parser.add_argument('-o', '--output-file', type=str, help='Path/to/output.csv', required=False)
    parser.add_argument('-b', '--batch-size', type=str, help='Number of packets to be processed in a batch', required=False)
    parser.add_argument('-l', '--label', type=str, help='label of the data', required=False)
    args = parser.parse_args()
    
    if args.config_file:
        config_file = args.config_file

        with open(config_file, 'r') as f:
            config_file = json.load(f)

        for key, value in config_file.items():
            setattr(variables, key, value)

    elif args.input_file:
        setattr(variables, 'input_pcap_file', args.input_file)
        if args.output_file:
            setattr(variables, 'output_csv_file', args.output_file)
        if args.batch_size:
            setattr(variables, 'batch_size', args.batch_size)
        if args.label:
            setattr(variables, 'label', args.label)
    else:
        raise FileNotFoundError('No input PCAP file provided!')

    analyze()

    print('='*100)
    print('Printing final results:')
    print(f"Total no. of packets present: {variables.total_packets_count}")
    print(f"Total no. of MQTT packets present: {variables.total_mqtt_packets_count}")
    if variables.sessions_count:
        print(f"Total no. of sessions extracted: {variables.sessions_count}")
        print(f"CSV file saved to {variables.output_csv_file}")
    else:
        print(f"No sessions found :(")
    print('='*100)

if __name__ == '__main__':
    main()