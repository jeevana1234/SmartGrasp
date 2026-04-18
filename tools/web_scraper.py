"""
Web scraper to download cup images for training dataset
Scrapes from Unsplash and Pexels for free cup images
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime

class CupImageScraper:
    """Scrape cup images from web sources"""
    
    def __init__(self, output_folder="../dataset/raw_images"):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_unsplash(self, query="coffee cup with handle", num_images=20):
        """Scrape from Unsplash (free, high-quality images)"""
        print(f"🌐 Scraping Unsplash for: {query}")
        
        base_url = f"https://unsplash.com/napi/search/photos"
        params = {
            'query': query,
            'page': 1,
            'per_page': num_images
        }
        
        try:
            response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
            data = response.json()
            
            downloaded = 0
            for photo in data.get('results', []):
                try:
                    img_url = photo['urls']['regular']
                    img_response = requests.get(img_url, headers=self.headers, timeout=10)
                    
                    # Save image
                    filename = f"{self.output_folder}/unsplash_{photo['id']}.jpg"
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    
                    downloaded += 1
                    print(f"  ✅ {downloaded}/{num_images}: {photo['description'][:40] if photo.get('description') else 'Cup image'}")
                    time.sleep(0.5)  # Be nice to server
                    
                except Exception as e:
                    print(f"  ❌ Failed to download: {e}")
            
            return downloaded
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0
    
    def scrape_pexels(self, query="coffee cup", num_images=20):
        """Scrape from Pexels (free images)"""
        print(f"🌐 Scraping Pexels for: {query}")
        
        base_url = f"https://www.pexels.com/search/{query}/"
        
        try:
            response = requests.get(base_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find image elements
            img_elements = soup.find_all('img', class_='lazy')
            
            downloaded = 0
            for img in img_elements[:num_images]:
                try:
                    img_url = img.get('data-lazy-src') or img.get('src')
                    if not img_url or 'pexels' not in img_url:
                        continue
                    
                    img_response = requests.get(img_url, headers=self.headers, timeout=10)
                    
                    filename = f"{self.output_folder}/pexels_{downloaded}.jpg"
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    
                    downloaded += 1
                    print(f"  ✅ {downloaded}/{num_images}")
                    time.sleep(0.5)
                    
                except Exception as e:
                    pass
            
            return downloaded
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0
    
    def download_from_urls(self, urls):
        """Download images from a list of URLs"""
        print(f"📥 Downloading {len(urls)} images from URLs")
        
        downloaded = 0
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                filename = f"{self.output_folder}/custom_{i}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                downloaded += 1
                print(f"  ✅ {downloaded}/{len(urls)}")
                time.sleep(0.3)
            except Exception as e:
                print(f"  ❌ Failed {i}: {e}")
        
        return downloaded

if __name__ == "__main__":
    scraper = CupImageScraper()
    
    print("🤖 Cup Image Web Scraper")
    print("=" * 50)
    
    # Scrape from Unsplash (most reliable)
    count1 = scraper.scrape_unsplash("coffee mug with handle", num_images=10)
    count2 = scraper.scrape_unsplash("tea cup ceramic handle", num_images=10)
    
    # Try Pexels
    count3 = scraper.scrape_pexels("coffee cup handle", num_images=10)
    
    print("\n" + "=" * 50)
    print(f"✅ Downloaded {count1 + count2 + count3} images")
    print(f"📁 Saved to: ../dataset/raw_images/")
