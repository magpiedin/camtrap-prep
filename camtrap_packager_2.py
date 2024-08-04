'''DRAFT - Setup camtrap-dp package, with ref to media files on AWS S3'''

import json, os, re, sys
import pandas as pd
import utils.camtrap_dp_terms as uc
import utils.file_utils as uf
import utils.amazon.filter_s3_keys as utils_s3
from dotenv import dotenv_values
from exiftool import ExifToolHelper
from frictionless import validate
from pandas import DataFrame


config = dotenv_values()
camtrap_config_urls = {}

camtrap_config_urls['base_url'] = f"{config['CAMTRAP_BASE_URL']}/{config['CAMTRAP_VERSION']}"
camtrap_config_urls['profile_url'] = f"{camtrap_config_urls['base_url']}{config['CAMTRAP_PROFILE']}"
camtrap_config_urls['deployments'] = f"{camtrap_config_urls['base_url']}{config['CAMTRAP_DEPLOYMENTS_SCHEMA']}"
camtrap_config_urls['media'] = f"{camtrap_config_urls['base_url']}{config['CAMTRAP_MEDIA_SCHEMA']}"
camtrap_config_urls['observations'] = f"{camtrap_config_urls['base_url']}{config['CAMTRAP_OBSERVATIONS_SCHEMA']}"
camtrap_config_urls['output'] = config['CAMTRAP_OUTPUT_DIR']

def get_camtrap_dp_metadata(
        file_path_raw:str = None, 
        # sd_data_entry_info:dict = None,
        resources_prepped:list = None,
        media_table:list = None,
        obs_table = None
        ) -> uc.CamtrapPackage:
    '''Setup metadata + resources datapackage.json as a camtrap package'''
    
    descriptor = uc.CamtrapPackage(
        profile_dict = None,
        resources_prepped = resources_prepped,
        media_table = media_table,
        get_obs_table=False,
        obs_table = obs_table)

    return descriptor


def setup_dataset_as_resource(
        data_name:str=None, 
        camtrap_config_urls:dict=camtrap_config_urls
        ) -> dict:
    '''setup an input table as a resource for a frictionless package'''

    valid_data_name = ['deployments', 'media', 'observations']

    if data_name not in valid_data_name:
        raise ValueError(f'setup_dataset_as_resource: data_name must be one of {valid_data_name}')
    
    data_path = f'{data_name}.csv'
    # dataset.to_csv(data_path, index = False)
    print(f' # # #   -  convert-to-rsc "data_name" = {data_name}')

    resource = {
        'path' : data_path,
        'name' : data_name,
        'scheme' : 'file',
        'format' : 'csv',
        'profile' : 'tabular-data-resource',
        'schema' : camtrap_config_urls[data_name]
    }

    return resource


def generate_deployments_datasets(
        file_path:str=None,
        media_table:list=None,
        input_data:dict=None
        ) -> list:
    '''Get sdUploader + image inputs for deployments'''

    # TODO 
    # - update this to use new folder-name-convention 
    # - switch media-file-ref to pull from AWS S3 (`utils_s3` functions)
    
    deps_data_raw = None
    deps_table_blank = uc.get_deployments_table_schema()

    if media_table is not None:

        deps_data_raw = uc.map_to_camtrap_deployment(
            deployment_table = deps_table_blank,
            input_data = input_data,
            media_file_path = file_path,
            media_table = media_table
        )

        deps_data = DataFrame([deps_data_raw])

        dep_data_filename = f"{camtrap_config_urls['output']}/deployments.csv"

        deps_data.to_csv(dep_data_filename, 
                         index=False,
                         )
        
        print(f'deployments_data preview:')
        print(deps_data[:5])

        deps_data_valid = validate(dep_data_filename)
        print(f'deps data validations:  {deps_data_valid}')

    return deps_data


