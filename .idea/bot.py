import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ollama import AsyncClient

# Конфигурация
TOKEN = "8000161068:AAHrJIgL6OpCY5fVseZbEm9mcX33UhBqg44"
MODEL_NAME = "llama3:instruct"
UNIVERSITY_NAME = "РТУ МИРЭА"

PROMPT_TEMPLATE = """[INST]
<<SYS>>Ты создаешь официальные посты для соцсетей университета. Стиль: дружелюбный, но профессиональный. Отвечай только на русском языке.<</SYS>>

Сгенерируй пост по шаблону:
1. Приветствие ("Уважаемые студенты!")
2. Описание события (1 предложение)
3. Детали (дата, время, место)
4. Призыв к участию
5. Хештеги: #{hashtag}

Информация о событии: {event_info}[/INST]"""


async def generate_post(event_info: str) -> str:
    """Генерация поста через локальную LLM"""
    client = AsyncClient()
    try:
        response = await client.generate(
            model=MODEL_NAME,
            prompt=PROMPT_TEMPLATE.format(
                event_info=event_info[:500],
                hashtag=UNIVERSITY_NAME.replace(" ", "")
            ),
            options={
                'temperature': 0.7,
                'num_ctx': 1024,
                'num_gpu': 1  # Для Mac с M1/M2
            }
        )
        return response['response']
    except Exception as e:
        print(f"Ошибка генерации: {str(e)}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет! Я помогу создать пост о событиях в {UNIVERSITY_NAME}.\n\n"
        "Пришли мне информацию о событии (например: '25 июня в 14:00 в ауд. 310 "
        "состоится мастер-класс по Python'), и я сгенерирую текст для соцсетей!"
    )


async def handle_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.chat.send_action(action="typing")
        generated_text = await generate_post(update.message.text)

        if not generated_text:
            raise ValueError("Не удалось сгенерировать пост")

        clean_post = generated_text.split('[/INST]')[-1].strip()
        await update.message.reply_text(f"📢 Готовый пост:\n\n{clean_post}")

    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Ошибка: {str(e)}\n\n"
            f"Шаблон для ручного ввода:\n\n"
            f"Уважаемые студенты!\n"
            f"{update.message.text[:300]}\n"
            f"#{UNIVERSITY_NAME.replace(' ', '')} #Событие"
        )


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event))
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()