import telebot

bot = telebot.TeleBot('896659837:AAFx8LMpzFoSSOlOqMHMpvY1RlwAIh9yfz0')


@bot.message_handler(commands=['start', 'help'])
def handle_start_commands(message):
    pass


@bot.message_handler(commands=['new'])
def handle_new_command(message):
    pass


@bot.message_handler(commands=['lists'])
def handle_lists_command(message):
    pass


bot.polling(none_stop=True, interval=0)