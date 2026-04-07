# QoS — Telegram Beauty Appointment Bot

A Telegram bot for booking beauty salon appointments, featuring integrated Mini Apps, automated reminders, and a client feedback system.

## Features

### Appointment Management
- **Service Selection** — Choose from available beauty services (manicure, pedicure, eyelash extensions)
- **Flexible Scheduling** — Pick a date from the next 7 days and select an available time slot
- **Full CRUD Operations** — Create, view, edit, and cancel appointments directly through the bot
- **Client Data Collection** — Captures client name and phone number for each booking

### Automated Notifications
- **24-Hour Reminder** — Notifies clients one day before their appointment
- **2-Hour Reminder** — Sends a same-day reminder two hours before the appointment
- **Review Request** — Automatically requests feedback approximately 24 hours after the service

### Feedback System
- **In-Bot Rating Collection** — Clients rate their experience on a 1–5 scale
- **Positive Reviews** — Clients with 4–5 star ratings are prompted to leave a public review on Yandex Maps
- **Negative Reviews** — Ratings of 1–3 stars trigger an automated email notification to management

### Mini Apps (React SPA)
- **Price List** — Browse service pricing
- **Reviews Page** — View client testimonials
- **Location Map** — Integrated Yandex Maps for directions

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Bot Framework** | Python 3, aiogram 3.x |
| **Mini App Frontend** | React 18, Vite |
| **Database** | SQLite3 |
| **Task Scheduling** | asyncio (built-in) |
| **Deployment** | GitHub Pages (Mini App), any Python host (Bot) |

## Project Structure

```
qos/
├── main.py                 # Bot entry point
├── config.py               # Configuration, bot & dispatcher setup
├── scheduler.py            # Reminder & review request scheduler
├── states.py               # FSM states for booking & review flows
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
│
├── handlers/               # Aiogram event handlers
│   ├── start_handlers.py       # /start command, welcome flow
│   ├── booking_handlers.py     # Service → date → time → name → phone → confirm flow
│   ├── edit_handlers.py        # Edit existing appointments
│   ├── appointments_handlers.py # View & manage appointments
│   └── reviews_handlers.py     # Review rating & feedback collection
│
├── keyboards/              # Inline & reply keyboard builders
│   └── __init__.py
├── constants/              # Text constants & messages
│   └── __init__.py
├── models/                 # Database layer (SQLite3)
│   └── __init__.py
│
└── miniapp/                # React Mini App (Vite + React)
    ├── src/
    │   ├── components/         # PriceList, Reviews
    │   ├── App.jsx
    │   └── main.jsx
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+ (for Mini App development)
- A Telegram Bot token from [BotFather](https://t.me/BotFather)

### Bot Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd qos
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your `BOT_TOKEN` and other variables.

4. **Run the bot**
   ```bash
   python main.py
   ```

### Mini App Development

```bash
cd miniapp
npm install
npm run dev      # Development server
npm run build    # Production build
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot token from BotFather |
| `ADMIN_EMAIL` | Email for negative review notifications |
| `SMTP_SERVER` | SMTP server for sending emails (default: smtp.gmail.com) |
| `SMTP_PORT` | SMTP port (default: 587) |
| `SMTP_USER` | SMTP username |
| `SMTP_PASSWORD` | SMTP password (app password for Gmail) |

## Database Schema

The bot uses SQLite with the following tables:

| Table | Purpose |
|-------|---------|
| `users` | Registered bot users (telegram_id, name, username) |
| `appointments` | Booking records (service, date, time slot, client info) |
| `reminders` | Tracks sent reminders to avoid duplicates |
| `review_requests` | Tracks review requests and responses |

## License

MIT
