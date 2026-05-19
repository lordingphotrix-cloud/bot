import discord
from discord.ext import commands
import random
import os

# 讀取 Token（Render / 環境變數）
TOKEN = os.getenv("DISCORD_TOKEN")

# 安全檢查（建議加）
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
        await ctx.send("目前沒有任何清單！請先新增清單檔案或用 !新增 指令建立選項。")
    else:
        list_text = "\n".join([f"- {name}" for name in files])
        await ctx.send(f"目前可用的清單：\n{list_text}")

# 🎲 抽籤：無參數時抽戰役+等級，有參數時抽指定清單
@bot.command(name="抽籤")
async def draw(ctx, list_name: str = None):
    if not list_name:
        # 預設同時抽戰役+等級
        options_campaign = load_options("戰役")
        options_level = load_options("等級")
        if not options_campaign or not options_level:
            await ctx.send("戰役或等級清單沒有選項，請先新增！")
            return
        choice1 = random.choice(options_campaign)
        choice2 = random.choice(options_level)
        await ctx.send(f"抽籤結果：{choice1} + {choice2}")
        return

    # 單獨抽某一個清單
    options = load_options(list_name)
    if not options:
        await ctx.send(f"清單「{list_name}」沒有選項，請先新增！")
        return
    result = random.choice(options)
    await ctx.send(f"從「{list_name}」抽籤結果：{result}")

@bot.command(name="新增")
async def add_option(ctx, list_name: str = None, *, option: str = None):
    if not list_name:
        await ctx.send("請輸入清單名稱，例如：!新增 戰役 光能者")
        return
    if not option:
        await ctx.send("請輸入要新增的選項，例如：!新增 戰役 光能者")
        return

    options = load_options(list_name)
    option = option.strip()
    if option in options:
        await ctx.send(f"選項「{option}」已存在於清單「{list_name}」！")
        return

    options.append(option)
    save_options(list_name, options)
    options_list = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    await ctx.send(f"已新增「{option}」至清單「{list_name}」\n目前選項：\n{options_list}")

@bot.command(name="查看")
async def list_options(ctx, list_name: str = None):
    if not list_name:
        await ctx.send("請輸入清單名稱，例如：!查看 戰役 或 !查看 等級")
        return
    options = load_options(list_name)
    if not options:
        await ctx.send(f"清單「{list_name}」目前沒有任何選項！")
        return
    options_list = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    await ctx.send(f"清單「{list_name}」的選項：\n{options_list}")

@bot.command(name="刪除")
async def delete_option(ctx, list_name: str = None, index: int = None):
    if not list_name:
        await ctx.send("請輸入清單名稱，例如：!刪除 戰役 2")
        return
    if index is None:
        await ctx.send("請輸入要刪除的選項編號，例如：!刪除 戰役 2")
        return

    options = load_options(list_name)
    if not options:
        await ctx.send(f"清單「{list_name}」沒有任何選項！")
        return
    if index < 1 or index > len(options):
        await ctx.send(f"請輸入有效的編號（1~{len(options)}）")
        return

    removed = options.pop(index - 1)
    save_options(list_name, options)
    if options:
        options_list = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        await ctx.send(f"已刪除「{removed}」從清單「{list_name}」\n目前選項：\n{options_list}")
    else:
        await ctx.send(f"已刪除「{removed}」從清單「{list_name}」\n清單「{list_name}」已空，請新增新選項！")

bot.run(TOKEN)
