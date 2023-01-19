import googlesheets_explorer as gs
import settings
from settings import admin_spreadsheet_id
from datetime import datetime, timedelta
import pytz

descriptionText = """☀️ Поздравляем вас с ещë одним шагом к себе настоящему.

🏄🏼‍♂️ Вас ждëт долгий, а может и короткий путь, где вы сами решаете на каком уровне остановиться, на каком результате. Мы очень рады, что вы выбрали именно нас в свои проводники к себе, своей мечте, своему счастью. 

Для вас подготовлено 3 категории услуг:
⚫️ black
⚪️ silver / silver premium
🟡 gold / gold premium
каждая из них имеет свою ценность и направление.

Вы можете ознакомиться с каждым форматом в разделе «оплата услуг» и выбрать самый подходящий.

Желаем вам хорошого дня, отличного настроения, сил и здоровья) 
Дальше только лучше!"""

mainMenuText = "<b>Главное меню</b>"

aboutUsText = "✅ Главная цель психологического центра \"Новый уровень\" - изменить понимание людей о психологии, " \
              "сломать стереотипы об идеальном психологе, развеять мем о кушетке и о безрезультатной трате своих " \
              "денег в течение 5-10 лет. \n\n" \
              "🏤 Здесь каждый сможет найти для себя тот инструмент, который улучшит качество жизни, " \
              "выведет его из дня сурка, позволит жить, а не выживать. Психология, которая действительно помогает 😌"

enterCodeText = "✏️ Введите, пожалуйста, код с карты, приобретённой вами ранее.\n\n" \
                 "✅ Сразу после активации кода на ваш счет будет зачислена соответствующая услуга"

chooseService = "🔖 Выберите услугу:\n\n" \
                "❗ Подробную информацию об услуге вы можете \nполучить, нажав на соответствующую кнопку с названием " \
                "услуги"

useYorServicesBeforeActivate = "❗ Перед активацией нового кода, запишитесь, пожалуйста, на предыдущую " \
                               "активированную услугу\n\n📎 Информацию о вашей активированной услуге можно " \
                               "получить, зайдя во вкладку \"Мой профиль\""

useYorServicesBeforePay = "❗ Перед оплатой, запишитесь, пожалуйста, на предыдущую " \
                          "активированную услугу\n\n📎 Информацию о вашей активированной услуге можно получить, " \
                          "зайдя во вкладку \"Мой профиль\""

enterYourInfo = "📝 Для того, чтобы продолжить, вам нужно ввести информацию о себе\n\n" \
                "❗ Введенная информация будет доступна во вкладке \"Информация о клиенте\" в главном меню"

askQuestionText = "❓ Здесь вы можете анонимно задать вопрос, ответ на который будет получен в нашем телеграм" \
                  " канале в порядке очереди\n\n" \
                  "❗ Прямо сейчас вы можете ввести текст своего вопроса"

questionPassed = "✅ Ваш вопрос принят, постараемся ответить на него как можно скорее"

signedUpOnConsultation = "✅ Вы успешно записаны на консультацию"

enterFullName = "Введите ФИО"
enterPhoneNumber = "Введите номер телефона"

reenter = "Введите, пожалуйста, ещё раз"
infoUpdated = "✅ Информация успешно обновлена.\n\n" \
              "Теперь вам доступны оплата услуг и ввод кода в главном меню"

scheduleUpdated = "✅ Ваша консультация успешно перенесена"

