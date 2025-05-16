from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import logging
import config
import asyncio

logging.basicConfig(level=logging.INFO)

# 轮询客服分配
current_index = 0
pending_users = {}  # chat_id: asyncio.Task

def get_next_customer_service():
    global current_index
    cs = config.CUSTOMER_SERVICE[current_index]
    current_index = (current_index + 1) % len(config.CUSTOMER_SERVICE)
    return cs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("售后服务", callback_data="售后服务")],
        [InlineKeyboardButton("技术支持", callback_data="技术支持")],
        [InlineKeyboardButton("商务合作", callback_data="商务合作")],
    ]
    await update.message.reply_text(
        "您好，请选择您需要的服务类型：",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service_type = query.data
    assigned = get_next_customer_service()

    await query.message.reply_text(f"您的问题将由 {assigned} 客服协助，请稍等。")

    # 启动3分钟超时提醒
    async def timeout():
        await asyncio.sleep(180)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"⚠️ {assigned} 尚未响应该用户请求，请尽快处理！"
        )

    # 存储定时任务
    if query.message.chat_id in pending_users:
        pending_users[query.message.chat_id].cancel()
    pending_users[query.message.chat_id] = asyncio.create_task(timeout())

# 语音/图片处理
async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.voice:
        await update.message.reply_text("收到语音，我们会尽快处理。")
    elif update.message.photo:
        await update.message.reply_text("收到图片，我们会查看后尽快回复您。")
    elif update.message.document:
        await update.message.reply_text("收到文件。")
    else:
        await update.message.reply_text("感谢您的信息，我们正在处理。")

app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.VOICE | filters.PHOTO | filters.DOCUMENT, media_handler))

if __name__ == "__main__":
    app.run_polling()
