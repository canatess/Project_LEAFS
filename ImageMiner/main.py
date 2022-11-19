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
import concurrent.futures
from scraper import ImageScraper


# Function to run in CPU threads.
def worker_thread(search_key):
    image_scraper = ImageScraper(webdriver_path, image_path, search_key, number_of_images, headless, min_resolution, max_resolution)
    image_urls = image_scraper.find_image_urls()
    image_scraper.save_images(image_urls, keep_filenames)

    # Release the resources to free-up memory.
    del image_scraper


if __name__ == '__main__':
    # Determine the webdriver path automatically.
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', 'chromedriver.exe'))

    # Determine the destination path of images to save.
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'labels'))

    # Parameters
    search_keys = list({"keyword_1", "keyword_2"})      # Keywords to search
    number_of_images = 5                             # Desired number of images
    headless = True                                     # True = No Chrome GUI
    min_resolution = (480, 640)                         # Minimum desired image resolution
    max_resolution = (9999, 9999)                       # Maximum desired image resolution
    max_missed = 2000                                   # Max number of failed images before exit
    number_of_workers = 6                               # Number of "workers" used
    keep_filenames = False                              # Keep original URL image filenames

    # Automatically run the CPU threads with search keywords.
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, search_keys)