card_description = {'BLACK': """⚫️ <b>Формат консультации «Black»</b>

Идеально подойдëт для знакомства с психологическим центром «Новый уровень» и с психологией в целом. 

✔️ Продолжительность: 30-40м
✔️Формат: онлайн
✔️1 посещение

Что получаете:
Мы выявим суть проблемы. У вас появится основа для эффективных психологических проработок- понимание дальнейшего направления и путь решения запроса.
В классической психотерапии подобный результат достигается за несколько месяцев.

Рекомендуем воспользоваться этой услугой, перед приобретением других форматов.\n\n""",

                    'SILVER': """⚪️ <b>Формат консультации «Silver»</b>

отлично подойдёт, если вы в целом довольны своей жизнью, но что-то мешает, беспокоит. Также рекомендуем этот формат при нехватке сил и энергии.

✔️ Продолжительность: 1 час
✔️Формат: онлайн
✔️1 посещение

Что получаете:
Вы получите инструментарий для восстановления, сохранения своих сил и обретения спокойствия. Наполненность энергией. Состояние и силы, для реализации задуманного. Избавление от зависимостей.\n\n""",

                    'GOLD': """🟡 <b>Формат консультации «Gold»</b>

Отлично подходит, если вы хотите исполнить свои мечты, самые заветные идеи. Эта услуга направлена на принципиальное улучшение качества жизни а темах семьи, работы, денег, отношений, призвания. 

✔️ Продолжительность: 1 час
✔️Формат: онлайн, очно
✔️1 посещение

Что получаете:

Поможем найти ваш смысл жизни. Произойдёт запуск переформирований на самых глубинных уровнях психики, переписывание родительских предписаний, проработка родовых сценарий, изменения убеждения, раскрытия вашего потенциала, выявление и раскрытия ценностей.

Рекомендуем в начале посетить  предыдущие услуги, такие как Black, Silver или Silver Premium. 


*при очной встрече, с вами свяжется специалист и вышлет координаты кабинета и всю нужную информацию.\n\n""",
                    'SILVER Premium': """⬜️ <b>Формат консультации «Silver Premium. Продвижение»</b>

 "Продвижение" помогает выработать стратегию достижения результата. Рекомендуем приобрести, если вы не хватает сил для и самостоятельного достижения масштабных целей.

Отлично подходит для проработки сложной ситуации, выработку стратегии поведения, обретение  спокойствия и уверенности. 

✔️ Продолжительность: 1 час
✔️Формат: онлайн, аудио
✔️4 консультации ( 1 в неделю)
✔️4 созвон по телефону 10-15 минут (1 раз в неделю)

Что получаете:

Опытный психолог поможет Вам с постановкой цели, подберет техники по индивидуальному плану. 

Во время поддерживающих телефонных разговоров, ваш психолог поможет оценить состояние, поделится своими силами и знаниями, настроем.

В этой услуге акцент ставится на удалении негативных состояний, мешающих получить желаемое, улучшение самочувствия, приобретение энергии и сил.\n\n""",
                    'GOLD Premium': """🟨 <b>Формат консультации «Gold Premium. Продвижение»</b>

Данный формат- это решение исполнить свои мечты, понять, в чем заключается ваша одарённость и смысл.

✔️ Продолжительность: 1 час
✔️Формат: онлайн, аудио
✔️4 консультации ( 1 в неделю)
✔️4 созвон по телефону 10-15 минут (1 раз в неделю)
✔️ возможность переноса 1 встречи 
✔️ материалы для более эффективной работы 

Что получаете:

Через переформирования на самых глубинных уровнях психолог проведёт вас к себе настоящему. Произойдёт  переписывание родительских предписаний, проработка родовых сценарий, изменения убеждения, раскрытия вашего потенциала, выявление и раскрытия ценностей.

*при очной встрече, с вами свяжется специалист и вышлет координаты кабинета и всю нужную информацию.\n\n""",}  # описание карт


haveNotPayedServices = "У вас еще нет оплаченных услуг. Чтобы записаться, вам нужно либо ввести промокод, либо " \
                       "оплатить интересующую вас услугу в главном меню"

chooseAppointmentDate = "Выберите дату"


#  сообщение для вкладки "информация о клиенте"
def client_info(user_id):
    user_ids = gs.read_values(admin_spreadsheet_id, "Клиенты", "COLUMNS", "A1", "A5000")[0]

    if str(user_id) in user_ids:
        user_index = user_ids.index(str(user_id)) + 1
        user_info = gs.read_values(admin_spreadsheet_id, "Клиенты", "ROWS", f"A{user_index}", f"G{user_index}")[0]

        message = f"<b>👤 Мой профиль:</b>\n\n" \
                  f"<b>ID: </b>{user_id}\n" \
                  f"<b>ФИО: </b>{user_info[1]}\n" \
                  f"<b>Телефон:</b> {user_info[2]}\n"
        if len(user_info) > 4:
            if int(user_info[5]) == 1:
                message += f"\n📌 У вас осталось {user_info[5]} посещение по {user_info[4]} карте\n"
            else:
                message += f"\n📌 У вас осталось {user_info[5]} посещения по {user_info[4]} карте\n"
        message += "\n❗️Если ваши контактные данные не совпадают, пожалуйста, обновите их"
        return message
    else:
        return enterYourInfo


