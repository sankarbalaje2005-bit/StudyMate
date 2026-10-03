import io
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    SUMMARY_REQUEST_PROMPT,
)


# ==========================================
# SETTINGS
# ==========================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash"


# ==========================================
# CHECK API KEYS
# ==========================================

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")


# ==========================================
# GEMINI CLIENT
# ==========================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# Each Telegram user gets their own
# Gemini conversation.

user_chats = {}


def get_user_chat(user_id):

    if user_id not in user_chats:

        user_chats[user_id] = gemini_client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
        )

    return user_chats[user_id]


# ==========================================
# /START
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    get_user_chat(user_id)

    await update.message.reply_text(
        "Hey! 👋 I'm StudyMate ⚙️📚\n\n"
        "I'm your AI Mechanical Engineering study assistant.\n\n"
        "You can:\n"
        "• Ask engineering questions\n"
        "• Solve numerical problems\n"
        "• Upload engineering images\n"
        "• Prepare exam answers\n"
        "• Generate revision summaries\n\n"
        "Commands:\n"
        "/help - Show help\n"
        "/topics - Mechanical Engineering topics\n"
        "/formula - Formula assistance\n"
        "/exam - Exam preparation\n"
        "/summary - Revision summary\n"
        "/clear - Start a new study session"
    )


# ==========================================
# /HELP
# ==========================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⚙️ StudyMate Help\n\n"

        "Ask questions about:\n"
        "• Thermodynamics\n"
        "• Thermal Engineering\n"
        "• Fluid Mechanics\n"
        "• Machine Design\n"
        "• Manufacturing\n"
        "• Metrology\n"
        "• CAD\n"
        "• Engineering Mechanics\n\n"

        "Commands:\n"
        "/topics - View topics\n"
        "/formula - Get formula help\n"
        "/exam - Exam preparation\n"
        "/summary - Revision summary\n"
        "/clear - Start a new session\n\n"

        "You can also:\n"
        "📷 Send an engineering image\n"
        "🧮 Send a numerical problem"
    )


# ==========================================
# /TOPICS
# ==========================================

async def topics(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⚙️ Mechanical Engineering Topics\n\n"

        "1. Engineering Mechanics\n"
        "2. Thermodynamics\n"
        "3. Thermal Engineering\n"
        "4. Fluid Mechanics\n"
        "5. Heat Transfer\n"
        "6. Manufacturing Processes\n"
        "7. Metrology\n"
        "8. Machine Design\n"
        "9. Design of Machine Elements\n"
        "10. CAD\n"
        "11. Engineering Drawing\n"
        "12. Theory of Machines\n"
        "13. Engineering Materials\n"
        "14. Maintenance Engineering\n\n"

        "Send me a topic and I'll explain it! 📚"
    )


# ==========================================
# /FORMULA
# ==========================================

async def formula(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📐 Formula Help\n\n"

        "Tell me the topic you need a formula for.\n\n"

        "Examples:\n"
        "• Thermodynamics\n"
        "• Fluid Mechanics\n"
        "• Heat Transfer\n"
        "• Machine Design\n"
        "• Engineering Mechanics\n\n"

        "Example:\n"
        "\"Formula for Reynolds number\""
    )


# ==========================================
# /EXAM
# ==========================================

async def exam(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📚 Exam Preparation Mode\n\n"

        "I can prepare answers for:\n\n"

        "🟢 2 Marks\n"
        "🟡 5 Marks\n"
        "🟠 8 Marks\n"
        "🔴 10 Marks\n\n"

        "Example:\n"
        "\"Give me a 5-mark answer for entropy.\""
    )


# ==========================================
# /CLEAR
# ==========================================

async def clear_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id in user_chats:
        del user_chats[user_id]

    get_user_chat(user_id)

    await update.message.reply_text(
        "🧹 Chat cleared successfully!\n\n"
        "Your new StudyMate session has started. 📚⚙️"
    )


# ==========================================
# TEXT QUESTIONS
# ==========================================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    question = update.message.text

    chat = get_user_chat(user_id)

    try:

        response = chat.send_message(
            question
        )

        await update.message.reply_text(
            response.text
        )

    except Exception as error:

        await update.message.reply_text(
            "Sorry, something went wrong.\n\n"
            f"Error: {error}"
        )


# ==========================================
# IMAGE QUESTIONS
# ==========================================

async def handle_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    chat = get_user_chat(user_id)

    try:

        photo = update.message.photo[-1]

        telegram_file = await context.bot.get_file(
            photo.file_id
        )

        image_bytes = io.BytesIO()

        await telegram_file.download_to_memory(
            out=image_bytes
        )

        image_data = image_bytes.getvalue()

        instruction = """
        Analyze this image as a Mechanical Engineering
        study assistant.

        If it contains a mechanical component:

        1. Identify the component.
        2. Explain its main function.
        3. Explain its working principle.
        4. Mention common materials.
        5. Mention applications.
        6. Mention important parameters.
        7. Mention common defects when relevant.

        If it contains an engineering question:

        1. Read the question.
        2. Identify the given information.
        3. Identify what is required.
        4. Select the appropriate formula.
        5. Solve it step by step.
        6. Give the final answer with units.

        If the image is unclear,
        clearly mention what is unclear.
        """

        parts = [
            types.Part.from_bytes(
                data=image_data,
                mime_type="image/jpeg",
            ),
            instruction,
        ]

        response = chat.send_message(
            parts
        )

        await update.message.reply_text(
            response.text
        )

    except Exception as error:

        await update.message.reply_text(
            "Sorry, I could not analyze the image.\n\n"
            f"Error: {error}"
        )


# ==========================================
# /SUMMARY
# ==========================================

async def summary(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    chat = get_user_chat(user_id)

    try:

        response = chat.send_message(
            SUMMARY_REQUEST_PROMPT
        )

        await update.message.reply_text(
            "📚 Revision Summary\n\n"
            + response.text
        )

    except Exception as error:

        await update.message.reply_text(
            "Could not create the summary.\n\n"
            f"Error: {error}"
        )


# ==========================================
# MAIN
# ==========================================

def main():

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Commands

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("topics", topics)
    )

    application.add_handler(
        CommandHandler("formula", formula)
    )

    application.add_handler(
        CommandHandler("exam", exam)
    )

    application.add_handler(
        CommandHandler("summary", summary)
    )

    application.add_handler(
        CommandHandler("clear", clear_chat)
    )

    # Normal text messages

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text
        )
    )

    # Images

    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            handle_photo
        )
    )

    print(
        "StudyMate Telegram bot is running..."
    )

    application.run_polling()


if __name__ == "__main__":
    main()