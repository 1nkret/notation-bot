# Notatum — Telegram Pocket Notebook Bot

A Telegram bot for quick note-taking and task management. Send any message and it instantly saves to your Inbox — organize later with custom categories, toggle tasks as done, and work in your preferred language.

## Features

- **Quick Capture** — any text message auto-saves to Inbox, no buttons needed
- **Custom Categories** — create categories with custom emojis to organize notes
- **Task Management** — toggle done/not done with visual checkboxes
- **Edit & Move** — edit text, move records between categories, bulk-clear completed items
- **Multi-language** — English, Russian, Ukrainian with in-bot language switching

## Tech Stack

- **Python 3.12** + [aiogram 3](https://docs.aiogram.dev/) (async Telegram framework)
- **MongoDB 7** via [Motor](https://motor.readthedocs.io/) (async driver)
- **Redis 7** — FSM state storage
- **Docker & Docker Compose** — containerized deployment

## Project Structure

```
├── main.py                  # Entry point
├── core/                    # Config, env variables, bot/dispatcher setup
├── db/                      # MongoDB client and CRUD operations
├── bot/
│   ├── onboarding/          # /start, language selection, user creation
│   ├── start/               # Dashboard, settings, about
│   ├── categories/          # Create, rename, delete categories
│   ├── records/             # CRUD, pagination, toggle done, move
│   └── catch_all/           # Auto-save any text to Inbox
├── utils/                   # Router loader, i18n helper
└── locales/                 # en.yaml, ru.yaml, uk.yaml
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/notation-bot.git
   cd notation-bot
   ```

2. Create `.env` from the example:
   ```bash
   cp .env.example .env
   ```

3. Fill in your bot token in `.env`:
   ```env
   BOT_TOKEN=your_bot_token_here
   REDIS_URL=redis://redis:6379/0
   MONGO_URL=mongodb://mongo:27017
   ```

4. Run with Docker Compose:
   ```bash
   docker compose up -d
   ```

The bot will start polling for updates. Send `/start` to begin.

### Running without Docker

```bash
pip install -r requirements.txt
python main.py
```

Make sure MongoDB and Redis are running and accessible at the URLs in your `.env`.

## Environment Variables

| Variable    | Default                    | Description                        |
|-------------|----------------------------|------------------------------------|
| `BOT_TOKEN` | —                          | Telegram Bot API token (required)  |
| `REDIS_URL` | `redis://redis:6379/0`     | Redis connection string            |
| `MONGO_URL` | `mongodb://mongo:27017`    | MongoDB connection string          |

## License

MIT