def reschedule_message(user_id):
    message = "Выберите номер консультации, которую вы бы хотели перенести: \n"
    notes = gs.read_values(settings.admin_spreadsheet_id, "Запись", "ROWS", "A2", "E20000")
    i = 2
    future_consultations = []
    future_consultations_indexes = []
    try:
        for note in notes:
            if note[3] == str(user_id):
                date = note[0].split(".")
                time = note[1].split(":")

                full_date = datetime(day=int(date[0]), month=int(date[1]), year=int(date[2]), hour=int(time[0]),
                                     minute=int(time[1]))

                if full_date - datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None) > timedelta(days=1):
                    future_consultations.append(note)
                    future_consultations_indexes.append(i)
                i += 1
    except:
        pass
    i = 1
    if len(future_consultations) > 0:
        for consultation in future_consultations:
            message += f"\n{i}. {consultation[0]} | {consultation[1]} - {consultation[4]}"
            i += 1
    else:
        return "У вас нет консультаций, которые можно перенести (перенос возможен не позднее, чем за 24 часа)", [], []
    return message, future_consultations_indexes, future_consultations


def accept_message(date, time, service):
    message = f"✴️ <b>Подтверждение записи:</b>\n\n " \
              f"📆 Дата: {date}\n" \
              f"🕗 Время: {time}\n" \
              f"🔖 Услуга: {service}\n"
    return message


def user_alert(time, service):
    return f"❕ Напоминаем, что сегодня в {time} вы записаны на {service}"


def my_appointments(user_id):
    notes = gs.read_values(settings.admin_spreadsheet_id, "Запись", "ROWS", "A2", "E20000")
    message = "📑 <b>Ваши консультации:</b>\n\n"
    nearest_consultation_time = datetime(year=4000, month=12, day=31) - \
                                datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None)
    nearest_consultation = []
    last_consultations = []
    future_consultations = []
    try:
        for note in notes:
            if note[3] == str(user_id):
                date = note[0].split(".")
                time = note[1].split(":")
                full_date = datetime(day=int(date[0]), month=int(date[1]), year=int(date[2]), hour=int(time[0]),
                                     minute=int(time[1]))
                if full_date < datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None):
                    last_consultations.append(note)
                else:

                    if full_date - datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None) \
                            < nearest_consultation_time:
                        nearest_consultation_time = full_date - \
                                                    datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None)
                        nearest_consultation = note
                    future_consultations.append(note)
    except:
        pass

    if len(future_consultations) > 0:
        message += f"🕗 <b>Ближайшая консультация: </b> {nearest_consultation[0]} | {nearest_consultation[1]} " \
                   f"- {nearest_consultation[4]}\n" \
                   f"\n📆 <b>Будущие консультации:</b>\n"

        for consultation in future_consultations:
            message += f"{consultation[0]} | {consultation[1]} - {consultation[4]} \n"

    if len(last_consultations) > 0:
        message += "\n📒 <b>Прошедшие консультации:</b>\n"
        for consultation in last_consultations:
            message += f"{consultation[0]} | {consultation[1]} - {consultation[4]} \n"

    if len(future_consultations) == 0 and len(last_consultations) == 0:
        message += "🧷 У вас еще нет консультаций"
    return message


fullSchedule = "😔 К сожалению, в этот день время записи недоступно. Выберите, пожалуйста, другой день"

wrongService = "⛔ Введите, пожалуйста, корректный номер услуги"


# сообщение администратору, когда клиент записался на прием
def client_signed(full_name, date, time):
    return f"Новая запись!\nИмя: {full_name} \nВремя: {date} | {time}"


# сообщение администратору, что клиент перенес запись
def client_rescheduled(full_name, last_date, last_time, new_date, new_time):
    return f"Перенос записи!\nИмя: {full_name}\nВремя: {last_date} | {last_time} -> {new_date} | {new_time}"
