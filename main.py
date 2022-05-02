import telebot
from telebot import types
import json

bot = telebot.TeleBot("5113897551:AAHrjwo-piDc7OBWs9OI9eu2FON0B-LkZkw")

main_markup = types.ReplyKeyboardMarkup(row_width=2)
main_markup.add('▶️ Получить задание', '📈 Рекламодателю', '💵 Баланс', '💸 Вывод 💸', 'Информация о боте',
                '👥 Рефералы')

payment = types.ReplyKeyboardMarkup(row_width=2)
payment.add('Qiwi', 'ЮMoney', 'Банковская карта')

ads = types.ReplyKeyboardMarkup(row_width=1)
ads.add('📊 Активные задачи')

admin_markup = types.ReplyKeyboardMarkup(row_width=1)
admin_markup.add('Добавление админов', 'Добавить задание', 'Рассылка')
with open("users.json", "r") as us_file:
    users = json.load(us_file)

with open("advertisers.json", "r") as us_file:
    advertisers = json.load(us_file)

with open("tasks.json", "r") as ff:
    tasks = json.load(ff)

with open('admins.txt', 'r') as fff:
    admins = fff.readlines()

status = None
num = 0
status_pay = 0
method = None


def check(chat_check_id, check_user_id):
    statuss = ['creator', 'administrator', 'member']
    try:
        user_status = str(bot.get_chat_member(chat_id=chat_check_id, user_id=check_user_id).status)
        if user_status in statuss:
            return 1
        else:
            return 0
    except:
        return 0


@bot.callback_query_handler(func=lambda c: True)
def inlin(c):
    chanel_id = tasks[c.data][0]
    if chanel_id in users[str(c.message.chat.id)]["tasks"]:
        bot.send_message(c.message.chat.id, "Вы уже получили награду!")
        return
    res_check = check(chanel_id, c.message.chat.id)
    if res_check == 1:
        users[str(c.message.chat.id)]["balance"] += 0.20
        users[str(c.message.chat.id)]["tasks"].append(chanel_id)
        tasks[c.data][1] += 1
        if tasks[c.data][1] >= int(tasks[c.data][2]):
            tasks.pop(c.data)
            advertisers[str(c.message.chat.id)] -= 1
            with open("advertisers.json", "w") as tasks_file:
                json.dump(advertisers, tasks_file)
        with open("tasks.json", "w") as tasks_file:
            json.dump(tasks, tasks_file)
        bot.send_message(c.message.chat.id,
                         "Ваша подписка на канал была засчитана. 💵 Вам было начислено 0.20руб! 💵")
    elif res_check == 0:
        bot.send_message(c.message.chat.id, "⛔️ Вы не подписались на канал! ⛔️")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id != message.from_user.id:
        return
    # if admin
    if str(message.chat.id) in admins:
        bot.send_message(message.chat.id, "Привет! Ты распознан как админ!", reply_markup=admin_markup)
        return
    # if the message is first
    if not str(message.chat.id) in users:
        users[str(message.chat.id)] = {
            "balance": 0,
            "withdrawn": 0,
            "tasks": [],
            "referals": []
        }
        # если реферал
        if " " in message.text:
            referrer_candidate = message.text.split()[1]
            if str(referrer_candidate) in users:
                return
            try:
                referrer = int(referrer_candidate)
                users[str(referrer)]["referals"].append(referrer)
                users[str(referrer)]["balance"] += 0.02
            except ValueError:
                pass
    bot.send_message(message.chat.id,
                     "Привет! \nЕсли ты здесь для заработка - жми Получить задание. \nЕсли для накрутки в свой канал "
                     "- Рекламодателю.",
                     reply_markup=main_markup)
    with open("users.json", "w") as json_file:
        json.dump(users, json_file)


