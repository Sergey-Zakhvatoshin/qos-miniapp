# QoS Mini App - Схема проезда

Telegram Mini App для бота Quality of Style.

## Разработка

### Требования
- Node.js (версия 18 или выше)
- npm

### Установка зависимостей

```bash
cd miniapp
npm install
```

### Запуск в режиме разработки

```bash
npm run dev
```

### Сборка для продакшена

```bash
npm run build
```

После сборки файлы будут в папке `miniapp/dist/`

## Деплой

### Вариант 1: GitHub Pages

1. Создайте репозиторий на GitHub
2. Запушьте файлы из папки `dist` в ветку `gh-pages`
3. Включите GitHub Pages в настройках репозитория
4. Обновите `MINI_APP_URL` в `keyboards/__init__.py`

### Вариант 2: Vercel

1. Установите Vercel CLI: `npm install -g vercel`
2. В папке `miniapp` выполните: `vercel`
3. Следуйте инструкциям
4. Обновите `MINI_APP_URL` в `keyboards/__init__.py`

### Вариант 3: Ваш сервер

1. Скопируйте файлы из `dist` на ваш сервер
2. Настройте веб-сервер (nginx/apache) для раздачи статических файлов
3. Обновите `MINI_APP_URL` в `keyboards/__init__.py`

## Настройка URL

После деплоя обновите переменную `MINI_APP_URL` в файле `keyboards/__init__.py`:

```python
MINI_APP_URL = "https://your-deployed-url.com/index.html"
```

## Тестирование в Telegram

1. Откройте вашего бота в Telegram
2. Нажмите `/start`
3. Нажмите кнопку "🗺️ Схема проезда"
4. Mini App откроется внутри Telegram

## Структура проекта

```
miniapp/
├── index.html          # Точка входа
├── package.json        # Зависимости
├── vite.config.js      # Конфигурация Vite
├── src/
│   ├── main.jsx        # Entry point React
│   ├── App.jsx         # Главный компонент
│   ├── App.css         # Стили компонента
│   └── index.css       # Глобальные стили
└── dist/               # Собранный проект (после build)
```

## Интеграция с Telegram WebApp

Приложение использует Telegram WebApp API для:
- Получения параметров темы (светлая/тёмная)
- Автоматической подстройки под интерфейс Telegram
- Управления окном (expand, close)

## Особенности

- Адаптивный дизайн для мобильных устройств
- Поддержка светлой и тёмной темы Telegram
- SVG схема проезда
- Кнопки для открытия в Яндекс.Картах и Google Maps
