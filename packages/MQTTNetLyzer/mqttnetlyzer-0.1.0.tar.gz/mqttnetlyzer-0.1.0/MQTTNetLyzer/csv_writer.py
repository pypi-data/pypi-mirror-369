import csv
from MQTTNetLyzer.calculate_features import calculate_features
from MQTTNetLyzer import variables
from MQTTNetLyzer.helper_functions import clean_dict

def csv_writer():
    sessions_list = []
    for session in variables.completed_sessions:
        try:
            session_features = calculate_features(session)
            session_features['label'] = str(variables.label)
        except Exception as e:
            continue
        sessions_list.append(clean_dict(session_features))

    variables.completed_sessions = []

    if not sessions_list:
        return

    if not variables.csv_initialized:
        with open(variables.output_csv_file, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(sessions_list[0].keys()))
            writer.writeheader()
        variables.csv_initialized = True

    with open(variables.output_csv_file, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(sessions_list[0].keys()))
        writer.writerows(sessions_list)
        variables.sessions_count += len(sessions_list)