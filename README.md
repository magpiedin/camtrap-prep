# Camtrap Packager and rePackager

For creating camtrap-dp zip files according to: https://camtrap-dp.tdwg.org/.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

Built with python==3.9.6
Will need to download and install exiftool at: https://exiftool.org/install.html
Ensure exiftool.exe lies within PATH, if using conda, you can store the exe in your Scripts path.

### Example Installation Steps

1. Clone the repository:

   ```sh
   git clone https://github.com/username/camtrap-prep.git
   ```

2. Navigate to the project directory:

   ```sh
   cd camtrap-prep
   ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt

        or, if using conda

   conda create -f environment.yml
   ```

4. For repackager - manage Google Application Credentials  
You will need to activate the Google Drive API in cloud console  
You may also need to create a cloud project (no billing)  
Manage the Google Drive API, go to the 

Go to OAuth consent screen:

In the Google Cloud Console, select APIs & Services > OAuth consent screen.
Fill in the required fields, such as application name, support email, etc.
Add Test Users:

Scroll down to the Test users section.
Add the email addresses of users you want to allow access to your app.

Scopes Could Be:
 'https://www.googleapis.com/auth/drive.readonly'
 'https://www.googleapis.com/auth/drive'

## Usage

Follow the .env.example file and create a .env file with the desired file paths and destinations.

### Example Usage

1. Run the script:

   ```sh
   python camtrap.py packager

   or

   python camtrap.py repackager
   ```

## Contributing

Guidelines for contributing to the project. Include information about how to report bugs, suggest enhancements, and submit pull requests.

## License

Information about the project's license. Include the license type and any additional terms or conditions.
