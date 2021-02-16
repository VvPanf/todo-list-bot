import telebot
import flask
import os
import logging
from telebot import types
from enum import Enum
import python.sqlite_repo as repo
from python.text_templates import *

API_TOKEN = os.environ.get("BOT_TOKEN")

PAGE_SIZE = 5

class MENU_ACTIONS(Enum):
    CLOSE = "close"
    EDIT = "edit"
    NEXT = "next"
    PREV = "prev"


bot = telebot.AsyncTeleBot(API_TOKEN)


# Инициалицазия и подсказка
@bot.message_handler(commands=['start', 'help'])
def handle_start_commands(message):
    user = message.chat.id
    repo.add_user_if_not_exists(user)
    bot.send_message(user, hello_message, parse_mode="Markdown")

# Удаление данных пользователя
@bot.message_handler(commands=['exit'])
def handle_exit_command(message):
    user = message.chat.id
    repo.delete_user(user)
    bot.send_message(user, user_data_deleted)

# Создание нового списка
@bot.message_handler(commands=['new'])
def handle_new_command(message):
    user = message.chat.id
    repo.change_state(user, repo.STATES.S_ENTER_LIST_AND_ITEMS.value)
    bot.send_message(user, enter_list_name)

# Ввод названия списка и его элементов
@bot.message_handler(func=lambda message: repo.get_state(message.chat.id) == repo.STATES.S_ENTER_LIST_AND_ITEMS.value,
                     content_types=['text'])
def handle_enter_list_name(message):
    bot.send_message(message.chat.id, "...")
    user = message.chat.id
    lines = message.text.split('\n')
    name = lines[0]
    items = lines[1:]
    repo.add_list(repo.find_user_id(user), name)
    list_id = repo.get_list_id(repo.find_user_id(user), name)
    for item in items:
        repo.add_item(list_id, item)
    repo.change_state(user, repo.STATES.S_START.value)
    bot.send_message(user, list_added)

# Вывод всех списков пользователя
@bot.message_handler(commands=['lists'])
def handle_lists_command(message):
    user = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    for el in repo.get_lists(repo.find_user_id(user)):
        keyboard.add(types.InlineKeyboardButton(text=el[1], callback_data='list=' + str(el[0])))
    keyboard.add(types.InlineKeyboardButton(text=close_sign + ' Закрыть', callback_data=MENU_ACTIONS.CLOSE.value))
    bot.send_message(user, list_list, reply_markup=keyboard)

# Вывод всех списков пользователя для удаления
@bot.message_handler(commands=['delete'])
def handle_lists_command(message):
    user = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    for el in repo.get_lists(repo.find_user_id(user)):
        keyboard.add(types.InlineKeyboardButton(text=el[1], callback_data='delete=' + str(el[0])))
    bot.send_message(user, delete_list, reply_markup=keyboard)

# Постановка галочки на элементе списка
@bot.callback_query_handler(func=lambda call: call.data.startswith('item'))
def callback_inline_item(call):
    if call.message:
        user = call.message.chat.id
        lists, curr_page, count_page = parse_list_header(call.message.text)
        list_id = repo.get_list_id(repo.find_user_id(user), lists)
        keyboard = types.InlineKeyboardMarkup(row_width=4)
        items = repo.get_items(list_id)
        for item in items[curr_page*PAGE_SIZE:curr_page*PAGE_SIZE+PAGE_SIZE]:
            if 'item=' + str(item[0]) == call.data:
                repo.change_item_checked(item[0], not bool(item[2]))
                keyboard.add(types.InlineKeyboardButton(text=set_item_text(not bool(item[2]), item[1]), callback_data=set_callback_item(item[0])))
            else:
                keyboard.add(types.InlineKeyboardButton(text=set_item_text(bool(item[2]), item[1]), callback_data=set_callback_item(item[0])))
        keyboard = get_menu_buttons(keyboard, count_page > 0)
        bot.edit_message_reply_markup(user, call.message.message_id, reply_markup=keyboard)

# Вывод элементов списка при нажатии на нужный список
@bot.callback_query_handler(func=lambda call: call.data.startswith('list'))
def callback_inline_list(call):
    if call.message:
        user = call.message.chat.id
        list_id = int(call.data.replace('list=', ''))
        name = repo.get_list_name(list_id)
        keyboard = types.InlineKeyboardMarkup(row_width=4)
        items = repo.get_items(list_id)
        for item in items[:PAGE_SIZE]:
            keyboard.add(types.InlineKeyboardButton(text=set_item_text(bool(item[2]), item[1]),
                                                    callback_data=set_callback_item(item[0])))
        keyboard = get_menu_buttons(keyboard, len(items) > PAGE_SIZE)
        bot.delete_message(user, call.message.message_id)
        msg = (str(name) + "\n0/" + str(int(len(items) / PAGE_SIZE))) if len(items) > PAGE_SIZE else str(name)
        bot.send_message(user, msg, reply_markup=keyboard)