@bot.message_handler(content_types=['text'])
def main(message):
    if message.chat.id != message.from_user.id:
        return
    # админка
    global status
    global num
    global status_pay
    global method
    consts = ["add_admin", "add_task", "mailing", "add_button", "del_button"]
    if str(message.chat.id) in admins:
        if message.text == "Добавление админов":
            bot.send_message(message.chat.id, "Пришлите ID нового админа.")
            status = "add_admin"
            return
        elif message.text == "Добавить задание":
            bot.send_message(message.chat.id,
                             "Пришлите канал в формате ссылка >> его id >> колличество подписчиков, которое нужно >> "
                             "набрать (через пробел) >> id его админа ")
            status = "add_task"
            return
        elif message.text == "Рассылка":
            bot.send_message(message.chat.id, "Пришлите сообщение, которое нужно отправить всем пользователям")
            status = "mailing"
            return
        if status in consts:
            if status == "add_admin":
                admins.append(message.text)
                with open('admins.txt', 'a') as qwe:
                    qwe.write("\n{}".format(message.text))
                bot.send_message(message.chat.id, "Админ успешно добавлен!")
                status = None
            elif status == "add_task":
                try:
                    task_mas = message.text.split()
                    tasks[task_mas[0]] = [task_mas[1], 0, task_mas[2]]
                    advertisers[str(message.chat.id)] = [task_mas[3]]
                    with open("tasks.json", "w") as tasks_file:
                        json.dump(tasks, tasks_file)
                    with open("advertisers.json", "w") as tasks_file:
                        json.dump(advertisers, tasks_file)
                    bot.send_message(message.chat.id, "Задание успешно добавлено!")
                except:
                    bot.send_message(message.chat.id, "Неверный формат ввода!")
                    status = None
                    return
                status = None
            elif status == "mailing":
                for elem in users:
                    try:
                        bot.send_message(elem, message.text)
                    except:
                        pass
                bot.send_message(message.chat.id, "Рассылка завершена")
                status = None
        with open("users.json", "w") as json_file:
            json.dump(users, json_file)
        status = None
        return
    if message.text == "▶️ Получить задание":
        task_link = ""
        user_tasks = users[str(message.chat.id)]["tasks"]
        for elem in tasks:
            if not tasks[elem][0] in user_tasks:
                task_link = elem
                try:
                    a = str(bot.get_chat_member(chat_id=-1001531991308, user_id=5113897551).status)
                    break
                except telebot.apihelper.ApiTelegramException:
                    task_link = ""
                    continue
        if task_link == "":
            bot.send_message(message.chat.id,
                             "Хорошая работа! Вы выполнили все задания! Через некоторое время появятся новые!")
            return

        # клавиатура
        task_keyboard = types.InlineKeyboardMarkup()
        link = types.InlineKeyboardButton(text='Перейти к каналу', url=task_link)
        check_button = types.InlineKeyboardButton(text="Проверить подписку", callback_data=task_link)
        task_keyboard.add(link, check_button)
        bot.send_message(message.chat.id,
                         "Для выполнения задания необходимо подписаться на канал и подтвердить выполнение.",
                         reply_markup=task_keyboard)
    elif message.text == "📈 Рекламодателю":
        bot.send_message(message.chat.id, "‼Что бы добавить свой канал в раскрутку напишите админу: @earleyn_on"
                                          "(Не раскручиваем 18+🔞)", reply_markup=ads)
    elif message.text == "👥 Рефералы":
        bot.send_message(message.chat.id,
                         "👤 Ваша реферальная ссылка:\n\n https://t.me/Actioncore_bot?start={}\n\n👥 Кол-во "
                         "рефералов:{}\n💸 Заработок с рефералов : {}₽".format(message.chat.id, len(users[str(
                             message.chat.id)]["referals"]), len(users[str(
                             message.chat.id)]["referals"]) * 0.02))
    elif message.text == "💵 Баланс":
        bot.send_message(message.chat.id, "🏦 Общий баланс: {} \n"
                                          "👥 Получено с рефералов: {}\n"
                                          "💰 Выплаченно в сумме: {}\n"
                                          "💸 Минимальная сумма вывода: 20₽\n"
                                          "📃 Комиссия QIWI за перевод:\n"
                                          "🥝 QIWI : 2%\n"
                                          "🔄 ЮMoney : 0%\n"
                                          "💳 Банк. карты: 2% + 50₽.\n".
                         format(users[str(message.chat.id)]["balance"],
                                len(users[str(message.chat.id)]["referals"]) * 0.02,
                                users[str(message.chat.id)]["withdrawn"]))
    elif message.text == "💸 Вывод 💸":
        if users[str(message.chat.id)]["balance"] < 20:
            bot.send_message(message.chat.id, "Ваш баланс меньше минимальной суммы для выплаты. Минимум - 20₽")
            return
        else:
            bot.send_message(message.chat.id,
                             "Выберите способ оплаты", reply_markup=payment)
            status_pay = 1
            return
    if status_pay == 1:
        if message.text == "Qiwi":
            method = "Qiwi"
            bot.send_message(message.chat.id,
                             "Отправьте номер кошелька! Если вы отправите неверный номер, напишите @earleyn_on",
                             reply_markup=types.ReplyKeyboardRemove())
            status_pay = 2
            return
        elif message.text == "ЮMoney":
            method = "ЮMoney"
            bot.send_message(message.chat.id,
                             "Отправьте номер счёта! Если вы отправите неверный номер, напишите @earleyn_on",
                             reply_markup=types.ReplyKeyboardRemove())
            status_pay = 2
            return
        elif message.text == "Банковская карта":
            method = "Банковская карта"
            bot.send_message(message.chat.id,
                             "Отправьте номер карты! Если вы отправите неверный номер, напишите @earleyn_on",
                             reply_markup=types.ReplyKeyboardRemove())
            status_pay = 2
            return
        else:
            method = None
            status_pay = 0
            num = 0
            bot.send_message(message.chat.id, "Неверный формат ввода", reply_markup=main_markup)
            return
    elif status_pay == 2:
        num = message.text
        status_pay = 3
        bot.send_message(message.chat.id, "Отправьте сумму вывода")
        return
    elif status_pay == 3:
        try:
            summ = float(message.text)
            if users[str(message.chat.id)]["balance"] >= summ:
                users[str(message.chat.id)]["balance"] -= summ
                bot.send_message(1755776176,
                                 "Пришла заявка на вывод на {} на сумму {} на номер счёта {} от {}. Его id {}".format(
                                     method, summ, num, message.from_user.first_name, message.from_user.id))
                if message.from_user.username is not None:
                    bot.send_message(1819042943, "Его username @" + message.from_user.username)
                bot.send_message(message.chat.id, "Заявка на вывод была успешно отправлена!", reply_markup=main_markup)
                method = None
                status_pay = 0
                num = 0
                return
            else:
                method = None
                status_pay = 0
                num = 0
                bot.send_message(message.chat.id, "Недостачно средств на счету")
                return
        except ValueError:
            method = None
            status_pay = 0
            num = 0
            bot.send_message(message.chat.id, "Неверный формат ввода")
            return


    elif message.text == "Информация о боте":
        bot.send_message(message.chat.id,
                         "С помощью этого бота можно легко зарабатывать, выполняя простые задания в телеграм. А так "
                         "же, заказать накрутку подписчиков для своего телеграм канала.",
                         reply_markup=main_markup)
    elif message.text == "📊 Активные задачи":
        if str(message.chat.id) in advertisers:
            bot.send_message(message.chat.id, "У вас есть {} задач.".format(advertisers[str(message.chat.id)] + 1),
                             reply_markup=main_markup)
        else:
            bot.send_message(message.chat.id, "У вас нет активных задач.", reply_markup=main_markup)
    with open("users.json", "w") as json_file:
        json.dump(users, json_file)


bot.polling()
