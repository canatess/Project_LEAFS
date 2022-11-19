"""
@Project:
    AIN 311 - Project LEAFS

@Authors:
    1- Can Ali Ateş
    2- Baha Kırbaşoğlu
    3- Abdullah Enes Ergün
"""

# Import Selenium Drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Import Libraries
import io
import os
import time
import driver
import requests
from PIL import Image
from urllib.parse import urlparse


class ImageScraper:

    # Initialize the Scraper.
    def __init__(self, webdriver_path, image_path, search_key="cat", number_of_images=1, headless=True, min_resolution=(0, 0), max_resolution=(1920, 1080), max_missed=10):

        # Create a File(s) to Save Images.
        image_path = os.path.join(image_path, search_key)
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)

        # Check Chromedriver Updated
        while True:
            try:
                # Try Go to the Google Home Page.
                options = Options()
                if headless:
                    options.add_argument('--headless')
                web_driver = webdriver.Chrome(webdriver_path, chrome_options=options)
                web_driver.set_window_size(1400, 1050)
                web_driver.get("https://www.google.com")
                if web_driver.find_elements("id", "L2AGLb"):
                    web_driver.find_element("id", "L2AGLb").click()
                break
            except:
                # Chromedriver is not Available or Outdated.
                try:
                    web_driver
                except NameError:
                    is_patched = driver.download_latest_chromedriver()
                else:
                    is_patched = driver.download_latest_chromedriver(web_driver.capabilities['version'])
                if not is_patched:
                    exit("[ERROR] Please Update the chromedriver.exe in the webdriver Folder")

        # If Chromedriver Exist and Available, then Initialize the Parameters.
        self.driver = web_driver
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = f"https://www.google.com/search?q={search_key}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.max_missed = max_missed

    def find_image_urls(self):
        """
            This function search and return a list of image urls based on the search key.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls = google_image_scraper.find_image_urls()

        """
        print("[INFO] Gathering Image Links")
        image_urls = []
        count = 0
        missed_count = 0
        self.driver.get(self.url)
        time.sleep(3)
        index = 1
        while self.number_of_images > count:
            try:
                # Find and Click the Image.
                img_url = self.driver.find_element('xpath', f'//*[@id="islrg"]/div[1]/div[{str(index)}]/a[1]/div[1]/img')
                img_url.click()
                missed_count = 0
            except Exception:
                missed_count = missed_count + 1
                if missed_count>self.max_missed:
                    print("[INFO] Maximum Missed Photos Reached, Exiting...")
                    break
            try:
                # Select Image from the Pop-up
                time.sleep(1)
                class_names = ["n3VNCb"]
                images = [self.driver.find_elements("class name", class_name) for class_name in class_names if len(self.driver.find_elements("class name", class_name)) != 0 ][0]
                for image in images:
                    # Only Download the https based Image
                    src_link = image.get_attribute("src")
                    if ("http" in src_link) and (not "encrypted" in src_link):
                        print(
                            f"[INFO] {self.search_key} \t #{count} \t {src_link}")
                        image_urls.append(src_link)
                        count += 1
                        break
            except Exception:
                print("[INFO] Unable to Get Link")

            try:
                # Scroll Page to Load Next Image
                if count % 3 == 0:
                    self.driver.execute_script("window.scrollTo(0, "+str(index*60)+");")
                element = self.driver.find_element("class name", "mye4qd")
                element.click()
                print("[INFO] Loading Next Page")
                time.sleep(3)
            except Exception:
                time.sleep(1)
            index += 1

        self.driver.quit()
        print("[INFO] Google Search Finished")
        return image_urls

    def save_images(self,image_urls, keep_filenames):
        print(keep_filenames)
        # Save Images Into File Directory
        """
            This function takes in an array of image urls and save it into the given image path/directory.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls=["https://example_1.jpg","https://example_2.jpg"]
                google_image_scraper.save_images(image_urls)

        """
        print("[INFO] Saving Image, Please wait...")
        for index, image_url in enumerate(image_urls):
            try:
                print(f"[INFO] Image Url:{image_url}")
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            if keep_filenames:
                                # Extact Filename Without Extension from URL
                                o = urlparse(image_url)
                                image_url = o.scheme + "://" + o.netloc + o.path
                                name = os.path.splitext(os.path.basename(image_url))[0]
                                # Join Filename and Extension
                                filename = "%s.%s"%(name, image_from_web.format.lower())
                            else:
                                filename = "%s%s.%s"%(search_string, str(index), image_from_web.format.lower())

                            image_path = os.path.join(self.image_path, filename)
                            print(
                                f"[INFO] {self.search_key} \t {index} \t Image saved at: {image_path}")
                            image_from_web.save(image_path)
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution != None:
                            if image_resolution[0]<self.min_resolution[0] or image_resolution[1] < self.min_resolution[1] or image_resolution[0] > self.max_resolution[0] or image_resolution[1] > self.max_resolution[1]:
                                image_from_web.close()
                                os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                print("[ERROR] Download Failed: ", e)
                pass
        print("--------------------------------------------------")
        print("[INFO] Downloads Completed. Please Note That Some Photos Were Not Downloaded as They Were not in the Correct Format (e.g. jpg, jpeg, png)")
