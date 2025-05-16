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
    user_id = update.message.from_user.id
    text = update.message.text or ""

    if user_id not in user_sessions:
        cs_id = get_next_customer_service()
        if cs_id is None:
            await update.message.reply_text("当前没有客服在线，请稍后再试。")
            return
        user_sessions[user_id] = cs_id

    cs_id = user_sessions[user_id]
    forward_text = f"来自用户 [{user_id}]: {text}"

    try:
        await context.bot.send_message(chat_id=cs_id, text=forward_text)
        await update.message.reply_text("消息已转发给客服，请耐心等待回复。")
    except Exception as e:
        logger.error(f"转发消息失败: {e}")
        await update.message.reply_text("消息转发失败，请稍后再试。")

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), forward_user_message))

    logger.info("🤖 Bot 已启动")
    application.run_polling()
