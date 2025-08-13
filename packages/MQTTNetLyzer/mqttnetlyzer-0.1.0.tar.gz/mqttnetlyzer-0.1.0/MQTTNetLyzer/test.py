import glob
import os
import matplotlib.pyplot as plt
import pandas as pd

dirr="C:\materials\mqtt_ids\CSV\DoS_DDoS"
desc='DoS/DDoS-MQTT-IoT: DDoS'

d={}
for csv in glob.glob(os.path.join(dirr, '**', '*.csv'), recursive=True):
    df=pd.read_csv(csv)
    if 'DDoS' in csv.split('\\'):
        d[csv.split('\\')[5]]=d.get(csv.split('\\')[5], 0)+len(df[df.srcIP.isin(["192.168.90.100", "192.168.90.101", "192.168.90.102"])])
        d['Normal']=d.get('Normal', 0)+len(df)-len(df[df.srcIP.isin(["192.168.90.100", "192.168.90.101", "192.168.90.102"])])
    if 'NormalData' in csv.split('\\'):
        d['Normal']=d.get('Normal', 0)+len(df)
# print(d)

bars=plt.bar(list(d.keys()), list(d.values()), color='skyblue')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center')
plt.ylabel('Count')
plt.title(desc)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(dirr,'description_DDoS.png'))
plt.show()



# import os

# def rename_files_and_folders(directory):
#     # Walk through the directory
#     for root, dirs, files in os.walk(directory, topdown=False):
#         # Rename files
#         for name in files:
#             if ' ' in name:
#                 old_path = os.path.join(root, name)
#                 new_name = name.replace(' ', '_')
#                 new_path = os.path.join(root, new_name)
#                 os.rename(old_path, new_path)
#                 print(f'Renamed file: {old_path} -> {new_path}')
        
#         # Rename directories
#         for name in dirs:
#             if ' ' in name:
#                 old_path = os.path.join(root, name)
#                 new_name = name.replace(' ', '_')
#                 new_path = os.path.join(root, new_name)
#                 os.rename(old_path, new_path)
#                 print(f'Renamed directory: {old_path} -> {new_path}')

# # Example usage:
# directory = r'C:\materials\mqtt_ids\CSV'  # replace with the path to your directory
# rename_files_and_folders(directory)
