import sys
import requests
import os
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO
import utils.amazon.read_s3_public as rs3

# TODO: Read deploymentID from argv
# Usage: python filter_s3_keys.py <deploymentID> <optional: media>
# IF specifying string 'media' as argv[2] then a media.csv file will be created (slow)

def main():
    # Idenfiy bucket and base url
    bucket_name = 'urbanriverrangers'
    base_url = f'https://{bucket_name}.s3.amazonaws.com'
    if len(sys.argv) > 1:
        filterID = sys.argv[1]
        # ex '2024-06-03_UR011'
    else:
        return print("Error: Specify Deployment ID")

    # run read_s3_public here 
    if len(sys.argv) > 2:
        read_s3_fresh = sys.argv[2]
        if read_s3_fresh == "GET":
            print("Getting fresh s3 keys with utils/amazon/read_s3_public.py")
            df_a = rs3.get_s3_keys()
        
        else:
            return print("Error: expected 'GET' to get fresh s3 keys, or nothing to read local s3_keys.csv")

    else:
        print("Reading local s3_keys.csv (add 'GET' to cli args to get fresh s3 keys)")
        df_a = pd.read_csv("s3_keys.csv")

    # Sort list of all s3_keys
    # ...If no filters have been specified in read or filter scripts or in .env 'INPUT_S3_FILTER' variable, 
    # ...then this will be full master list of keys
    df_a = df_a.sort_values(by='Key')

    # Filter the df to only the deploymentID and no sendlist
    # Also only contains images and videos
    filtered_df = filter_s3_keys(df_a, filterID)

    if len(sys.argv) > 2:
        if sys.argv[2] == 'media':
            # Generate the media.csv df
            media_df = create_media_csv(filtered_df, base_url)

            # Save the media DataFrame to a CSV file
            media_df.to_csv(f'{filterID}_media.csv', index=False)
            print(f"Media Records saved to {filterID}_media.csv")

    # Generate observation base information for upload to google sheets
    images_df, videos_df = create_obs_csv(filtered_df, base_url)

    # Check for output dir
    if not os.path.isdir('./processed'):
        os.makedirs('./processed')

    # Save the Images DataFrame to a CSV file
    images_df.to_csv(f'./processed/{filterID}_images.csv', index=False)
    print(f"Image Observations saved to {filterID}_images.csv")

    # Save the Videos DataFrame to a CSV file
    videos_df.to_csv(f'./processed/{filterID}_videos.csv', index=False)
    print(f"Video Observations saved to {filterID}_videos.csv")

    return print('Job Complete')


def filter_s3_keys(df: pd.DataFrame, filterID: str):
    """ 
    Focuses on a specific deployment_id and return the filtered df.
    Ignores all images with sendlist in key path. 
    """
    # List of valid image and video extensions
    valid_extensions = ('.jpg', '.jpeg', '.mp4', '.mov')

    filter1_df = df[df['Key'].str.contains(filterID) &\
                     ~df['Key'].str.contains("sendlist") &\
                          ~df['Key'].str.contains("THUMB")]
    filter2_df = filter1_df[filter1_df['Key'].str.lower().str.endswith(valid_extensions)]

    return filter2_df


def create_media_csv(df: pd.DataFrame, base_url: str):
    """ Generates media.csv file for the deploymentID """
    # mediaID: s3 ETag, or other random unique ID, or s3 'Key'
    # deploymentID	
    # captureMethod	
    # timestamp	
    # filePath: URL to s3 Bucket
    # filePublic: TRUE
    # fileName: last of split '/'	
    # fileMediatype: mimeType eg image/jpeg | image/jpg | video/mp4 | video/mov
    # exifData: JSON pulled by pillow function
    # favorite	
    # mediaComments

    # Notify Script is Running
    print("Building media.csv table with Exif Information")

    # List of valid image and video extensions
    image_extensions = ['jpg', 'jpeg']
    video_extensions = ['mp4', 'mov']

    media = []
    for index, row in df.iterrows():
        key = row['Key']
        fileType = key.lower().split('.')[-1]

        if fileType in image_extensions:
            mimeType = f'image/{fileType}'
            exif_data = generate_Exif_JSON(key, base_url)

        elif fileType in video_extensions:
            mimeType = f'video/{fileType}'
            exif_data = {}

        fileName = key.split('/')[-1]
        deploymentID = key.split('/')[2]

        # add a row to media with all of the media information
        media.append({
            'mediaID': row['ETag'],
            'deploymentID': deploymentID,
            'captureMethod': "activityDetection",
            'timestamp': "",
            'filePath': f'{base_url}/{key}',
            'filePublic': True,
            'fileName': fileName,
            'fileMediatype': mimeType,
            'exifData': exif_data,
            'favorite': "",
            'mediaComments': ""

            })
        
    media_df = pd.DataFrame(media)

    return media_df

def extract_Exif(image):
    """Returns JSON of Exif Data"""
    # Define the Exif tags you want to exclude
    tags_to_exclude = [
        'MakerNote',
        'UserComment',
        'ComponentsConfiguration',
        'FileSource',
        'SceneType'
    ]

    # Extract specific parts from the Exif data
    exif_data = {}
    if hasattr(image, '_getexif'):  # Check if image has EXIF data
        exif_info = image._getexif()
        if exif_info is not None:
            for tag, value in exif_info.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name not in tags_to_exclude:
                    exif_data[tag_name] = value

    return exif_data

def generate_Exif_JSON(key, base_url):
    exif_JSON = []
    # Download the image from the public S3 URL into memory
    response = requests.get(f'{base_url}/{key}')
    response.raise_for_status()  # Ensure the request was successful
    file_content = response.content
    
    try:
        # Open the image using Pillow
        image = Image.open(BytesIO(file_content))
        
        # Check if the image format is supported
        if image.format is None:
            raise ValueError("Unsupported image format")
        
        # Extract metadata
        exif_JSON = extract_Exif(image)

    except (IOError, ValueError) as e:
        print(f"Error processing image '{key}': {e}")

    return exif_JSON



def create_obs_csv(df: pd.DataFrame, base_url: str):
    """ Generates first 4 columns of observations for google sheets """
    # observationID: None until observations made
    # deploymentID: matches the folder name saved by SDUploader
    # mediaID: needs to match media.mediaID - maybe s3 ETag

    # Notify User of Starting Script
    print("Building image and video observation lookups ")

    # List of valid image and video extensions
    image_extensions = ['jpg', 'jpeg']
    video_extensions = ['mp4', 'mov']

    filtered_images = []
    filtered_videos = []

    for index, row in df.iterrows():
        key = row['Key']
        fileType = key.lower().split('.')[-1]
        deploymentID = key.split('/')[2]
        if fileType in image_extensions:
            filtered_images.append({
                'observationID': '', # Assigning an observation ID should happen after observing
                'deploymentID': deploymentID,
                'mediaID': row['ETag'],
                'filePath': f'{base_url}/{key}'

                })
        elif fileType in video_extensions:
            filtered_videos.append({
                'observationID': '', # Assigning an observation ID should happen after observing
                'deploymentID': deploymentID,
                'mediaID': row['ETag'],
                'filePath': f'{base_url}/{key}'

                })           

    images_df = pd.DataFrame(filtered_images)
    videos_df = pd.DataFrame(filtered_videos)

    return images_df, videos_df


if __name__ == "__main__":
    main()