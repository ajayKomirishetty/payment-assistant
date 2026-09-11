from app.services.telegram_service import TelegramService


if __name__ == "__main__":
    bot = TelegramService()
    bot.run()