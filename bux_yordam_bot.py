#!/usr/bin/env python3
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = "8849803431:AAEPi0FseWHGh6-EmgfAEvws1mLT9-XZDoU"
GROQ_API_KEY = "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"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
groq_client = Groq(api_key=GROQ_API_KEY)
