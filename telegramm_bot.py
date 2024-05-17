import json
import sys
import os
import telebot
import random
from telebot.types import InputFile
from database import check_passwd, add_user, check_user, add_task_db, check_task_db, del_task_num_db
from configure import token

bot = telebot.TeleBot(token)
hand = 0


@bot.message_handler(commands=['deltask'])
def del_task(message):
    reg_id = check_user(message)
    task_num = bot.send_message(message.chat.id, 'Введите номер заявки который хотите удалить')
    bot.register_next_step_handler(task_num, del_task_num, reg_id)


def del_task_num(task_num, reg_id):
    try:
        task_num = int(task_num.text)
        del_task_num_db(int(task_num), reg_id)
    except ValueError:
        bot.send_message(task_num.chat.id, 'Введено недопутимое значение!\n' +
                         'Повторите ввод /deltask .')


@bot.message_handler(commands=['checktask'])
def add_new_task(message):
    data = check_task_db(message)
    if data:
        bot.send_message(message.chat.id, 'Ваши заявки:')
        for task_id, task_name in data:
            bot.send_message(message.chat.id, f'{task_id} - {task_name}')
    else:
        bot.send_message(message.chat.id, 'У вас нет открытых заявок!')


@bot.message_handler(commands=['addtask'])
def add_new_task(message):
    #получение команды добавления новой заяки и получение названия заявки, дальше передаём в функцию add_task_name
    task_name = bot.send_message(message.chat.id, 'Введите название заявки: \n' +
                                                  'Для прекращения добавления введи "НЕТ" ')
    reg_id = check_user(message)
    #print(task_name, add_task_name, reg_id, sep='\n')
    bot.register_next_step_handler(task_name, add_task_name, reg_id)


def add_task_name(task_name, reg_id):
    #запрашиваем текст заявки и передаём всё дальше в add_task_text
    #print(task_name.text)
    if task_name.text.lower() == 'нет':
        print('НЕТ')
    else:
        # with open('products.json', 'r', encoding='utf-8') as file:
        #     data = json.load(file)
        task_text = bot.send_message(task_name.chat.id, 'Введите текст заявки: \n' +
                                                        'Максимально подробно опишите суть проблемы или задачи.\n' +
                                                        'Для прекращения добавления введи "НЕТ" ')
        #bot.get_updates(limit=1, timeout=1, offset=-1)
        bot.register_next_step_handler(task_text, add_task_text, task_name, reg_id)


def add_task_text(task_text, task_name, reg_id):
    #отправляем данные по заявке в функцию add_task_db, которая добавляет данные в базу
    if task_text.text.lower() == 'нет':
        print('НЕТ')
    else:
        #print(task_name.text, task_text.text, reg_id, sep='\n')
        task_id = add_task_db(task_name, task_text, reg_id)
        bot.send_message(task_text.chat.id, f'Заявка создана. Номер заявки {task_id}')


@bot.message_handler(commands=['reg'])
def start_command(message):
    reg_id = check_user(message)
    if reg_id:
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
    else:
        mesg = bot.send_message(message.chat.id, 'Введите пароль выданный вам для регистрации: ')
        bot.register_next_step_handler(mesg, registation)


def registation(message):
    if check_passwd(message):
        add_user(message)
        bot.send_message(message.chat.id, 'Вы успешно зарегистрированы!')
    else:
        bot.send_message(message.chat.id, 'Вы ввели недействительный пароль.\n Повторите попытку регистрации /reg')


@bot.message_handler(commands=['cat'])
def start_command(message):
    #  отправляет пользователю в ответ на любой текст картинку с котиком
    path = r'stickers_cat'
    data = os.listdir(path)
    image = random.choice(data)
    path_image = (f'{path}/{image}')
    with open(path_image, 'rb') as f:
        bot.send_document(
            message.chat.id,
            InputFile(f)
        )


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        'Поздравляю! Теперь мы можем сыграть в игру 21.\n' +
        'Для начала игры набери команду /g21.\n' +
        'Для регистрации набери команду /reg.\n' +
        'Для получания помощи /help.'
    )


@bot.message_handler(commands=['hi'])
def hi_command(message):
    bot.send_message(
        message.chat.id,
        'И тебе привет!'
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Сообщить разработчику', url='telegram.me/flint93'
        )
    )
    bot.send_message(
        message.chat.id,
        'Если что-то работает не так, обратитесь к разработчику.',
        reply_markup=keyboard
    )


@bot.message_handler(commands=['g21'])
def g21_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('ДА', callback_data='get-YES'),
        telebot.types.InlineKeyboardButton('НЕТ', callback_data='get-NO')
    )
    global hand
    hand = random.randrange(2, 11)
    bot.send_message(
        message.chat.id,
        'Начинаем игру!\n' +
        f'У вас {hand}\n' +
        'Хотите добрать ещё?',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        if data == ('get-YES'):
            g21_yes(query.message)
        elif data == ('get-NO'):
            g21_no(query.message)
        else:
            g21_command(query.message)


def g21_yes(message):
    global hand
    hand += random.randrange(2, 11)
    if hand == 21:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('ЗАНОВО!', callback_data='get-RESTART')
        )
        bot.send_message(
            message.chat.id,
            'Вы выиграли!',
            #reply_markup=keyboard
        )
    elif hand > 21:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('ЗАНОВО?', callback_data='get-RESTART')
        )
        bot.send_message(
            message.chat.id,
            f'У вас {hand} очков\n' +
            'Вы проиграли!',
            reply_markup=keyboard
        )
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('ДА', callback_data='get-YES'),
            telebot.types.InlineKeyboardButton('НЕТ', callback_data='get-NO')
        )
        bot.send_message(
            message.chat.id,
            f'У вас {hand}\n' +
            'Хотите добрать ещё?',
            reply_markup=keyboard
        )


def g21_no(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('ЗАНОВО?', callback_data='get-RESTART')
    )
    bot_hand = random.randrange(15, 25)
    if bot_hand >= 22 or hand >= bot_hand:
        bot.send_message(
            message.chat.id,
            f'У вас {hand} очков, у вашего аппонента {bot_hand} очков\n' +
            'Вы выиграли!',
            reply_markup=keyboard
        )
    else:
        bot.send_message(
            message.chat.id,
            f'У вас {hand} очков, у вашего аппонента {bot_hand} очков\n' +
            'Вы проиграли!',
            reply_markup=keyboard
        )


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    # bot.reply_to(message, message.text)
    bot.reply_to(message, message.from_user.id)


bot.infinity_polling()
