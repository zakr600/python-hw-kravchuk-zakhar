#!/usr/bin/env python3
"""
База данных для хранения данных скрапера и Telegram бот
Позволяет подписаться на фильтры и получать уведомления о новых объявлениях
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import aiofiles


@dataclass
class Subscription:
    """Подписка"""
    user_id: int
    city: str
    rooms: Optional[int] = None
    max_price: Optional[int] = None


@dataclass
class Listing:
    """Объявление"""
    id: str
    source: str
    title: str
    price: str
    url: str
    scraped_at: str


class Database:
    
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.listings_file = self.data_dir / "listings.json"
        self.subscriptions_file = self.data_dir / "subscriptions.json"
    
    async def load_listings(self) -> Dict[str, Listing]:
        if not self.listings_file.exists():
            return {}
        
        try:
            async with aiofiles.open(self.listings_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                return {listing_id: Listing(**listing) for listing_id, listing in data.items()}
        except Exception as e:
            print(f"Ошибка при загрузке объявлений: {e}")
            return {}
    
    async def save_listings(self, listings: Dict[str, Listing]) -> None:
        data = {listing_id: asdict(listing) for listing_id, listing in listings.items()}
        async with aiofiles.open(self.listings_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    
    async def add_listings(self, new_listings: List[Listing]) -> List[Listing]:
        existing = await self.load_listings()
        truly_new = []
        
        for listing in new_listings:
            if listing.id not in existing:
                existing[listing.id] = listing
                truly_new.append(listing)
        
        if truly_new:
            await self.save_listings(existing)
        
        return truly_new
    
    async def load_subscriptions(self) -> List[Subscription]:
        if not self.subscriptions_file.exists():
            return []
        
        try:
            async with aiofiles.open(self.subscriptions_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                return [Subscription(**sub) for sub in data]
        except Exception as e:
            print(f"Ошибка при загрузке подписок: {e}")
            return []
    
    async def save_subscriptions(self, subscriptions: List[Subscription]) -> None:
        data = [asdict(sub) for sub in subscriptions]
        async with aiofiles.open(self.subscriptions_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    
    async def add_subscription(self, subscription: Subscription) -> bool:
        subscriptions = await self.load_subscriptions()
        
        for sub in subscriptions:
            if (sub.user_id == subscription.user_id and
                sub.city == subscription.city and
                sub.rooms == subscription.rooms and
                sub.max_price == subscription.max_price):
                return False
        
        subscriptions.append(subscription)
        await self.save_subscriptions(subscriptions)
        return True
    
    async def remove_subscription(self, user_id: int, index: int) -> bool:
        subscriptions = await self.load_subscriptions()
        user_subs = [s for s in subscriptions if s.user_id == user_id]
        
        if 0 <= index < len(user_subs):
            sub_to_remove = user_subs[index]
            subscriptions.remove(sub_to_remove)
            await self.save_subscriptions(subscriptions)
            return True
        return False
    
    async def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        subscriptions = await self.load_subscriptions()
        return [s for s in subscriptions if s.user_id == user_id]
    
    def matches_subscription(self, listing: Listing, subscription: Subscription) -> bool:
        if listing.source != 'yandex':
            return False
        return True


class TelegramBot:
    
    def __init__(self, token: str, db: Database):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.db = db
        self._register_handlers()
    
    def _register_handlers(self):
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_subscribe, Command("subscribe"))
        self.dp.message.register(self.cmd_list, Command("list"))
        self.dp.message.register(self.cmd_unsubscribe, Command("unsubscribe"))
    
    async def cmd_start(self, message: Message):
        """Команда /start"""
        await message.answer(
            "Привет! Я бот для отслеживания объявлений о съеме жилья.\n\n"
            "Используй /help для списка команд."
        )
    
    async def cmd_help(self, message: Message):
        """Команда /help"""
        help_text = """
Доступные команды:

/subscribe - Подписаться на новые объявления
Формат: /subscribe город [комнаты] [макс_цена]
Примеры:
  /subscribe moskva
  /subscribe moskva 2
  /subscribe moskva 2 50000

/list - Показать мои подписки

/unsubscribe - Отписаться от подписки
Формат: /unsubscribe номер
Пример: /unsubscribe 0

