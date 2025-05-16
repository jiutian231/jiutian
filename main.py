import logging
from telegram import Update, Message, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ChatType
from config import BOT_TOKEN, GROUP_ID

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 存储用户 ID 对应的 message_thread_id
user_threads = {}

async def forward_to_forum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    user_id = user.id
    user_name = user.full_name

    # 如果这个用户没有记录过线程 ID，就创建一个话题
    if user_id not in user_threads:
        topic_title = f"{user_name} ({user_id})"
        topic = await context.bot.create_forum_topic(chat_id=GROUP_ID, name=topic_title)
        thread_id = topic.message_thread_id
        user_threads[user_id] = thread_id
    else:
        thread_id = user_threads[user_id]

    # 转发消息到对应话题
    if message.text:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"💬 用户 {user_name}：\n{message.text}",
            message_thread_id=thread_id
        )
    elif message.photo:
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=message.photo[-1].file_id,
            caption=f"📷 用户 {user_name} 发送了图片",
            message_thread_id=thread_id
        )
    elif message.voice:
        await context.bot.send_voice(
            chat_id=GROUP_ID,
            voice=message.voice.file_id,
            caption=f"🎤 用户 {user_name} 发送了语音",
            message_thread_id=thread_id
        )
    else:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"📎 用户 {user_name} 发送了其他类型的消息。",
            message_thread_id=thread_id
        )

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # 处理用户发来的所有消息
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VOICE, forward_to_forum))

    print("🤖 Bot 已启动")
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
