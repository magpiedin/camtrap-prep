'''Tools to help handle files from SD card uploads and transfers across servers/platforms'''

import os
import sys
import json, re, requests, time
import utils.csv_tools as csv_tools
import utils.google_drive as ug
from datetime import datetime
from dotenv import dotenv_values
from exiftool import ExifToolHelper

config = dotenv_values()
camtrap_base_url = f'{config["CAMTRAP_BASE_URL"]}/{config["CAMTRAP_VERSION"]}'
camtrap_profile_url = f'{camtrap_base_url}{config["CAMTRAP_PROFILE"]}'
camtrap_deployment_schema_url = f'{camtrap_base_url}{config["CAMTRAP_DEPLOYMENTS_SCHEMA"]}'
camtrap_media_schema_url = f'{camtrap_base_url}{config["CAMTRAP_MEDIA_SCHEMA"]}'
camtrap_observations_schema_url = f'{camtrap_base_url}{config["CAMTRAP_OBSERVATIONS_SCHEMA"]}'


def get_deployment_dir():
    '''Combine the work-folder and deployment id to form / match the server's deployment directory path'''

    # TODO - Allow / check for CLI input 
    if config['INPUT_DEPLOY_ID'] is not None and os.path.exists(f"{config['WORK_FOLDER']}/{config['INPUT_DEPLOY_ID']}"):
        deploy_dir = f"{config['WORK_FOLDER']}/{config['INPUT_DEPLOY_ID']}"
    else:
        deploy_dir = f"{config['WORK_FOLDER']}/{sys.argv[1]}"

    return deploy_dir


def get_image_dirs(deploy_dir):
    '''check for subdirectories under 'DCIM' from a given SD card upload folder (~ deployment ID)'''

    # NOTE: Most camera-formatted SD card image subdirectories under 'DCIM' seem to start with "100".
    #  If this turns out not to be the case, a list of image subdirs is started here:
    # # A list of image-folder names under the DCIM folder
    # # If a new camera model formats SD cards with another naming convention, add to this list
    # sd_card_folder_names = [
    #     '100DSCIM'  # Spypoint,
    #     '100EK113',  # Bushnell
    #     '100MEDIA',  # Reveal
    #     '100SYCAM',  # Reveal
    # ]

    image_subdirs = os.listdir(f'{deploy_dir}/DCIM')

    if len(image_subdirs) > 0:
        image_subdir = [subdir for subdir in image_subdirs if len(re.findall(r'^100', subdir)) > 0]

    print(f'image subdirs = {image_subdir}')
    if len(image_subdir) > 0:
        print('WARNING -- Extra image subdirectories found, but only the first will be processed')

    return f"{deploy_dir}/DCIM/{image_subdir[0]}"
    

# def get_sduploader_input() -> dict:
#     '''get input data entered by camera crew when offloading SD cards'''

#     # TODO - Determine how/where sdUploader should output that data

#     data_entry_info = {
#         'photographer' : None,
#         'camera' : None,
#         'date' : None,
#         'location' : None,
#         'notes' : None
#     }

#     sd_input_path = None

#     if 'INPUT_SDUPLOADER_DATA_ENTRY' in config.keys():
#         sd_input_path = config['INPUT_SDUPLOADER_DATA_ENTRY']

#     # Read in camera-deployment info from info.txt (or camera_info.json)
#     if sd_input_path is None:
#         sd_input_dir = f"{config['WORK_FOLDER']}/{config['INPUT_DEPLOY_ID']}/"

#         if os.path.exists(f"{sd_input_dir}info.txt"):
#             sd_input_path = f"{sd_input_dir}info.txt"

#         elif os.path.exists(f"{sd_input_dir}camera_info.json"):
#             sd_input_path = f"{sd_input_dir}camera_info.json"


#     print(f'SD uploader data entry file: {sd_input_path}')

#     if os.path.exists(sd_input_path):
#         with open(sd_input_path) as file:
#             data_raw = file.read()

#         if len(re.findall(r'\.json$', sd_input_path)) > 0:
#             data_entry_info = json.loads(data_raw)