/help - Показать эту справку
        """
        await message.answer(help_text)
    
    async def cmd_subscribe(self, message: Message):
        """Команда /subscribe"""
        args = message.text.split()[1:]
        
        if not args:
            await message.answer(
                "Использование: /subscribe город [комнаты] [макс_цена]\n"
                "Пример: /subscribe moskva 2 50000"
            )
            return
        
        city = args[0]
        rooms = None
        max_price = None
        
        if len(args) > 1:
            try:
                rooms = int(args[1])
            except ValueError:
                pass
        
        if len(args) > 2:
            try:
                max_price = int(args[2])
            except ValueError:
                pass
        
        subscription = Subscription(
            user_id=message.from_user.id,
            city=city,
            rooms=rooms,
            max_price=max_price
        )
        
        added = await self.db.add_subscription(subscription)
        
        if added:
            await message.answer(
                f"Подписка добавлена!\n"
                f"Город: {city}\n"
                f"Комнаты: {rooms or 'любые'}\n"
                f"Макс. цена: {max_price or 'без ограничений'}\n"
                f"Источник: Яндекс.Недвижимость"
            )
        else:
            await message.answer("Такая подписка уже существует!")
    
    async def cmd_list(self, message: Message):
        """Команда /list"""
        subscriptions = await self.db.get_user_subscriptions(message.from_user.id)
        
        if not subscriptions:
            await message.answer("У вас нет активных подписок. Используйте /subscribe для добавления.")
            return
        
        text = "Ваши подписки:\n\n"
        for i, sub in enumerate(subscriptions):
            text += f"{i}. Город: {sub.city}\n"
            if sub.rooms:
                text += f"   Комнаты: {sub.rooms}\n"
            if sub.max_price:
                text += f"   Макс. цена: {sub.max_price}\n"
            text += f"   Источник: Яндекс.Недвижимость\n\n"
        
        await message.answer(text)
    
    async def cmd_unsubscribe(self, message: Message):
        """Команда /unsubscribe"""
        args = message.text.split()[1:]
        
        if not args:
            await message.answer("Использование: /unsubscribe номер\nПример: /unsubscribe 0")
            return
        
        try:
            index = int(args[0])
            removed = await self.db.remove_subscription(message.from_user.id, index)
            
            if removed:
                await message.answer(f"Подписка #{index} удалена!")
            else:
                await message.answer("Подписка с таким номером не найдена. Используйте /list для просмотра подписок.")
        except ValueError:
            await message.answer("Номер должен быть числом!")
    
    async def send_listing_notification(self, user_id: int, listing: Listing):
        text = (
            f"Новое объявление!\n\n"
            f"{listing.title}\n"
            f"Цена: {listing.price}\n"
            f"Ссылка: {listing.url}\n"
            f"Дата: {listing.scraped_at}"
        )
        
        try:
            await self.bot.send_message(user_id, text)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
    
    async def process_new_listings(self, new_listings: List[Listing]):
        subscriptions = await self.db.load_subscriptions()
        
        for listing in new_listings:
            for subscription in subscriptions:
                if self.db.matches_subscription(listing, subscription):
                    await self.send_listing_notification(subscription.user_id, listing)
                    await asyncio.sleep(0.1)
    
    async def start(self):
        await self.dp.start_polling(self.bot)


async def run_bot_and_scraper(
    bot_token: str,
    scrape_interval: int = 3600,
    city: str = "moskva",
    rooms: Optional[int] = None,
    max_price: Optional[int] = None
):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from task_5_2 import RentalScraper
    
    db = Database()
    bot = TelegramBot(bot_token, db)
    
    async def scraper_loop():
        async with RentalScraper() as scraper:
            while True:
                try:
                    print(f"\n[{datetime.now()}] Начинаем проверку новых объявлений...")
                    
                    new_listings_raw = await scraper.find_new_listings(city, rooms, max_price)
                    
                    new_listings = [
                        Listing(
                            id=listing['id'],
                            source=listing['source'],
                            title=listing['title'],
                            price=listing['price'],
                            url=listing['url'],
                            scraped_at=listing['scraped_at']
                        )
                        for listing in new_listings_raw
                    ]
                    
                    if new_listings:
                        print(f"Найдено {len(new_listings)} новых объявлений")
                        truly_new = await db.add_listings(new_listings)
                        
                        if truly_new:
                            print(f"Добавлено {len(truly_new)} новых объявлений в базу")
                            await bot.process_new_listings(truly_new)
                    else:
                        print("Новых объявлений не найдено")
                    
                    print(f"Следующая проверка через {scrape_interval} секунд...")
                except Exception as e:
                    print(f"Ошибка в цикле скрапинга: {e}")
                
                await asyncio.sleep(scrape_interval)
    
    await asyncio.gather(
        bot.start(),
        scraper_loop()
    )


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Telegram бот для отслеживания объявлений о съеме жилья"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Telegram bot token (или используйте переменную окружения TELEGRAM_BOT_TOKEN)"
    )
    parser.add_argument(
        "--city",
        type=str,
        default="moskva",
        help="Город для скрапинга (по умолчанию: moskva)"
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
        "--interval",
        type=int,
        default=3600,
        help="Интервал между проверками в секундах (по умолчанию: 3600)"
    )
    
    args = parser.parse_args()
    
    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("Ошибка: не указан токен Telegram бота!")
        print("Используйте --token или установите переменную окружения TELEGRAM_BOT_TOKEN")
        return
    
    print("Запуск бота и скрапера...")
    asyncio.run(run_bot_and_scraper(
        token,
        args.interval,
        args.city,
        args.rooms,
        args.max_price
    ))


if __name__ == "__main__":
    main()

