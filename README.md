# Telegram-бот для генерации постов о событиях университета

🤖 Бот создает посты для соцсетей о мероприятиях с использованием локальной языковой модели (Llama 3)

## 🚀 Быстрый старт

### Необходимые компоненты
- Python 3.10+
- Ollama (последняя версия)
- Токен бота от [@BotFather](https://t.me/BotFather)

### Установка
1. Установите Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh  # Linux/macOS
   winget install Ollama.Ollama                   # Windows
2. Установите языковую модель:
   ```bash
     ollama pull llama3:instruct   
3.Клонируйте репозиторий

4.В файле bot.py укажите ваш токен:
Получите токен бота у @BotFather в Telegram 
Вставте токен - TOKEN = "ВАШ_ТОКЕН_БОТА"

### Запуск системы 
1.Первый терминал (запуск сервера Ollama):
```bash
   ollama serve

