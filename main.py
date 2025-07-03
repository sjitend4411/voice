import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import pytesseract
import os

# --- API KEYS ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# --- Gemini Setup ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Text-to-Speech (Voice Mode) ---
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# --- Voice Recognition ---
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("🧠 Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        return query.lower()
    except Exception as e:
        print(f"❌ Error: {e}")
        return "none"

# --- Gemini AI Response ---
def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text.replace("*", "")

# --- OCR from Image ---
def image_to_text(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip() if text else "❌ No text detected in image."
    except Exception as e:
        return f"❌ Error processing image: {e}"

# --- Telegram Menu Buttons ---
reply_keyboard = [["📝 Talk to Jarvis", "🖼 Image to Text"], ["ℹ️ About", "❌ Exit"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to Jarvis AI Assistant.\nChoose an option below or type a question.",
        reply_markup=markup
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    if user_msg == "ℹ️ About":
        await update.message.reply_text("🤖 I am Jarvis, powered by Gemini AI. You can chat, use voice, or extract text from images.")
    elif user_msg == "📝 Talk to Jarvis":
        await update.message.reply_text("💬 Please type your question.")
    elif user_msg == "❌ Exit":
        await update.message.reply_text("👋 Goodbye!")
    elif user_msg == "🖼 Image to Text":
        await update.message.reply_text("📷 Please send an image and I'll extract the text.")
    else:
        await update.message.reply_text("⏳ Thinking...")
        response = generate_response(user_msg)
        await update.message.reply_text(response)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f"image_{update.message.message_id}.jpg"
    await file.download_to_drive(file_path)

    extracted_text = image_to_text(file_path)
    await update.message.reply_text(f"🖼 Extracted Text:\n{extracted_text}")

    os.remove(file_path)

# --- Run Telegram Bot ---
def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    print("🚀 Telegram bot is running...")
    app.run_polling()

# --- Voice Assistant Mode ---
def run_voice_mode():
    speak("Voice mode activated. Say something!")
    while True:
        user_input = takeCommand()
        if user_input == "exit":
            speak("Goodbye!")
            break
        elif user_input != "none":
            print(f"👤 You: {user_input}")
            reply = generate_response(user_input)
            print(f"🤖 Jarvis: {reply}")
            speak(reply)

# --- Main Selector ---
def main():
    speak("Say 'voice' for voice mode or 'telegram' to use Telegram bot.")
    while True:
        command = takeCommand()
        print(f"You said: {command}")
        if "voice" in command:
            run_voice_mode()
            break
        elif "telegram" in command:
            speak("Launching Telegram bot")
            run_telegram_bot()
            break
        elif command == "none":
            speak("Didn't catch that. Please say again.")

if __name__ == "__main__":
    main()