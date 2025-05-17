import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import logging

# Логи
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
TOKEN = "Токен от вашего бота тг"
VEGA_API_KEY = "ВЕГА ТОКЕН"
UNIVERSITY_NAME = "РТУ МИРЭА"
VEGA_API_URL = "https://vega.rest/aiadapter/api/generate"

# Промт для запроса
PROMPT_TEMPLATE = """[INST]
<<SYS>>
Ты профессиональный копирайтер, создающий посты для соцсетей университета. 
Стиль: официально-дружелюбный, вдохновляющий, но без пафоса. 
Формат: 
1. Яркое приветствие (с эмодзи)
2. Описание события (2-3 предложения)
3. Детали (дата, время, место)
4. Призыв к действию (мотивирующая фраза)
5. Хештеги

<</SYS>>

Создай пост о событии: {event_info}

Соблюдай структуру:
🎯 [Приветствие с эмодзи]
✨ [Суть события] 
📌 Детали: [дата/время/место] 
🚀 [Призыв к участию] 
{hashtag}[/INST]"""

# Запрос к нейронке веги
async def generate_post(event_info: str) -> str:

    def sync_request():
        try:
            response = requests.post(
                VEGA_API_URL,
                headers={
                    "Authorization": f"Bearer {VEGA_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-r1:32b",
                    "prompt": PROMPT_TEMPLATE.format(
                        event_info=event_info[:500],
                        hashtag=UNIVERSITY_NAME.replace(" ", "")
                    ),
                    "temperature": 0.7,
                    "options": {
                        "stop": ["</think>", "<think>"],  #  Убрал размышления бота которые приходят в json
                        "num_ctx": 2048
                    }
                },
                verify=False,
                timeout=45
            )
            response.raise_for_status()
            full_response = response.json().get('response', '')

            # Очистка ответа от технических данных и размышлений
            if '<think>' in full_response:
                clean_post = full_response.split('</think>')[-1].strip()
            else:
                clean_post = full_response.strip()

            return clean_post
        except requests.exceptions.RequestException as e:
            logger.error(f"Vega API error: {str(e)}")
            return None

    try:
        return await asyncio.to_thread(sync_request)
    except Exception as e:
        logger.error(f"Async error in generate_post: {str(e)}")
        return None
#Обработка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            f"Привет! Я помогу создать пост о событиях в {UNIVERSITY_NAME}.\n\n"
            "Пришли мне информацию о событии (например: '25 июня в 14:00 в ауд. 310 "
            "состоится мастер-класс по Python'), и я сгенерирую текст для соцсетей!"
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")

# Обрабоктка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.chat.send_action(action="typing")

        if not update.message.text:
            await update.message.reply_text("Пожалуйста, отправьте текстовое описание события.")
            return

        generated_text = await generate_post(update.message.text)

        if not generated_text:
            raise ValueError("Не удалось сгенерировать пост. Попробуйте позже.")

        clean_post = generated_text.split('[/INST]')[-1].strip()
        if not clean_post:
            clean_post = generated_text.strip()  # Если разделитель не найден, используем весь текст

        await update.message.reply_text(f"📢 Готовый пост:\n\n{clean_post}")

    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        await update.message.reply_text(
            f"⚠️ Произошла ошибка. Вы можете использовать этот шаблон:\n\n"
            f"Уважаемые студенты!\n"
            f"{update.message.text[:300]}\n"
            f"#{UNIVERSITY_NAME.replace(' ', '')} #Событие"
        )


def main():
    try:
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("Бот запущен...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")


if __name__ == "__main__":
    main()