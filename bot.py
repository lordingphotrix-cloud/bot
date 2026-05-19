import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# ======================
# 🌐 Keep Alive Web Server
# ======================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ======================
# 🤖 Discord Bot
# ======================
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN 沒有設定，請檢查 Render Environment Variables")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

OPTIONS_FOLDER = "lists"
if not os.path.exists(OPTIONS_FOLDER):
    os.makedirs(OPTIONS_FOLDER)

def init_default_lists():
    default_lists = {
        "戰役": ["機器人", "蟲族", "光能者"],
        "等級": ["3級", "6級", "10級"]
    }
    for list_name, items in default_lists.items():
        file_path = os.path.join(OPTIONS_FOLDER, f"{list_name}.txt")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(items))

def load_options(list_name):
    file_path = os.path.join(OPTIONS_FOLDER, f"{list_name}.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_options(list_name, options):
    file_path = os.path.join(OPTIONS_FOLDER, f"{list_name}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(options))

init_default_lists()

@bot.event
async def on_ready():
    print(f"已登入：{bot.user}")

@bot.command(name="清單")
async def list_all_lists(ctx):
    files = [f[:-4] for f in os.listdir(OPTIONS_FOLDER) if f.endswith(".txt")]
    if not files:
        await ctx.send("目前沒有任何清單！")
    else:
        await ctx.send("\n".join([f"- {name}" for name in files]))

@bot.command(name="抽籤")
async def draw(ctx, list_name: str = None):
    if not list_name:
        options_campaign = load_options("戰役")
        options_level = load_options("等級")
        if not options_campaign or not options_level:
            await ctx.send("戰役或等級清單沒有選項！")
            return
        await ctx.send(f"抽籤結果：{random.choice(options_campaign)} + {random.choice(options_level)}")
        return

    options = load_options(list_name)
    if not options:
        await ctx.send(f"清單「{list_name}」沒有選項！")
        return

    await ctx.send(f"結果：{random.choice(options)}")

@bot.command(name="新增")
async def add_option(ctx, list_name: str = None, *, option: str = None):
    if not list_name or not option:
        await ctx.send("格式：!新增 戰役 光能者")
        return

    options = load_options(list_name)
    option = option.strip()

    if option in options:
        await ctx.send("已存在")
        return

    options.append(option)
    save_options(list_name, options)
    await ctx.send(f"已新增 {option}")

@bot.command(name="查看")
async def list_options(ctx, list_name: str = None):
    if not list_name:
        await ctx.send("格式：!查看 戰役")
        return

    options = load_options(list_name)
    await ctx.send("\n".join(options) if options else "空")

@bot.command(name="刪除")
async def delete_option(ctx, list_name: str = None, index: int = None):
    if not list_name or index is None:
        await ctx.send("格式：!刪除 戰役 2")
        return

    options = load_options(list_name)

    if index < 1 or index > len(options):
        await ctx.send("索引錯誤")
        return

    removed = options.pop(index - 1)
    save_options(list_name, options)
    await ctx.send(f"刪除 {removed}")

# ======================
# 🚀 啟動順序（重點）
# ======================
keep_alive()
bot.run(TOKEN)
