import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(name)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize speech recognition engine
r = sr.Recognizer()

# Configure the Gemini API
genai.configure(api_key="AIzaSyAbyk4r2SfZJelOq2u2DL1ll87kF2Dteag")

# Create a Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Voice", callback_data='voice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Hello! I am your assistant bot. You can ask me anything!', reply_markup=reply_markup)

def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'voice':
        voice_assistant(query)

def voice_assistant(query):
    query.edit_message_text("Please speak now...")
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            user_input = r.recognize_google(audio)
            response = generate_response(user_input)
            query.edit_message_text(response)
            engine.say(response)
            engine.runAndWait()
        except sr.UnknownValueError:
            query.edit_message_text("Sorry, I didn't catch that.")

def echo(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    update.message.reply_text(f'You said: {user_text}')
    response = generate_response(user_text)
    engine.say(response)
    engine.runAndWait()

def main() -> None:
    # Replace '7616675073:AAGoV2rIXkaBDyzCK2P5X50VPnZZpPqMbuU' with your Bot's API token
    updater = Updater("7616675073:AAGoV2rIXkaBDyzCK2P5X50VPnZZpPqMbuU")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_click))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if name == 'main':
    main()