# Удаление выбранного списка
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete'))
def callback_inline_delete(call):
    if call.message:
        user = call.message.chat.id
        list_id = int(call.data.replace('delete=', ''))
        repo.delete_list(list_id)
        bot.delete_message(user, call.message.message_id)
        bot.send_message(user, list_is_deleted)

# Закрытие сообщения со списком
@bot.callback_query_handler(func=lambda call: call.data.startswith(MENU_ACTIONS.CLOSE.value))
def callback_inline_close(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

# Редактирование списка
@bot.callback_query_handler(func=lambda call: call.data.startswith(MENU_ACTIONS.EDIT.value))
def callback_inline_close(call):
    user = call.message.chat.id
    repo.change_state(user, repo.STATES.S_EDIT_LIST.value)
    bot.delete_message(call.message.chat.id, call.message.message_id)

# Предыдущая страница списка
@bot.callback_query_handler(func=lambda call: call.data.startswith(MENU_ACTIONS.NEXT.value))
def callback_inline_next(call):
    next_or_prev_button(call, 1)

# Следующая страница списка
@bot.callback_query_handler(func=lambda call: call.data.startswith(MENU_ACTIONS.PREV.value))
def callback_inline_prev(call):
    next_or_prev_button(call, -1)


def set_item_text(checked, content):
    if checked:
        return checked_sign + ' ' + content
    return unchecked_sign + ' ' + content


def set_callback_item(s):
    return 'item='+str(s)


def get_menu_buttons(keyboard, all_buttons = True):
    if all_buttons:
        return keyboard.row(
            types.InlineKeyboardButton(text=prev_sign, callback_data=MENU_ACTIONS.PREV.value),
            types.InlineKeyboardButton(text=edit_sign, callback_data=MENU_ACTIONS.EDIT.value),
            types.InlineKeyboardButton(text=close_sign, callback_data=MENU_ACTIONS.CLOSE.value),
            types.InlineKeyboardButton(text=next_sign, callback_data=MENU_ACTIONS.NEXT.value))
    else:
        return keyboard.row(
            types.InlineKeyboardButton(text=edit_sign, callback_data=MENU_ACTIONS.EDIT.value),
            types.InlineKeyboardButton(text=close_sign, callback_data=MENU_ACTIONS.CLOSE.value))


def next_or_prev_button(call, i):
    user = call.message.chat.id
    lists, curr_page, count_page = parse_list_header(call.message.text)
    if count_page > 0:
        curr_page += i
        if curr_page > count_page:
            curr_page = 0
        if curr_page < 0:
            curr_page = count_page
        msg = str(lists) + '\n' + str(curr_page) + '/' + str(count_page)
        keyboard = get_list_items_keyboard(repo.get_list_id(repo.find_user_id(user), lists), curr_page)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=keyboard)


def get_list_items_keyboard(list_id, curr_page):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    items = repo.get_items(list_id)[curr_page*PAGE_SIZE:curr_page*PAGE_SIZE+PAGE_SIZE]
    for item in items:
        keyboard.add(types.InlineKeyboardButton(text=set_item_text(bool(item[2]), item[1]),
                                                callback_data=set_callback_item(item[0])))
    keyboard = get_menu_buttons(keyboard)
    return keyboard


def parse_list_header(header):
    list_header = header.split('\n')
    lists = list_header[0]
    curr_page = 0
    count_page = 0
    if len(list_header) > 1:
        curr_page = int(list_header[1].split('/')[0])
        count_page = int(list_header[1].split('/')[1])
    return lists, curr_page, count_page


repo.create_tebles()
# Проверим, есть ли переменная окружения Хероку (как ее добавить смотрите ниже)
if 'IS_HEROKU' in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)
    app = flask.Flask(__name__)

    @app.route('/' + API_TOKEN, methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(flask.request.stream.read().decode("utf-8"))])
        return "!", 200

    @app.route('/')
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url="https://todo-list-bot-app.herokuapp.com/" + API_TOKEN)  # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200

else:
    bot.remove_webhook()
    bot.polling(none_stop=True)