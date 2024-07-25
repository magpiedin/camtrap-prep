# Parse Public File to Extract All
import requests
import pandas as pd
import datetime, time
from xml.etree import ElementTree

bucket_name = 'urbanriverrangers'
base_url = f'https://{bucket_name}.s3.amazonaws.com'

    
def list_objects(bucket_url, continuation_token=None):
    params = {'list-type': '2'}  # Use list-type=2 for continuation token support
    if continuation_token:
        params['continuation-token'] = continuation_token

    response = requests.get(bucket_url, params=params)
    response.raise_for_status()  # Ensure we get a successful response

    return response.text

def parse_objects(xml_response):
    root = ElementTree.fromstring(xml_response)
    # Define the namespace
    namespace = {'ns': 'http://s3.amazonaws.com/doc/2006-03-01/'}
    data = []
    for item in root.findall('.//ns:Contents', namespace):
        row = {
            'Key': item.find('ns:Key', namespace).text,
            'ETag': item.find('ns:ETag', namespace).text,
            'LastModified': item.find('ns:LastModified', namespace).text
        }
        data.append(row)

    next_token = root.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}NextContinuationToken')
    return data, next_token.text if next_token is not None else None

continuation_token = None
all_data = []

i = 0
while True:
    xml_response = list_objects(base_url, continuation_token)
    data, continuation_token = parse_objects(xml_response)
    all_data.extend(data)

    time.sleep(2)

    i += 1
    if len(data) > 0:
        sample_row = data[0]
    else: data = ''
    print(f'~ {datetime.datetime.now()} - Getting XML ~ page {i} ~ sample row: {sample_row}')

    if i == 10:
        continuation_token = None
    
    if continuation_token is None:
        break

# Store keys in a pandas DataFrame
df = pd.DataFrame(all_data, columns=['Key','ETag','LastModified'])

# Save the DataFrame to a CSV file
print(f'~ {datetime.datetime.now()} - Saving df to CSV...')
csv_file = 's3_keys.csv'
df.to_csv(csv_file, index=False)

print(f"~ {datetime.datetime.now()} - Keys have been saved to {csv_file}")

# Step 2: Parse the XML generated in s3_keys (also df) into a media table?
# Alternately, we could do this right after filtering

# Step 3: Grab Exif Information
