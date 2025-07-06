# Processes a JSON file exported from Google Fit via the Google Takeout service.
# The file is expected to contain weight data in the format (below is an example):
# {
#    "Data Source": "raw:com.google.weight:com.google.android.apps.fitness:samsung:SM-N9005:d24315b1d42ed56e:user_input",
#    "Data Points": [
#        {"fitValue":[{"value":{"fpVal":89}}],"originDataSourceId":"raw:com.google.weight:com.google.android.apps.fitness:samsung:SM-N9005:d24315b1d42ed56e:user_input","endTimeNanos":1451624839273000000,"dataTypeName":"com.google.weight","startTimeNanos":1451624839273000000,"modifiedTimeMillis":1451631136423,"rawTimestampNanos":0}
#    ]
# }
#
# The script accepts a JSON file as input and outputs a CSV file with the following columns:
# - date (YYYY-MM-DD)
# - weight (kg)
import json
import re
import sys
import csv
from datetime import datetime
import argparse
import logging

def process_weight_data(input_file: str) -> list: 
    """Processes weight data from a JSON file and outputs in CSV format to stdout.
    
    Args:
        input_file (str): Path to the input JSON file.
    
    Returns:
        None: If the input data is not in the expected format.
        list: Array of CSV string entries if the data is valid.
    """
    
    output_data = [] # We'll store the output data in this list
    
    if not isinstance(input_file, str):
        raise TypeError("input_file must be a string path to the JSON file.")

    with open(input_file, 'r') as f:
        data = json.load(f)

    # Exit if the data is not in the expected format
    if (
        data.get("Data Source") is None
        or not re.search('^raw:com.google.weight', data["Data Source"])
        or data.get('Data Points') is None
        or len(data['Data Points']) == 0
    ):
        print("No valid weight data found in the input file.")
    else:
        # Otherwise, we continue
        for dp in data['Data Points']:
            timestamp = dp['startTimeNanos'] / 1e9  # Convert nanoseconds to seconds
            timestamp = datetime.fromtimestamp(timestamp)
            date = timestamp.strftime('%Y-%m-%d')
            weight = dp['fitValue'][0]['value']['fpVal']  # Extract weight in kg
            output_data.append((date, weight))
            
    # Output the data in CSV format
    return output_data

def parse_args():
    parser = argparse.ArgumentParser(description="Process Google Fit weight JSON export and output CSV.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON file.")
    parser.add_argument("--loglevel", default=logging.INFO, choices=['DEBUG', 'INFO', 'WARN', 'ERROR'], help='Set logging level (default: INFO)')
    return parser.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=args.loglevel)
    
    output_data = process_weight_data(args.input_file)
    if output_data:
        writer = csv.writer(sys.stdout, delimiter=',')
        writer.writerow(['date', 'weight'])
        writer.writerows(output_data)

if __name__ == "__main__":
    main()