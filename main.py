import os
import logging
import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
cs_str = os.getenv("CUSTOMER_SERVICES", "")
customer_services = list(map(int, cs_str.split(","))) if cs_str else []

# 存储客服轮询索引
current_cs_index = 0

# 记录用户与客服会话映射 user_id -> topic_message_thread_id
user_sessions = {}

# 超时设置，单位秒
RESPONSE_TIMEOUT = 60 * 5  # 5分钟


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
    user = update.message.from_user
    user_id = user.id
    chat_id = update.message.chat_id
    text = update.message.text

    if user_id in user_sessions:
        thread_id = user_sessions[user_id]
    else:
        # 分配客服
        cs_id = get_next_customer_service()
        if cs_id is None:
            await update.message.reply_text("暂时没有可用客服，请稍后再试。")
            return

        # 在频道/群组为该用户创建话题（消息线程）
        msg = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"新用户 @{user.username or user.first_name} 的会话开始。",
            message_thread_id=None,
        )
        thread_id = msg.message_thread_id
        user_sessions[user_id] = thread_id

        # 通知客服
        await context.bot.send_message(
            chat_id=cs_id,
            text=f"你被分配到新用户 @{user.username or user.first_name} 的会话。"
        )

    # 转发消息到对应话题群组线程
    if update.message.text:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            message_thread_id=thread_id,
            text=f"用户 @{user.username or user.first_name} 说：\n{update.message.text}",
        )
    elif update.message.photo:
        photo = update.message.photo[-1]
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            message_thread_id=thread_id,
            photo=photo.file_id,
            caption=f"用户 @{user.username or user.first_name} 发送了图片"
        )
    elif update.message.voice:
        await context.bot.send_voice(
            chat_id=CHANNEL_ID,
            message_thread_id=thread_id,
            voice=update.message.voice.file_id,
            caption=f"用户 @{user.username or user.first_name} 发送了语音"
        )
    else:
        await update.message.reply_text("暂时不支持此类型消息。")


async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), forward_user_message))

    logger.info("🤖 Bot 已启动")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
