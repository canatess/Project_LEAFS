"""
@Project:
    AIN 311 - Project LEAFS

@Authors:
    1- Can Ali Ateş
    2- Baha Kırbaşoğlu
    3- Abdullah Enes Ergün
"""

# Import Libraries
import os
import re
import stat
import zipfile
import urllib.request


# Function to Download Chrome Driver Automatically for Windows
def download_latest_chromedriver(current_chrome_version=""):

    # Driver Downloading Operation Control Variable.
    result = False
    try:
        # Find the Latest Chromedriver
        url = 'https://chromedriver.chromium.org/downloads'
        base_driver_url = 'https://chromedriver.storage.googleapis.com/'
        file_name = 'chromedriver_' + "win32.zip"
        pattern = 'https://.*?path=(\d+\.\d+\.\d+\.\d+)'

        # Download the Latest Chromedriver
        stream = urllib.request.urlopen(url)
        content = stream.read().decode('utf8')

        # Parse the Latest Version
        all_match = re.findall(pattern, content)

        if all_match:
            # Version of the Latest Driver
            if current_chrome_version != "":
                print("[INFO] Updating Chromedriver")
                all_match = list(set(re.findall(pattern, content)))
                current_chrome_version = ".".join(current_chrome_version.split(".")[:-1])
                version_match = [i for i in all_match if re.search("^%s" % current_chrome_version, i)]
                version = version_match[0]
            else:
                print("[INFO] Installing New Chromedriver")
                version = all_match[1]
            driver_url = base_driver_url + version + '/' + file_name

            # Download the Zip File
            print('[INFO] Downloading Chromedriver ver: %s: %s' % (version, driver_url))
            app_path = os.path.dirname(os.path.realpath(__file__))
            chromedriver_path = os.path.normpath(os.path.join(app_path, 'webdriver', 'chromedriver.exe'))
            file_path = os.path.normpath(os.path.join(app_path, 'webdriver', file_name))
            urllib.request.urlretrieve(driver_url, file_path)

            # Unzip the File Into Folder
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.normpath(os.path.join(app_path, 'webdriver')))
            st = os.stat(chromedriver_path)
            os.chmod(chromedriver_path, st.st_mode | stat.S_IEXEC)
            print('[INFO] Latest Chromedriver Downloaded')

            # Free-up Memory
            os.remove(file_path)

            # Return Operation Result to True
            result = True
    except Exception:
        print("[WARN] Unable to Download Latest Chromedriver. The System Will Use the Local Version Instead.")

    # Return the Result of Automatically Web Driver Installation.
    return result
