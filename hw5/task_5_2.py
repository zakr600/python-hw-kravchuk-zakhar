#!/usr/bin/env python3
"""
Асинхронный скрапер объявлений о съеме жилья
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse
import time
import hashlib


class RentalScraper:

    def __init__(self, output_dir: Path = Path("data")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
        connector = aiohttp.TCPConnector(limit=10, force_close=False)
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        cookie_jar = aiohttp.CookieJar(unsafe=True)
        self.session = aiohttp.ClientSession(headers=base_headers, connector=connector, timeout=timeout, cookie_jar=cookie_jar)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _generate_id(self, url: str, title: str) -> str:
        content = f"{url}{title}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    async def scrape_yandex(self, city: str = "moskva", rooms: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        listings = []
        
        city_map = {
            'moskva': 'moskva',
            'spb': 'sankt-peterburg',
            'ekaterinburg': 'ekaterinburg'
        }
        city_slug = city_map.get(city, city)
        
        url = f"https://realty.yandex.ru/{city_slug}/snyat/kvartira/"
        
        try:
            await asyncio.sleep(0.5)
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    offer_links = soup.find_all('a', href=lambda x: x and '/offer/' in x)
                    seen_offers = set()
                    
                    for link_elem in offer_links[:30]:
                        try:
                            link = link_elem.get('href', '')
                            if not link.startswith('http'):
                                link = f"https://realty.yandex.ru{link}"
                            
                            if link in seen_offers:
                                continue
                            seen_offers.add(link)
                            
                            parent = link_elem.find_parent('div') or link_elem.find_parent('article')
                            if not parent:
                                parent = link_elem
                            
                            title_elem = parent.find('span', {'data-test': 'title'}) or parent.find('h3') or parent.find('a', class_=lambda x: x and 'title' in str(x).lower()) or link_elem
                            title = title_elem.get_text(strip=True) if title_elem else "Объявление"
                            
                            price_elem = parent.find('span', {'data-test': 'price'}) or parent.find('div', class_=lambda x: x and 'price' in str(x).lower()) or parent.find('span', class_=lambda x: x and 'price' in str(x).lower())
                            price = price_elem.get_text(strip=True) if price_elem else "Не указана"
                            
                            listing_id = self._generate_id(link, title)
                            
                            listings.append({
                                'id': listing_id,
                                'source': 'yandex',
                                'title': title,
                                'price': price,
                                'url': link,
                                'scraped_at': datetime.now().isoformat()
                            })
                            
                            if len(listings) >= 20:
                                break
                        except Exception as e:
                            continue
                else:
                    print(f"Ошибка при запросе: статус {response.status}")
        except Exception as e:
            print(f"Ошибка при скрапинге: {e}")
        
        return listings
    
    async def scrape(self, city: str = "moskva", rooms: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        return await self.scrape_yandex(city, rooms, max_price)
    
    def save_listings(self, listings: List[Dict], filename: Optional[str] = None) -> Path:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"listings_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_existing_ids(self) -> set:
        existing_ids = set()
        
        for filepath in self.output_dir.glob("listings_*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for listing in data:
                            if 'id' in listing:
                                existing_ids.add(listing['id'])
            except Exception as e:
                print(f"Ошибка при загрузке {filepath}: {e}")
        
        return existing_ids
    
    async def find_new_listings(self, city: str = "moskva", rooms: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        existing_ids = self.load_existing_ids()
        all_listings = await self.scrape(city, rooms, max_price)
        
        new_listings = [listing for listing in all_listings if listing['id'] not in existing_ids]
        
        return new_listings


async def periodic_scrape(interval: int = 3600, city: str = "moskva", rooms: Optional[int] = None, max_price: Optional[int] = None):
    async with RentalScraper() as scraper:
        while True:
            print(f"\n[{datetime.now()}] Начинаем проверку новых объявлений...")
            
            new_listings = await scraper.find_new_listings(city, rooms, max_price)
            
            if new_listings:
                print(f"Найдено {len(new_listings)} новых объявлений")
                scraper.save_listings(new_listings)
            else:
                print("Новых объявлений не найдено")
            
            print(f"Следующая проверка через {interval} секунд...")
            await asyncio.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="Асинхронный скрапер объявлений о съеме жилья с Яндекс.Недвижимость"
    )
    parser.add_argument(
        "--city",
        type=str,
        default="moskva",
        help="Город для поиска (по умолчанию: moskva)"
    )
    parser.add_argument(
        "--rooms",
        type=int,
        default=None,
        help="Количество комнат (по умолчанию: все)"
    )
    parser.add_argument(
        "--max-price",
        type=int,
        default=None,
        help="Максимальная цена (по умолчанию: без ограничений)"
    )
    parser.add_argument(
        "--periodic",
        action="store_true",
        help="Запустить периодический скрапинг"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Интервал между проверками в секундах (по умолчанию: 3600)"
    )
    
    args = parser.parse_args()
    
    async def run_scraper():
        async with RentalScraper() as scraper:
            if args.periodic:
                await periodic_scrape(args.interval, args.city, args.rooms, args.max_price)
            else:
                print("Начинаем скрапинг Яндекс.Недвижимость...")
                start_time = time.time()
                
                listings = await scraper.scrape(args.city, args.rooms, args.max_price)
                
                elapsed_time = time.time() - start_time
                print(f"\nНайдено объявлений: {len(listings)}")
                print(f"Время выполнения: {elapsed_time:.2f} секунд")
                
                if listings:
                    filepath = scraper.save_listings(listings)
                    print(f"Объявления сохранены в: {filepath}")
    
    asyncio.run(run_scraper())


if __name__ == "__main__":
    main()