def generate_media_datasets(file_path:str=None, input_data:dict=None) -> list:
    '''Get sdUploader + image inputs for media'''

    # TODO 
    # - update this to use new folder-name-convention 
    # - switch media-file-ref to pull from AWS S3 (`utils_s3` functions)
    
    media_data = None
    image_batch = os.listdir(file_path)
    image_batch.sort()

    if image_batch is not None:

        media_raw_data = []
        media_row_blank = uc.get_media_table_schema()
        media_row = None

        # with ExifToolHelper() as et:
        for image in image_batch:

            if os.path.isfile(f'{file_path}/{image}') == True: # and re.find(r'\.[jpg|cr2|rw2|]', image.lower()) is not None:

                # Skip hidden .DS_Store files if present
                if len(re.findall(r".*DS_Store.*", f'{file_path}/{image}')) > 0:
                    pass
                else:

                    media_row = uc.map_to_camtrap_media(
                        media_table=media_row_blank, input_data=input_data,
                        media_file_path=f"{file_path}/{image}")
                    if media_row is not None:
                        media_raw_data.append(media_row)

        media_data_filename = f"{camtrap_config_urls['output']}/media.csv"

        media_data = DataFrame(media_raw_data)
        media_data.to_csv(media_data_filename, 
                          index=False,
                          )
        
        media_data_valid = validate(media_data_filename)
        print(f'media data validations:  {media_data_valid}')

    return media_data


def generate_observations_datasets(
        media_table:list=None) -> list:
    '''Get sdUploader + image inputs for observations'''

    # TODO 
    # - update this to use new folder-name-convention 
    # - switch media-file-ref to pull from AWS S3 (`utils_s3` functions)

    obs_data_filename = f"{camtrap_config_urls['output']}/observations.csv"

    if os.path.isfile(config['INPUT_OBSERVATION_XLSX']):

        obs_data = repackage_dp_v2(
            obs_xls_file = config['INPUT_OBSERVATION_XLSX'],
            obs_data_filename = obs_data_filename
            )
    
    else:
        obs_data_raw = None
        obs_table_blank = uc.get_observations_table_schema()

        if media_table is not None:

            obs_data_raw = uc.map_to_camtrap_observations(
                observations_table = obs_table_blank,
                media_table = media_table
            )

            obs_data = DataFrame(obs_data_raw)
            obs_data.to_csv(obs_data_filename, 
                            index=False,
                            )
            
    print(f'observations_data preview: ')
    print(obs_data[:5])

    obs_data_valid = validate(obs_data_filename)
    print(f'obs data validations:  {obs_data_valid}')
    
    return obs_data


def repackage_dp(obs_xls_file:str=config['INPUT_OBSERVATION_XLSX'], obs_data_filename:str=None):
    '''import manually-edited camtrap-dp 'observation' csv from old workflow / up to ~june 2024'''

    # # folder_to_check=f"{config['WORK_FOLDER']}"

    # # find excel file in folder_to_check
    # obs_xls_file = config['INPUT_OBSERVATION_XLSX']

    # read in the "observations" tab of that excel file
    obs_data = pd.read_excel(obs_xls_file,
                             # sheet_name='observations',  # default = 0 / first sheet
                             )

    # format the obs table / conform to the observation schema
    obs_data = DataFrame(obs_data)
    obs_data_filename = f"{camtrap_config_urls['output']}/observations.csv"

    prepped_obs_data = obs_data.drop('Common Name', axis = 1)

    # output to CSV for camtrap-dp
    prepped_obs_data.to_csv(obs_data_filename, 
                    index=False,
                    )

    return prepped_obs_data


def repackage_dp_v2(obs_xls_file:str=config['INPUT_OBSERVATION_XLSX'], obs_data_filename:str=None):
    '''import manually-edited camtrap-dp 'observation' table from new workflow / post ~june 2024'''

    # NOTE - 2024-aug - this currently requires:
    # 1 - the obs XLSX to be manually saved locally
    # 2 - the .env to be manually updated to point INPUT_OBSERVATION_XLSX to local xlsx file

    print(f'reading observation-sheet from .env INPUT_OBSERVATION_XLSX:  {obs_xls_file}')

    # read in the "observations" tab of a new observation sheet
    # skip 1st row, and use 2nd row as headers
    obs_data = pd.read_excel(obs_xls_file,
                             # sheet_name='observations',  # default = 0 / first sheet
                             header=1, 
                             skiprows=0)

    # Fill in gap-rows if present, where multiple observation-rows relate to the same media-file
    obs_data = DataFrame(obs_data).ffill(axis = 0)

    # reformat the obs table to conform to the observation schema
    # NOTE - reset index / maybe not needed
    obs_data = obs_data.drop('commonName', axis = 1)
    obs_schema = uc.get_observations_table_schema()
    prepped_obs_data = pd.concat([obs_schema, obs_data]).reset_index(drop = True)

    # output to CSV for camtrap-dp
    obs_data_filename = f"{camtrap_config_urls['output']}/observations.csv"

    prepped_obs_data.to_csv(
        obs_data_filename, 
        index=False,
        )

    return prepped_obs_data