#         elif sd_input_path.find('info.txt') > -1:
#             data_entry_info_raw = data_raw.split('\n')
#             data_entry_info['photographer'] = 'Urban Rivers'
#             data_entry_info['camera'] = data_entry_info_raw[1]
#             data_entry_info['date'] = data_entry_info_raw[2]
#             data_entry_info['location'] = data_entry_info_raw[0]
#             data_entry_info['notes'] = data_entry_info_raw[3]
        
    
#     return data_entry_info


# def get_image_data(media_file_path:str=None) -> list:
#     '''get a list of EXIF data for directory of images'''

#     image_info_list = []
#     image_info = {}

#     with ExifToolHelper() as et:
#         try:
#             image_info = et.get_tags(f'{media_file_path}', tags = None)
#             image_info_list.append(image_info)
#         except: 
#             print(f'Check {media_file_path} -- EXIF data not retrievable') 
#             pass

#     return image_info_list


# def get_jpg(file_path, search_string):
#     file_list = os.listdir(file_path)
#     jpg_index = [i for i, x in enumerate(file_list) if len(re.findall(rf'{search_string}', x.lower())) > 0]
#     print(jpg_index)
#     print(file_list[jpg_index[0]])
#     return f"{file_path}/{file_list[jpg_index[0]]}"


# class CamtrapPackage():
#     '''
#     Sets up a frictionless data package following the camtrap-dp exchange format. [Hopefully.]
#     - https://tdwg.github.io/camtrap-dp
#     - https://specs.frictionlessdata.io/data-package
#     '''

#     def __init__(
#             self, 
#             profile_dict:dict=None,
#             resources_prepped:list=None,
#             media_table:list=None,
#             get_obs_table:bool=False,
#             ) -> None:
        
#         if profile_dict is None:
#             profile_dict = map_camtrap_dp_ur_profile() # TODO - check this pulls input

#         self.id = profile_dict['id']
#         self.profile = profile_dict['profile']
        
#         self.name = profile_dict['name']
#         self.title = profile_dict['title']
#         self.created = profile_dict['created'] 
#         self.description = profile_dict['description']
#         self.version = profile_dict['version']
#         self.keywords = profile_dict['keywords']
#         self.image = profile_dict['image']
#         self.homepage = profile_dict['homepage']
#         self.sources = profile_dict['sources']
#         self.bibliographicCitation = profile_dict['bibliographicCitation']
#         self.licenses = profile_dict['licenses']

#         self.contributors = profile_dict['contributors']
#         self.project = profile_dict['project']

#         self.spatial = profile_dict['spatial']
#         self.temporal = get_temporal_data(media_table)
#         self.taxonomic = get_taxonomic_data(get_obs_table)  # profile_dict['taxonomic']

#         self.resources = resources_prepped

#     def __str__():
#         pass

# def save(
#         package_metadata=None,
#         output_path=None,
#         sort_keys=False,
#         make_archive=True,
#     ):
#     '''
#     Output a camtrap-dp package as a zipped directory
#     Based on camtrap-package's 'save' function
#     - https://gitlab.com/oscf/camtrap-package/-/blame/master/src/camtrap_package/package.py?ref_type=heads#L301
#     '''

#     # mkdir if output_path does not exist
#     if output_path:
#         os.makedirs(output_path, exist_ok=True)
#     else:
#         output_path = ''

#     descriptor = package_metadata

#     # write descriptor
#     with open(f"{output_path}/datapackage.json", "w", encoding="utf-8") as _file:
#         json.dump(descriptor.__dict__, 
#                 _file,
#                 indent=4, 
#                 sort_keys=sort_keys)

#     camtrap_id = f'{descriptor.id}'
#     print(f'Camtrap ID for filename === {camtrap_id}')

#     # create zipfile (if requested)
#     zip_name = f"{output_path}/camtrap-dp-{camtrap_id}.zip"
#     if make_archive:
#         with zipfile.ZipFile(zip_name, "w") as zipf:
#             zipf.write(
#                 f"{output_path}/deployments.csv",
#                 arcname="deployments.csv",
#             )
#             zipf.write(
#                 f"{output_path}/media.csv", 
#                 arcname="media.csv"
#             )
#             zipf.write(
#                 f"{output_path}/observations.csv",
#                 arcname="observations.csv",
#             )
#             zipf.write(
#                 f"{output_path}/datapackage.json",
#                 arcname="datapackage.json"
#                 )
#     return True
