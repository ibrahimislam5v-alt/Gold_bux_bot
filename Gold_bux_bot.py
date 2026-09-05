import os
import json
import time
import telebot
from telebot import types
from datetime import datetime, timedelta
from threading import Thread

# ===== Flask Keep Alive (Render / Replit) =====
try:
    from flask import Flask
    app = Flask(__name__)
    @app.route('/')
    def home():
        return "Gold Bux Bot is Alive! Tasks + bKash/Nagad/Binance"
    def run_flask():
        port = int(os.getenv('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    Thread(target=run_flask, daemon=True).start()
    print("Flask keep-alive started")
except:
    pass

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("BOT_TOKEN set koro!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)
DATA_FILE = "users.json"
WITHDRAW_FILE = "withdraws.json"
GROUPS_FILE = "groups.json"

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_USERNAME = "@TasklyEarn_Official"
CHANNEL_ID = "@TasklyEarn_Official"
CHANNEL_LINK = "https://t.me/TasklyEarn_Official"
GROUP_LINK = "https://t.me/Online_Earning_BD_All"

# Auto Poster Groups - /addgroup diye add korba
GROUPS = []

PROMO = """🔥 Gold Bux Bot - 1 Task = $0.05 🔥

🤖 Bot: @Gold_bux_bot

💰 Kivabe kaj:
Keyboard -> Tasks -> Join Channel -> Check = $0.01
6 ta task = $0.097 = 12 taka

💳 Withdraw: bKash | Nagad | Binance USDT
💵 Minimum: $0.10 | $1 = 124 TK
🎁 Daily Bonus: $0.005 Free
👥 Refer: Per friend $0.02

🚀 Start: @Gold_bux_bot
📌 Proof: @TasklyEarn_Official
💬 Group: https://t.me/Online_Earning_BD_All

24h Payment | 100% Trusted!"""

PROMO_VARIATIONS = [PROMO]

auto_post_enabled = False
auto_post_interval = 30 * 60

def save_groups():
    try:
        with open(GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(GROUPS, f, indent=2)
    except: pass

def load_groups():
    global GROUPS
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r", encoding="utf-8") as f:
                GROUPS = json.load(f)
        except: pass

load_groups()

def auto_post_loop():
    time.sleep(10)
    while True:
        if not auto_post_enabled or len(GROUPS)==0:
            time.sleep(30)
            continue
        try:
            import random
            text = random.choice(PROMO_VARIATIONS)
            for g in GROUPS:
                try:
                    bot.send_message(g, text, disable_web_page_preview=True)
                    time.sleep(random.randint(20,40))
                except: time.sleep(5)
        except: pass
        time.sleep(auto_post_interval)

user_states = {}

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member','administrator','creator']
    except:
        return False

DEFAULT_TASKS = [
    {"id": 1, "title": "Join Main Channel ($0.01)", "desc": f"Amader Main Channel e join koro\nReward: $0.01\n\nLink: {CHANNEL_LINK}\n\nJoin kore Check button e click koro.", "reward": 0.01, "link": CHANNEL_LINK},
    {"id": 2, "title": "Join Earning Group ($0.01)", "desc": f"Amader Group e join koro\nReward: $0.01\n\nLink: {GROUP_LINK}", "reward": 0.01, "link": GROUP_LINK},
    {"id": 3, "title": "Daily Bonus ($0.005)", "desc": "Protidin bonus nao!\nReward: $0.005\n\n24 ghonta por por claim korte parba!", "reward": 0.005, "link": None, "daily": True},
    {"id": 4, "title": "Subscribe Channel 2 ($0.01)", "desc": f"2nd Channel e join\nReward: $0.01\n\nLink: {CHANNEL_LINK}", "reward": 0.01, "link": CHANNEL_LINK},
    {"id": 5, "title": "Follow & Share ($0.012)", "desc": "Bot ta 3 ta group e share koro\nReward: $0.012\n\nShare kore screenshot admin ke pathao.", "reward": 0.012, "link": None},
    {"id": 6, "title": "App Download ($0.05)", "desc": "Official App download koro\nReward: $0.05\n\nLink: https://play.google.com/store\n\nDownload kore Claim koro.", "reward": 0.05, "link": "https://play.google.com/store"},
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

def load_withdraws():
    if os.path.exists(WITHDRAW_FILE):
        try:
            with open(WITHDRAW_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_withdraws(data):
    with open(WITHDRAW_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

def get_user(user_id, users):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "balance": 0.0,
            "completed_tasks": [],
            "referrals": 0,
            "referred_by": None,
            "last_bonus": None,
            "username": "",
            "name": ""
        }
    return users[uid]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💰 Balance", "📋 Tasks (6)")
    markup.add("👥 Refer", "💳 Withdraw")
    markup.add("🎁 Daily Bonus", "📊 Stats")
    return markup

def tasks_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    users = load_data()
    for t in DEFAULT_TASKS:
        markup.add(types.InlineKeyboardButton(f"{t['title']}", callback_data=f"task_{t['id']}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    users = load_data()
    uid = str(message.from_user.id)
    is_new = uid not in users
    user = get_user(message.from_user.id, users)
    user['username'] = message.from_user.username or ""
    user['name'] = message.from_user.first_name or ""

    # Referral system
    args = message.text.split()
    if len(args) > 1 and is_new:
        ref_id = args[1]
        if ref_id != uid and ref_id in users:
            user['referred_by'] = ref_id
            users[ref_id]['balance'] += 0.02
            users[ref_id]['referrals'] += 1
            try:
                bot.send_message(int(ref_id), f"🎉 New Refer! +$0.02\n👤 {user['name']}\n💰 Balance: ${users[ref_id]['balance']:.4f}")
            except: pass

    save_data(users)
    
    if not is_user_joined(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ Check Joined", callback_data="check_join"))
        bot.send_message(message.chat.id, f"👋 Welcome {message.from_user.first_name}!\n\n💰 Gold Bux Bot e Income Shuru Koro!\n\n⚠️ Age amader Channel e Join korte hobe:\n\n{CHANNEL_LINK}\n\nJoin kore Check button e click koro!", reply_markup=markup)
        return

    bot.send_message(message.chat.id, f"✅ Welcome Back {message.from_user.first_name}!\n\n💰 Balance: ${user['balance']:.4f}\n📋 6 ta task complete kore $0.097 free nao!\n\nNicher menu theke kaj shuru koro 👇", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: c.data=="check_join")
def check_join(call):
    if is_user_joined(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Joined! Ekhon kaj shuru koro 👇", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ Channel e join koro nai! Join kore abar Check koro", show_alert=True)

@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def balance(message):
    users = load_data()
    user = get_user(message.from_user.id, users)
    bot.send_message(message.chat.id, f"💰 Your Balance\n\n💵 Balance: ${user['balance']:.4f} (~{user['balance']*124:.2f} TK)\n✅ Completed Tasks: {len(user['completed_tasks'])}\n👥 Referrals: {user['referrals']}\n\n💳 Min Withdraw: $0.10\n🎁 Daily Bonus: $0.005\n👥 Refer Bonus: $0.02 per friend", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text=="📋 Tasks (6)" or m.text=="Tasks")
def show_tasks(message):
    bot.send_message(message.chat.id, "📋 Tomar Tasks (6):\n\n1 task = $0.01 - $0.05\nSob complete = $0.097 = 12 TK\n\nTask e click koro 👇", reply_markup=tasks_markup())

@bot.callback_query_handler(func=lambda c: c.data.startswith("task_"))
def task_detail(call):
    tid = int(call.data.split("_")[1])
    task = next((t for t in DEFAULT_TASKS if t['id']==tid), None)
    if not task: return
    users = load_data()
    user = get_user(call.from_user.id, users)
    
    markup = types.InlineKeyboardMarkup()
    if task['link']:
        markup.add(types.InlineKeyboardButton("🔗 Open Link", url=task['link']))
    if tid in user['completed_tasks']:
        markup.add(types.InlineKeyboardButton("✅ Completed", callback_data="done"))
    else:
        markup.add(types.InlineKeyboardButton("✅ Check & Claim", callback_data=f"claim_{tid}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="task_list"))

    bot.edit_message_text(f"📋 {task['title']}\n\n{task['desc']}\n\n💰 Reward: ${task['reward']}", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("claim_"))
def claim_task(call):
    tid = int(call.data.split("_")[1])
    users = load_data()
    user = get_user(call.from_user.id, users)
    
    if tid in user['completed_tasks']:
        bot.answer_callback_query(call.id, "✅ Already completed!")
        return

    task = next((t for t in DEFAULT_TASKS if t['id']==tid), None)
    
    # Daily bonus check
    if task.get('daily'):
        if user['last_bonus']:
            last = datetime.fromisoformat(user['last_bonus'])
            if datetime.now() - last < timedelta(hours=24):
                remain = 24 - (datetime.now() - last).seconds//3600
                bot.answer_callback_query(call.id, f"❌ 24h por abar! {remain}h baki", show_alert=True)
                return
        user['last_bonus'] = datetime.now().isoformat()
    
    else:
        # Channel join check for task 1,2,4
        if tid in [1,2,4]:
            if not is_user_joined(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Channel e join koro nai! Age join koro", show_alert=True)
                return

    user['balance'] += task['reward']
    user['completed_tasks'].append(tid)
    save_data(users)
    bot.answer_callback_query(call.id, f"✅ ${task['reward']} Added! Balance: ${user['balance']:.4f}")
    bot.edit_message_text(f"✅ Completed! +${task['reward']}\n\n💰 New Balance: ${user['balance']:.4f}\n\nAro task baki ache!", call.message.chat.id, call.message.message_id, reply_markup=tasks_markup())

@bot.callback_query_handler(func=lambda c: c.data in ["task_list","back_menu","done"])
def back_tasks(call):
    if call.data=="back_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Main Menu 👇", reply_markup=main_menu())
    elif call.data=="done":
        bot.answer_callback_query(call.id, "Already done!")
    else:
        bot.edit_message_text("📋 Tomar Tasks (6):", call.message.chat.id, call.message.message_id, reply_markup=tasks_markup())

@bot.message_handler(func=lambda m: m.text=="👥 Refer")
def refer(message):
    users = load_data()
    user = get_user(message.from_user.id, users)
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start={message.from_user.id}"
    bot.send_message(message.chat.id, f"👥 Refer & Earn\n\n🔗 Tomar Link:\n{link}\n\n💰 Per Refer: $0.02\n👥 Total Refer: {user['referrals']}\n💵 Refer Earn: ${user['referrals']*0.02:.4f}\n\nBondhuder share koro!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text=="🎁 Daily Bonus")
def daily_bonus(message):
    users = load_data()
    user = get_user(message.from_user.id, users)
    if user['last_bonus']:
        last = datetime.fromisoformat(user['last_bonus'])
        if datetime.now() - last < timedelta(hours=24):
            remain = 24 - int((datetime.now() - last).total_seconds()//3600)
            bot.send_message(message.chat.id, f"❌ Bonus already claimed!\n⏰ {remain} hour por abar pabe\n\n💰 Balance: ${user['balance']:.4f}", reply_markup=main_menu())
            return
    user['balance'] += 0.005
    user['last_bonus'] = datetime.now().isoformat()
    save_data(users)
    bot.send_message(message.chat.id, f"🎁 Daily Bonus Claimed!\n\n💰 +$0.005 Added!\n💵 New Balance: ${user['balance']:.4f}", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text=="💳 Withdraw")
def withdraw(message):
    users = load_data()
    user = get_user(message.from_user.id, users)
    if user['balance'] < 0.10:
        bot.send_message(message.chat.id, f"❌ Balance kom!\n\n💰 Tomar: ${user['balance']:.4f}\n💳 Minimum: $0.10\n\nAro task koro!", reply_markup=main_menu())
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("💳 bKash", callback_data="wd_bKash"),
               types.InlineKeyboardButton("💳 Nagad", callback_data="wd_Nagad"))
    markup.add(types.InlineKeyboardButton("💰 Binance USDT", callback_data="wd_Binance"))
    bot.send_message(message.chat.id, f"💳 Withdraw\n\n💰 Balance: ${user['balance']:.4f}\n💵 Min: $0.10\n\nMethod select koro:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("wd_"))
def wd_method(call):
    method = call.data.split("_")[1]
    user_states[call.from_user.id] = {"step": "account", "method": method}
    bot.send_message(call.message.chat.id, f"💳 {method} selected!\n\n🔢 Tomar {method} number/wallet address dao:")

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id].get("step")=="account")
def wd_account(message):
    state = user_states[message.from_user.id]
    state['account'] = message.text
    state['step'] = "amount"
    bot.send_message(message.chat.id, f"✅ Account: {message.text}\n\n💵 Koto withdraw korba? (Example: 0.10)\nMin $0.10")

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id].get("step")=="amount")
def wd_amount(message):
    try:
        amount = float(message.text)
    except:
        bot.send_message(message.chat.id, "❌ Sothik amount likho! Example: 0.10")
        return
    users = load_data()
    user = get_user(message.from_user.id, users)
    if amount < 0.10 or amount > user['balance']:
        bot.send_message(message.chat.id, f"❌ Invalid!\nBalance: ${user['balance']:.4f}\nMin: $0.10")
        return
    
    state = user_states[message.from_user.id]
    method = state['method']
    account = state['account']
    
    user['balance'] -= amount
    save_data(users)
    
    withdraws = load_withdraws()
    record = {
        "user_id": message.from_user.id,
        "name": message.from_user.first_name,
        "username": message.from_user.username or "",
        "method": method,
        "account": account,
        "amount": amount,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending"
    }
    withdraws.append(record)
    save_withdraws(withdraws)
    
    bot.send_message(message.chat.id, f"✅ Withdraw Request Done!\n\n💳 Method: {method}\n🔢 Account: {account}\n💵 Amount: ${amount:.4f} (~{amount*124:.0f} TK)\n\n⏰ 24h er moddhe payment pabe!\n💰 New Balance: ${user['balance']:.4f}", reply_markup=main_menu())
    
    if ADMIN_ID != 0:
        try:
            bot.send_message(ADMIN_ID, f"🔔 NEW WITHDRAW!\n\n👤 {record['name']} (@{record['username']})\n🆔 {record['user_id']}\n💳 {method}: {account}\n💵 ${amount:.4f}\n⏰ {record['time']}")
        except: pass
    
    del user_states[message.from_user.id]

@bot.message_handler(func=lambda m: m.text=="📊 Stats")
def stats(message):
    users = load_data()
    total_users = len(users)
    user = get_user(message.from_user.id, users)
    bot.send_message(message.chat.id, f"📊 Stats\n\n👥 Total Users: {total_users}\n💰 Your Balance: ${user['balance']:.4f}\n✅ Tasks Done: {len(user['completed_tasks'])}/6\n👥 Referrals: {user['referrals']}\n\n🚀 Keep Earning!", reply_markup=main_menu())

# ===== ADMIN COMMANDS =====
@bot.message_handler(commands=['admin','addbalance','autoposton','autopostoff','addgroup','listgroups','removegroup','autopoststatus'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Admin only!")
        return
    txt = message.text
    if txt.startswith('/addbalance'):
        try:
            parts = txt.split()
            uid = parts[1]
            amt = float(parts[2])
            users = load_data()
            if uid in users:
                users[uid]['balance'] += amt
                save_data(users)
                bot.send_message(message.chat.id, f"✅ Added ${amt} to {uid}\nNew: ${users[uid]['balance']:.4f}")
                try: bot.send_message(int(uid), f"🎉 Admin added ${amt} to your balance!\n💰 New: ${users[uid]['balance']:.4f}")
                except: pass
            else: bot.send_message(message.chat.id, "❌ User not found!")
        except: bot.send_message(message.chat.id, "Use: /addbalance USER_ID AMOUNT\nEx: /addbalance 123456789 0.05")
    
    elif txt.startswith('/addgroup'):
        try:
            g = txt.split()[1]
            if not g.startswith('@'): g='@'+g
            if g not in GROUPS:
                GROUPS.append(g)
                save_groups()
                bot.send_message(message.chat.id, f"✅ Added {g}\nTotal: {len(GROUPS)}")
            else: bot.send_message(message.chat.id, "Already added!")
        except: bot.send_message(message.chat.id, "Use: /addgroup @groupname")
    
    elif txt.startswith('/removegroup'):
        try:
            g = txt.split()[1]
            if not g.startswith('@'): g='@'+g
            if g in GROUPS:
                GROUPS.remove(g)
                save_groups()
                bot.send_message(message.chat.id, f"✅ Removed {g}")
            else: bot.send_message(message.chat.id, "Not found!")
        except: bot.send_message(message.chat.id, "Use: /removegroup @groupname")
    
    elif txt.startswith('/listgroups'):
        if not GROUPS: bot.send_message(message.chat.id, "No groups added!")
        else: bot.send_message(message.chat.id, "\n".join(GROUPS))
    
    elif txt.startswith('/autoposton'):
        global auto_post_enabled
        auto_post_enabled=True
        bot.send_message(message.chat.id, f"✅ Auto Post ON - {len(GROUPS)} groups")
    elif txt.startswith('/autopostoff'):
        auto_post_enabled=False
        bot.send_message(message.chat.id, "❌ Auto Post OFF")
    elif txt.startswith('/autopoststatus'):
        bot.send_message(message.chat.id, f"Status: {'ON' if auto_post_enabled else 'OFF'}\nGroups: {len(GROUPS)}\n{', '.join(GROUPS)}")
    elif txt.startswith('/admin'):
        bot.send_message(message.chat.id, f"👑 Admin Panel\n\nUsers: {len(load_data())}\nWithdraws: {len(load_withdraws())}\nGroups: {len(GROUPS)}\n\nCommands:\n/addbalance ID AMOUNT\n/addgroup @name\n/removegroup @name\n/listgroups\n/autoposton\n/autopostoff\n/autopoststatus")

@bot.message_handler(func=lambda m: True)
def default_handler(message):
    if message.from_user.id in user_states:
        return
    bot.send_message(message.chat.id, "Menu theke select koro 👇", reply_markup=main_menu())

# Start Auto Poster
try:
    Thread(target=auto_post_loop, daemon=True).start()
except: pass

print("Gold Bux Bot Started! Polling...")
try: bot.delete_webhook(drop_pending_updates=True)
except: pass

while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
    except Exception as e:
        print(f"Polling error: {e}")
        time.sleep(5)
