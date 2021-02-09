import telebot
from telebot import types
import python.repo as repo
from python.text_templates import *

bot = telebot.TeleBot('896659837:AAFx8LMpzFoSSOlOqMHMpvY1RlwAIh9yfz0')


@bot.message_handler(commands=['start', 'help'])
def handle_start_commands(message):
    user = message.chat.id
    repo.add_user_if_not_exists(user)
    bot.send_message(user, hello_message, parse_mode="Markdown")


@bot.message_handler(commands=['new'])
def handle_new_command(message):
    user = message.chat.id
    repo.change_state(user, repo.STATES.S_ENTER_LIST_AND_ITEMS.value)
    bot.send_message(user, enter_list_name)


@bot.message_handler(func=lambda message: repo.get_state(message.chat.id) == repo.STATES.S_ENTER_LIST_AND_ITEMS.value,
                     content_types=['text'])
def handle_enter_list_name(message):
    user = message.chat.id
    lines = message.text.split('\n')
    name = lines[0]
    items = lines[1:]
    repo.add_list(repo.find_user_id(user), name)
    list_id = repo.get_list_id(repo.find_user_id(user), name)
    for item in items:
        repo.add_item(list_id, item)
    repo.change_state(user, repo.STATES.S_SHOW_LIST.value)
    bot.send_message(user, list_added)


@bot.message_handler(commands=['lists'])
def handle_lists_command(message):
    user = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    for el in repo.get_lists(repo.find_user_id(user)):
        keyboard.add(types.InlineKeyboardButton(text=el[1], callback_data='list=' + str(el[0])))
    bot.send_message(user, list_list, reply_markup=keyboard)


@bot.message_handler(commands=['delete'])
def handle_lists_command(message):
    user = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    for el in repo.get_lists(repo.find_user_id(user)):
        keyboard.add(types.InlineKeyboardButton(text=el[1], callback_data='delete=' + str(el[0])))
    bot.send_message(user, delete_list, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data.startswith('item'):
            user = call.message.chat.id
            list_id = repo.get_list_id(repo.find_user_id(user), call.message.text)
            keyboard = types.InlineKeyboardMarkup()
            for item in repo.get_items(list_id):
                if 'item=' + str(item[0]) == call.data:
                    repo.change_item_checked(item[0], not bool(item[2]))
                    keyboard.add(types.InlineKeyboardButton(text=set_item_text(not bool(item[2]), item[1]), callback_data=set_callback_item(item[0])))
                else:
                    keyboard.add(types.InlineKeyboardButton(text=set_item_text(bool(item[2]), item[1]), callback_data=set_callback_item(item[0])))
            bot.edit_message_reply_markup(user, call.message.message_id, reply_markup=keyboard)
        elif call.data.startswith('list'):
            user = call.message.chat.id
            list_id = int(call.data.replace('list=', ''))
            name = repo.get_list_name(list_id)
            keyboard = types.InlineKeyboardMarkup()
            for item in repo.get_items(list_id):
                keyboard.add(types.InlineKeyboardButton(text=set_item_text(bool (item[2]), item[1]), callback_data=set_callback_item(item[0])))
            bot.send_message(user, name, reply_markup=keyboard)
        elif call.data.startswith('delete'):
            user = call.message.chat.id
            list_id = int(call.data.replace('delete=', ''))
            repo.delete_list(list_id)
            bot.send_message(user, list_is_deleted)


def set_item_text(checked, content):
    if checked:
        return checked_sign + ' ' + content
    return unchecked_sign + ' ' + content


def set_callback_item(s):
    return 'item='+str(s)


bot.polling(none_stop=True, interval=0)
