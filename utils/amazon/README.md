# s3_bucketTools
 Public and Private s3 interaction

## Step 1
 - Download all s3_keys via read_s3_public.ipynb

## Step 2
 - Run unique_deploys.py to get the set of all ids - so far they have been in order
 - Compare against what has already been generated in the processed folder

## Step 3
 - Run filter_s3_keys.py with argument for folder name search argument
 - Review csv file to see if new files were found, many times the video folder is empty
 - Upload exported csv to google drive raw.
 - https://drive.google.com/drive/folders/1vaeAYVJ7OjL3W9oAKvvrdHtULvRVKNRQ

## Step 4
 - Convert csv to observation by import from template
 - Open the template and make a copy into the 1 - Images or 2 - Videos folder with the File name matching the deployment (that was filtered)
 - Navigate to the header in cell B2 "ObservationID"
 - Choose Import,
 - Find the csv file uploaded
 - Choose "replace data at current cell" and leave "detect automatically"
 - Wait a minute-ish because some of these files are large. The sheet should update silently.
 - Hit "allow access" from the orange bar in the top right corner

# YOU DID IT

## Step 5
 - Cleanup the files converted by moving them from the raw folder to the [converted folder](https://drive.google.com/drive/u/1/folders/1avurttV3rAFLsgmTrnjE5nz2WO9W8Nm4) (this keeps a backup and keeps track of the raw data)


---

# Follow-up 
After Observations are awesomely finished:

## Step 6
Process Camtrap-DP dataset from finished obs CSVs
 
- Retrieve google doc
- Format back to camtrap-dp observations table `camtrap_packager_2.py`
- Format camtrap-dp media & deployment tables
- Upload to GitHub UR data repo +/- MongoDB


---

# Back-log 

## Step 1
Process datasets from old camtrap-dp prep workflow in [Wildlife_Camera drive](https://drive.google.com/drive/u/1/folders/1WXqZzyEt-NcHk_o399rdXjuGvi88__1s)

- Retrieve an observation CSV
- Update env variables to reference google doc
- Format back to camtrap-dp observations table using `camtrapRepackager.py`
  - For media accessURIs, replace Google URLs with AWS URLs
- Format camtrap-dp media & deployment tables
- Upload to GitHub UR data repo +/- MongoDB
