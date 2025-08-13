from datetime import datetime, timezone
import re
from MQTTNetLyzer.running_stats import StreamingStats

def time_to_str(seconds):
    return datetime.fromtimestamp(float(seconds), timezone.utc).strftime('%d-%m-%Y %H:%M:%S.%f')

def str_to_time(timestamp):
    if isinstance(timestamp, str):
        return datetime.strptime(timestamp, '%d-%m-%Y %H:%M:%S.%f')
    return timestamp

def total_seconds(ts1, ts2):
    if isinstance(ts1, str):
        ts1 = str_to_time(ts1)
    if isinstance(ts2, str):
        ts2 = str_to_time(ts2)
    try:
        return abs((ts1-ts2).total_seconds())
    except:
        return 0

def add_or_initialize(container, key, value):
    if isinstance(container, dict):
        if key in container:
            container[key] += value
        else:
            container[key] = value
    else:
        setattr(container, key, getattr(container, key, 0)+value)

def update_or_initialize_streamingstats(container, key, value):
    if isinstance(container, dict):
        if key in container:
            container[key].update(value)
        else:
            container[key] = StreamingStats(value)
    else:
        if hasattr(container, key):
            getattr(container, key).update(value)
        else:
            setattr(container, key, StreamingStats(value))

def get_value(container, key, alternate_value=None):
    if isinstance(container, dict):
        if key in container:
            return container[key]
        return alternate_value
    else:
        return getattr(container, key, alternate_value)
    
def get_stats(dct):
    stats = {}
    for key, value in dct.items():
        if isinstance(value, int) or isinstance(value, float):
            stats.update({
                'mean'+key[0].upper()+key[1:] : '',
                'median'+key[0].upper()+key[1:] : '',
                'var'+key[0].upper()+key[1:] : '',
                'std'+key[0].upper()+key[1:] : '',
                'skew'+key[0].upper()+key[1:] : '',
                'min'+key[0].upper()+key[1:] : '',
                'max'+key[0].upper()+key[1:] : '',
                'total'+key[0].upper()+key[1:] : '',
            })
            continue

        try:
            skew = value.get_skewness()
        except:
            skew = 0

        stats.update({
            'mean'+key[0].upper()+key[1:] : value.get_mean(),
            'median'+key[0].upper()+key[1:] : value.get_median(),
            'var'+key[0].upper()+key[1:] : value.get_variance(),
            'std'+key[0].upper()+key[1:] : value.get_std(),
            'skew'+key[0].upper()+key[1:] : skew,
            'min'+key[0].upper()+key[1:] : value.get_min(),
            'max'+key[0].upper()+key[1:] : value.get_max(),
            'total'+key[0].upper()+key[1:] : value.get_total(),
        })

    return stats

# To remove unsupported characters
def clean_dict(data_dict, replacement=''):
    def clean_cell(cell):
        if isinstance(cell, str):
            return re.sub(r'[\x00-\x1f\x7f-\x9f]', replacement, cell)
        return cell
    return {key: clean_cell(value) for key, value in data_dict.items()}