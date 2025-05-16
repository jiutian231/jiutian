import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# 从环境变量读取客服ID，多个ID用逗号分隔，转换成整数列表
cs_str = os.getenv("CUSTOMER_SERVICES", "")
customer_services = list(map(int, cs_str.split(","))) if cs_str else []