def prep_camtrap_dp(file_path_raw:str=None):  # sd.SdXDevice=None):
    '''Prep Data from SDuploader media and output it a camtrap-dp dataset'''
    '''
    TODO - reference these functions in main.SDCardUploaderGUI.data_entry_info? 
    or split out data_entry_info functions from main.SDCardUploaderGUI ? 
    '''

    deploy_dir = uf.get_deployment_dir()

    
    print(f"deployment_id directory = {deploy_dir}")

    if config['MODE'] == "TEST":
        
        # file_path = f"{deploy_dir}/{config['INPUT_IMAGE_DIR']}"
        file_path = uf.get_image_dirs(deploy_dir = deploy_dir)

        print(f"file path = {file_path}")
        
    # else: 
    #     # TODO - check if mountpoint sd.SdXDevice is interchangeable with str
    #     file_path = file_path_raw.mountpoint

    data_entry_info = uc.get_sduploader_input()

    # # TODO - Get profile + sdUploader-inputs for datapackage.json -- e.g.:
    # descriptor = get_camtrap_dp_data(file_path)

    # Setup output datapackage
    # TODO - replace metadata/descriptor example with real-data inputs
    # TODO - replace deployments example with real-data inputs
    media_data = generate_media_datasets(
        file_path = file_path, 
        input_data = data_entry_info
        )
    
    # Generate deployments.CSV
    generate_deployments_datasets(
        file_path = file_path, 
        media_table = media_data,
        input_data = data_entry_info
        )

    # Generate observations.CSV
    obs_data = generate_observations_datasets(
        media_table = media_data
        )
    
    deployments_resource = setup_dataset_as_resource(
        # dataset = deployments_data,
        data_name = 'deployments'
        )

    media_resource = setup_dataset_as_resource(
        # dataset = media_data,
        data_name = 'media'
        )

    observations_resource = setup_dataset_as_resource(
        # dataset = observations_data,
        data_name = 'observations'
        )

    data_resources = [
        deployments_resource,
        media_resource,
        observations_resource
        ]
        
    output_camtrap = get_camtrap_dp_metadata(
        file_path_raw = file_path_raw, 
        # sd_data_entry_info = data_entry_info,
        resources_prepped = data_resources,
        media_table = media_data,
        obs_table = obs_data,
        )


    # Output Camtrap-DP
    output_path = camtrap_config_urls['output']
    output_camtrap_file = f"{output_path}/camtrap-dp-{output_camtrap.id}.zip"

    output_result = uc.save(package_metadata = output_camtrap, 
                            output_path = output_path)
    print(f'# # # OUTPUT Camtrap-dp? {output_result}')


    # Validate output ZIP file using frictionless
    if output_result == True:
        if os.path.exists(output_camtrap_file):
            print(f'Validating output...May take a minute...')

            valid_frictionless = validate(output_camtrap_file)

            print(f"...outputing validation details to 'validation-{output_camtrap.id}.json'")

            with open(f"{output_path}/validation-{output_camtrap.id}.json", "w", encoding='utf-8') as file:
                json.dump(valid_frictionless.to_dict(), file, indent=4, sort_keys=False)

    # Cleanup
    for file in ['datapackage.json', 'deployments.csv', 'media.csv', 'observations.csv']:
        out_file = f'{output_path}/{file}'
        if os.path.exists(out_file):
            print(f'cleanup -- removing {out_file}')
            os.remove(out_file)

if __name__ == "__main__":
    prep_camtrap_dp()