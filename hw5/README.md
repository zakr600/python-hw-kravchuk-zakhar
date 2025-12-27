# ДЗ 5 Кравчук Захар

## Структура

- `task_5_1.py` - Асинхронное скачивание изображений с picsum.photos
- `task_5_2.py` - Асинхронный скрапер объявлений о съеме жилья с Яндекс.Недвижимость
- `task_5_3.py` - База данных и Telegram бот для отслеживания объявлений

## Установка

### Локальная установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Для задачи 5.3 создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
Отредактируйте .env и добавьте ваш TELEGRAM_BOT_TOKEN
```

### Docker установка

1. Создайте файл `.env` с вашим токеном:
```bash
cp .env.example .env
Отредактируйте .env и добавьте ваш TELEGRAM_BOT_TOKEN
```

2. Запустите через docker-compose:
```bash
docker-compose up -d
```
