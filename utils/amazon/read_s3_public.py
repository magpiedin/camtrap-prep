# Parse Public File to Extract All
import sys
import requests
import pandas as pd
import datetime, time
from dotenv import dotenv_values
from xml.etree import ElementTree

    
def list_objects(bucket_url, filter, continuation_token=None):
    params = {'list-type':'2'} # Use list-type=2 for continuation token support
    # params['prefix'] = filter
    if continuation_token:
        params['continuation-token'] = continuation_token

    full_url = f'{bucket_url}{filter}'

    print(f'full url = {full_url}')

    response = requests.get(full_url, params=params)
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


def get_s3_keys():
    '''main function to retrieve keys from sn s3 bucket, given a filter'''

    config = dotenv_values()
    base_url = config['S3_BASE_URL']
    if base_url is None:
        print('Reminder: Set .env variable S3_BASE_URL to your AWS S3 base url')
        base_url = "https://urbanriverrangers.s3.amazonaws.com"

    # Get filters
    filter = ''
 
    # # 1 - check cli args
    if len(sys.argv) > 1:
        filter = f'/?prefix=images/{sys.argv[1][:4]}/{sys.argv[1]}'  # ex '/?prefix=images/2024/2024-07-20_UR004'
    
    # # 2 - check .env
    elif config['INPUT_S3_FILTER'] is not None:
        filter = config['INPUT_S3_FILTER']

    continuation_token = None
    all_data = []

    i = 0
    while True:
        xml_response = list_objects(base_url, filter, continuation_token)
        data, continuation_token = parse_objects(xml_response)
        all_data.extend(data)

        time.sleep(2)

        i += 1
        sample_row = ''
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


    # Step 2: Parse the XML generated in s3_keys (also df) into a media table?
    # # Alternately, we could do this right after filtering


    # Step 3: Grab Exif Information


    # OPTIONALLY Save the DataFrame to a CSV file
    to_csv = sys.argv[2]
    if to_csv == "CSV":
        print(f'~ {datetime.datetime.now()} - Saving df to CSV...')
        csv_file = 's3_keys.csv'
        df.to_csv(csv_file, index=False)
        
        print(f"~ {datetime.datetime.now()} - Keys have been saved to {csv_file}")
    
    else:
        return df


if __name__ == "__main__":
    get_s3_keys()