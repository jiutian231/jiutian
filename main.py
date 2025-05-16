import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
cs_str = os.getenv("CUSTOMER_SERVICES", "")
customer_services = list(map(int, cs_str.split(","))) if cs_str else []

current_cs_index = 0
user_sessions = {}

def get_next_customer_service():
    global current_cs_index
    if not customer_services:
        return None
    cs = customer_services[current_cs_index]
    current_cs_index = (current_cs_index + 1) % len(customer_services)
    return cs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用客服机器人！发送消息开始咨询。")

async def forward_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 这里省略消息转发逻辑，跟之前一样
    pass

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), forward_user_message))

    logger.info("🤖 Bot 已启动")
    application.run_polling()
