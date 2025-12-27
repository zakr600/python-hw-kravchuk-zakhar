#!/usr/bin/env python3
"""
Асинхронное скачивание картинок с picsum.photos
Использует aiohttp для неблокирующих HTTP запросов
"""

import asyncio
import aiohttp
import aiofiles
import argparse
from pathlib import Path
import time


async def download_image(session: aiohttp.ClientSession, image_id: int, output_dir: Path, semaphore: asyncio.Semaphore) -> bool:
    url = f"https://picsum.photos/id/{image_id % 1000}/800/600"
    filename = output_dir / f"image_{image_id}.jpg"
    
    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(filename, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    return True
                else:
                    print(f"Ошибка при загрузке изображения {image_id}: статус {response.status}")
                    return False
        except Exception as e:
            print(f"Ошибка при загрузке изображения {image_id}: {e}")
            return False


async def download_images(count: int, output_dir: Path, max_concurrent: int = 10) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        tasks = [
            download_image(session, i, output_dir, semaphore)
            for i in range(count)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is True)
        print(f"\nЗагружено успешно: {successful} из {count} изображений")
        print(f"Изображения сохранены в: {output_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Асинхронное скачивание изображений с picsum.photos"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="Количество изображений для загрузки (по умолчанию: 10)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="images",
        help="Директория для сохранения изображений (по умолчанию: images)"
    )
    parser.add_argument(
        "-c", "--concurrent",
        type=int,
        default=10,
        help="Максимальное количество одновременных загрузок (по умолчанию: 10)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    
    print(f"Начинаем загрузку {args.count} изображений...")
    start_time = time.time()
    
    asyncio.run(download_images(args.count, output_dir, args.concurrent))
    
    elapsed_time = time.time() - start_time
    print(f"Время выполнения: {elapsed_time:.2f} секунд")


if __name__ == "__main__":
    main()


