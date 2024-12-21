from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
import os

# Mengatur driver Chrome untuk Selenium
service = Service('chromedriver.exe')  
options = webdriver.ChromeOptions()
options.add_argument("--headless") 
driver = webdriver.Chrome(service=service, options=options)

def scrape_with_selenium(url):
    try:
        driver.get("http://" + url if not url.startswith("http") else url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Ambil data yang sama seperti sebelumnya
        title = soup.title.string if soup.title else "N/A"
        meta_description = soup.find("meta", attrs={"name": "description"})
        description = meta_description["content"] if meta_description else "N/A"
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        keywords = meta_keywords["content"] if meta_keywords else "N/A"
        
        return {"url": url, "title": title, "description": description, "keywords": keywords}
    
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return {"url": url, "title": "Error", "description": "Error", "keywords": "Error"}

input_file = "sisa_irene_part3.csv"
output_file = "scraped_data_selenium_sisa_irene_part3.csv"
temp_file = "temp_checkpoint_sisa_irene_part3.csv"
BATCH_SIZE = 10

urls_df = pd.read_csv(input_file)
urls = urls_df['Url'].tolist()

# Melanjutkan dari checkpoint jika ada
if os.path.exists(temp_file):
    scraped_urls = set(pd.read_csv(temp_file)['url'])  
    print(f"Melanjutkan scraping. {len(scraped_urls)} URL telah di-scrape sebelumnya.")
else:
    scraped_urls = set()

# Membuka file output untuk menyimpan hasil scraping
with open(output_file, "a", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["url", "title", "description", "keywords"])
    # Tambahkan header hanya jika file baru
    if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
        writer.writeheader()
    
    batch_data = []
    for idx, url in enumerate(urls):
        if url in scraped_urls:
            continue  
        
        data = scrape_with_selenium(url)
        batch_data.append(data)
        scraped_urls.add(url)
        
        # Simpan data setiap mencapai ukuran batch
        if len(batch_data) >= BATCH_SIZE:
            writer.writerows(batch_data)
            batch_data = []
            with open(temp_file, "w", newline="", encoding="utf-8") as temp:
                temp_writer = csv.DictWriter(temp, fieldnames=["url"])
                temp_writer.writeheader()
                temp_writer.writerows([{"url": u} for u in scraped_urls])
            print(f"Batch {idx + 1} selesai. {len(scraped_urls)} URL telah di-scrape.")

        time.sleep(3)

    # Simpan sisa data di batch terakhir
    if batch_data:
        writer.writerows(batch_data)
        with open(temp_file, "w", newline="", encoding="utf-8") as temp:
            temp_writer = csv.DictWriter(temp, fieldnames=["url"])
            temp_writer.writeheader()
            temp_writer.writerows([{"url": u} for u in scraped_urls])
        print(f"Batch terakhir selesai. Total {len(scraped_urls)} URL telah di-scrape.")

# Hapus file checkpoint setelah selesai
if os.path.exists(temp_file):
    os.remove(temp_file)

driver.quit()

print(f"Scraping selesai. Data disimpan di '{output_file}'.")
