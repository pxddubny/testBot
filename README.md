# Telegram-бот для записи к мастеру маникюра (aiogram + SQLite)

## Возможности
- Запись клиента через inline-кнопки.
- Календарь доступных дат на 1 месяц вперед.
- Выбор только свободного слота.
- Один активный слот на пользователя.
- Сохранение записи в SQLite.
- Уведомление администратору и публикация в канал.
- Отмена записи пользователем (слот снова становится доступным).
- Проверка подписки на канал перед записью.
- Кнопки `Прайсы` и `Портфолио` в главном меню.
- Админ-панель:
  - Добавление рабочих дней.
  - Добавление/удаление слотов.
  - Закрытие/открытие дня.
  - Просмотр расписания на дату.
  - Отмена записи клиента.
- FSM для всех диалоговых сценариев.
- Автонапоминания за 24 часа через APScheduler.
- Восстановление задач напоминаний после перезапуска.

## Структура проекта
```text
/workspace/testBot
├── bot.py
├── config.py
├── states.py
├── requirements.txt
├── .env.example
├── README.md
├── database/
│   ├── __init__.py
│   └── db.py
├── handlers/
│   ├── __init__.py
│   ├── admin.py
│   ├── common.py
│   └── user.py
├── keyboards/
│   ├── __init__.py
│   └── inline.py
└── utils/
    ├── __init__.py
    └── scheduler.py
```

## Установка зависимостей
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка
1. Скопируйте `.env.example` в `.env` и заполните значения.
2. Экспортируйте переменные окружения:
```bash
export BOT_TOKEN="..."
export ADMIN_ID="..."
export CHANNEL_ID="..."
export CHANNEL_LINK="https://t.me/..."
export DB_PATH="bot.db"
```

## Запуск
```bash
python bot.py
```

## requirements.txt
```text
aiogram==3.27.0
APScheduler==3.11.2
```
