from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from config import *



def sub_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Боты логгеры", callback_data="loggers"))
    keyboard.row(InlineKeyboardButton("Поиск логов", callback_data="log_find"), InlineKeyboardButton("Мои логи", callback_data="my_logs"))
    keyboard.row(InlineKeyboardButton("Профиль", callback_data="profile"), InlineKeyboardButton("Информация", callback_data="info"))
    return keyboard


def cancel_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Отмена", callback_data="cancel"))
    return keyboard


def found_info_kb(user_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Пользователь", f"tg://users?id={user_id}"), InlineKeyboardButton("Попробовать снова", callback_data="log_find"))
    keyboard.row(InlineKeyboardButton("Главное меню", callback_data="start"))
    return keyboard


def telegraph_kb(link: str):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Скопировать ссылку", copy_text=CopyTextButton(link)))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="loggers"))
    return keyboard


def log_kb(user_id: int, page_number: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Пользователь", f"tg://users?id={user_id}"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data=f"page_{page_number}"))
    return keyboard


def telegraph_log_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Мои логи", callback_data="my_logs"))
    keyboard.row(InlineKeyboardButton("Главное меню", callback_data="start"))
    return keyboard


def info_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row( InlineKeyboardButton("Администратор", f"tg://user?id={OWNER_ID}"), InlineKeyboardButton("Наш канал", CHANNEL_LINK) )
    keyboard.row( InlineKeyboardButton("Назад", callback_data="start") )
    return keyboard


def main_menu_button_kb(status: bool):
    keyboard = InlineKeyboardMarkup()
    if status:
        keyboard.row(InlineKeyboardButton("Отключить уведомления", callback_data="status_off"))
    else:
        keyboard.row(InlineKeyboardButton("Включить уведомления", callback_data="status_on"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    return keyboard


def unsub_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row( InlineKeyboardButton("Купить подписку", callback_data="buy_sub") )
    keyboard.row( InlineKeyboardButton("Профиль", callback_data="profile"), InlineKeyboardButton("Наш канал", CHANNEL_LINK) )
    return keyboard

def buy_sub_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row( InlineKeyboardButton("1 день | 0.2$", callback_data="sub_1"), InlineKeyboardButton("Неделя | 1$", callback_data="sub_7") )
    keyboard.row( InlineKeyboardButton("Месяц | 3$", callback_data="sub_31"), InlineKeyboardButton("Навсегда | 6$", callback_data="sub_-1") )
    keyboard.row( InlineKeyboardButton("Назад", callback_data="start") )
    return keyboard