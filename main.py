from aiogram import Bot, Dispatcher, executor, types  # библиотека для работы с телеграмом
import logging  # библиотека для логов
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # управление памятью
from aiogram.dispatcher import FSMContext  # машина состояний
from aiogram.dispatcher.filters.state import State, StatesGroup  # машина состояний
from aiogram.types import LabeledPrice
from aiogram.types.message import ContentType

import date as date_file
import keyboards as kb  # файл с клавиатурами
import settings  # файл с настройками
import messages  # файл с сообщениями
import codes_explorer as ce  # файл для создания и использования кодов
import user_data_checker as check  # проверка на правильность введенных данных
import googlesheets_explorer as gs
from telegram_bot_calendar import WMonthTelegramCalendar, LSTEP  # измененная библиотека telegram - календаря
import asyncio  # для регулярно повторяющихся функций

from datetime import datetime
import pytz

# задаём уровень логов
logging.basicConfig(level=logging.INFO)

# инициализация бота и памяти для машины состояний
storage = MemoryStorage()
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


# --------------------------------------КЛАССЫ ДЛЯ МАШИНЫ СОСТОЯНИЙ-----------------------------------------

# режим ввода кода
class EnterCode(StatesGroup):
    code = State()


# режим ввода информации о клиенте
class EnterClientInfo(StatesGroup):
    fullName = State()
    phone_number = State()


# запись на приём или перенос консультации
class Appointment(StatesGroup):
    appointment = State()  # выбор консультации для редактирования
    date = State()
    time = State()
    acceptance = State()


# ввод вопроса
class AskQuestion(StatesGroup):
    question = State()


# оплата услуги
class PayForService(StatesGroup):
    service = State()
    pay_or_back = State()
    pay_for_service = State()
# ------------------------------------------ОБРАБОТЧИКИ КОМАНД----------------------------------------------


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.message, state: FSMContext):
    await bot.send_message(message.from_user.id, messages.descriptionText, parse_mode='HTML')
    await bot.send_message(message.from_user.id, messages.mainMenuText, reply_markup=kb.mainMenu, parse_mode='HTML')
    await state.finish()

# ----------------------------------------ПЕРЕНОС КОНСУЛЬТАЦИИ----------------------------------------------


# выбор консультации
@dp.message_handler(state=Appointment.appointment, content_types=types.ContentTypes.TEXT)
async def choose_appointment(message: types.Message, state: FSMContext):
    try:
        state_data = await state.get_data()

        indexes = state_data['indexes']
        appointment_id = int(message.text) - 1
        index = indexes[appointment_id]  # проверка, достаточная ли длина массива с индексами

        await state.update_data(index=appointment_id)

        max_date = date_file.max_date(settings.appointmentTimeRange)

        calendar, step = WMonthTelegramCalendar(
            current_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
            min_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
            max_date=datetime(day=max_date[0], month=max_date[1], year=max_date[2]).date(), locale='ru').build()
        await bot.send_message(chat_id=message.from_user.id, text=messages.chooseAppointmentDate,
                               parse_mode='HTML', reply_markup=calendar)
        await Appointment.date.set()
    except:
        await bot.send_message(message.from_user.id, "Введите корректный номер консультации")


# ----------------------------------------ЗАПИСЬ НА КОНСУЛЬТАЦИЮ--------------------------------------------

# выбор даты через инлайновый календарь
@dp.callback_query_handler(WMonthTelegramCalendar.func(), state=Appointment.date)
async def enter_appointment_date(call, state: FSMContext):
    max_date = date_file.max_date(settings.appointmentTimeRange)

    result, key, step = WMonthTelegramCalendar(
        current_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
        min_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
        max_date=datetime(day=max_date[0], month=max_date[1], year=max_date[2]).date(), locale='ru').process(call.data)
    a = ""
    if not result and key:
        if LSTEP[step] == "month":
            a = "месяц"
        elif LSTEP[step] == "day":
            a = "день"
        await bot.edit_message_text(f"Выберите {a}",
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=key)
    elif result:
        # здесь дата подгоняется под вид ДАТА.МЕСЯЦ.ГОД (как в таблице)
        required_date = datetime.strptime(str(result), "%Y-%m-%d").date()

        required_date = str(required_date.day).zfill(2) + "." + \
                        str(required_date.month).zfill(2) + "." + str(required_date.year)

        await state.update_data(date=required_date)

        chosen_day_appointments = []  # время записей в этот день
        booked_time = []  # время, в которое нельзя записаться

        appointment_dates = gs.read_values(settings.admin_spreadsheet_id, "Запись", "ROWS", "A2", "B2500")

        # поиск записей в этот день
        for date in appointment_dates:
            try:
                if date[0] == required_date:
                    chosen_day_appointments.append(date[1])
            except:
                pass

        # поиск полностью забронированного времени
        for appointment_time in chosen_day_appointments:
            if chosen_day_appointments.count(appointment_time) >= settings.employees:
                booked_time.append(appointment_time)

        formatted_date = datetime(day=int(required_date[0:2]), month=int(required_date[3:5]),
                                  year=int(required_date[6:10]))
        weekday = formatted_date.isoweekday()

        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G']  # колонки с днями недели

        schedule = gs.read_values(settings.admin_spreadsheet_id, 'Расписание', "COLUMNS", f"{columns[weekday-1]}2",
                                  f"{columns[weekday-1]}100")[0]

        # если пользователь выбрал сегодняшний день, удаляет время, которое уже прошло
        if formatted_date.date() == datetime.today().date():
            for time in schedule:
                time_array = time.split(":")
                formatted_time = datetime(day=1, month=1, year=1999,
                                          hour=int(time_array[0]), minute=int(time_array[1])).time()
                if formatted_time < datetime.today().time():
                    booked_time.append(time)

        booked_time = list(set(booked_time))
        # создание актуального свободного расписания на выбранный день
        for element in booked_time:
            try:
                schedule.remove(element)
            except:
                pass

        if len(schedule) > 0:
            await bot.send_message(call.message.chat.id, "Выберите время",
                                   reply_markup=kb.adaptive_time_keyboard(schedule), parse_mode='HTML')
            await Appointment.time.set()
        else:
            max_date = date_file.max_date(settings.appointmentTimeRange)

            calendar, step = WMonthTelegramCalendar(
                current_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
                min_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
                max_date=datetime(day=max_date[0], month=max_date[1], year=max_date[2]).date(), locale='ru').build()

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.fullSchedule, parse_mode='HTML',
                                        reply_markup=calendar)


# выбор времени через инлайновую клавиатуру
@dp.callback_query_handler(lambda call: True, state=Appointment.time)
async def enter_appointment_time(call, state: FSMContext):
    await state.update_data(time=call.data)
    state_data = await state.get_data()
    if state_data['type'] == "new":
        await bot.send_message(call.message.chat.id,
                               messages.accept_message(state_data['date'], state_data['time'],
                                                       state_data['service']),
                               reply_markup=kb.acceptanceMenu, parse_mode='HTML')
    else:
        appointments = state_data['appointments']
        id = int(state_data['index'])
        await bot.send_message(call.message.chat.id,
                               messages.accept_message(state_data['date'], state_data['time'],
                                                       appointments[id][4]),
                               reply_markup=kb.acceptanceMenu, parse_mode='HTML')
    await Appointment.acceptance.set()


# подтверждение записи или переноса
@dp.callback_query_handler(lambda call: True, state=Appointment.acceptance)
async def accept_appointment(call, state: FSMContext):
    if call.data == "refill":
        max_date = date_file.max_date(settings.appointmentTimeRange)

        calendar, step = WMonthTelegramCalendar(
            current_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
            min_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
            max_date=datetime(day=max_date[0], month=max_date[1], year=max_date[2]).date(), locale='ru').build()

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.chooseAppointmentDate, parse_mode='HTML',
                                    reply_markup=calendar)
        await Appointment.date.set()
    if call.data == "accept":
        state_data = await state.get_data()

        user_ids = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "COLUMNS", "A1", "A10000")[0]
        user_index = user_ids.index(str(call.message.chat.id)) + 1
        client_info = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "ROWS", f"A{user_index}",
                                     f"G{user_index}")[0]

        if state_data['type'] == "new":
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.signedUpOnConsultation)

            notes = gs.read_values(settings.admin_spreadsheet_id, "Запись", "COLUMNS", "A2", "A10000")[0]
            index = len(notes) + 2

            note = [state_data['date'], state_data['time'], "", str(call.message.chat.id), state_data['service'], "нет"]
            gs.write_values(settings.admin_spreadsheet_id, 'Запись', "ROWS", f"A{index}", f"F{index}", [note])
            await state.finish()

            visits = int(client_info[5]) - 1

            await bot.send_message(settings.admin_id, messages.client_signed(client_info[1], note[0], note[1]))

            premium_promos = ['SILVER Premium', 'GOLD Premium']

            if visits == 0 and state_data['service'] not in premium_promos:
                gs.write_values(settings.admin_spreadsheet_id,
                                "Клиенты", "ROWS", f"E{user_index}", f"F{user_index}", [["", ""]])
            elif state_data['service'] in premium_promos:  # обновление времени крайней записи по premium промокоду
                try:
                    if datetime.strptime(client_info[6], "%d.%m.%Y") < datetime.strptime(state_data['date'],
                                                                                         "%d.%m.%Y"):

                        gs.write_values(settings.admin_spreadsheet_id, "Клиенты", "ROWS", f"F{user_index}",
                                        f"G{user_index}", [[visits, state_data['date']]])
                    else:
                        gs.write_values(settings.admin_spreadsheet_id,
                                        "Клиенты", "ROWS", f"F{user_index}", f"F{user_index}", [[visits]])

                except:  # на случай, если это первая запись по промокоду
                    gs.write_values(settings.admin_spreadsheet_id, "Клиенты", "ROWS", f"F{user_index}",
                                    f"G{user_index}", [[visits, state_data['date']]])
            else:
                gs.write_values(settings.admin_spreadsheet_id,
                                "Клиенты", "ROWS", f"F{user_index}", f"F{user_index}", [[visits]])

            await bot.send_message(call.message.chat.id, messages.mainMenuText, reply_markup=kb.mainMenu,
                                   parse_mode='HTML')

        else:
            appointments = state_data['appointments']
            id = int(state_data['index'])
            index = state_data['indexes'][id]
            appointment = appointments[id]

            await bot.send_message(settings.admin_id,
                                   messages.client_rescheduled(client_info[1],
                                                               appointment[0],
                                                               appointment[1],
                                                               state_data['date'],
                                                               state_data['time']))

            appointment[0] = state_data['date']
            appointment[1] = state_data['time']
            gs.write_values(settings.admin_spreadsheet_id, "Запись", "ROWS", f"A{index}", f"F{index}", [appointment])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.scheduleUpdated, parse_mode='HTML')

            await bot.send_message(call.message.chat.id, messages.mainMenuText, reply_markup=kb.mainMenu,
                                   parse_mode='HTML')
            await state.finish()


# ----------------------------------------------ОПЛАТА УСЛУГИ-----------------------------------------------

# выбор услуги для просмотра информации
@dp.callback_query_handler(lambda call: True, state=PayForService.service)
async def choose_service(call, state: FSMContext):
    if call.data != "backToMainMenu":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.card_description[call.data], parse_mode='HTML',
                                    reply_markup=kb.aboutServiceMenu)
        await state.update_data(service=call.data)
        await PayForService.pay_or_back.set()
    else:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.mainMenuText, reply_markup=kb.mainMenu, parse_mode='HTML')
        await state.finish()


# оплатить или выбрать другую услугу
@dp.callback_query_handler(lambda call: True, state=PayForService.pay_or_back)
async def pay_or_not(call, state: FSMContext):
    if call.data == "pay":
        rows = {'BLACK': 2, 'SILVER': 3, 'GOLD': 4, 'SILVER Premium': 5, 'GOLD Premium': 6}
        price = 10000

        state_data = await state.get_data()

        try:
            price = int(gs.read_values(settings.admin_spreadsheet_id, "Услуги", "ROWS",
                                       f"C{rows[state_data['service']]}", f"C{rows[state_data['service']]}")[0][0])
        except:
            pass

        await bot.send_invoice(chat_id=call.message.chat.id,
                               title=f"Оплата услуги {state_data['service']}",
                               description="\n\n🔄 Услуга появится во вкладке \"Мой профиль\" сразу после оплаты",
                               payload=call.message.chat.id,  # чтобы быть точно уверенным, что это нужная транзакция
                               provider_token=settings.PAYMENTS_TOKEN,
                               currency="RUB",
                               prices=[LabeledPrice("Руб", int(float(price) * 100))])
        await PayForService.pay_for_service.set()
    if call.data == "backToServicesMenu":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.chooseService, reply_markup=kb.choose_service())
        await PayForService.service.set()


# подтверждение для оплаты
@dp.pre_checkout_query_handler(state=PayForService.pay_for_service)
async def process_pre_checkout_query(pre_checkout_query: types.pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# зачисление услуги
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=PayForService.pay_for_service)
async def sign_up(message: types.Message, state: FSMContext):
    if str(message.successful_payment.invoice_payload) == str(message.from_user.id):
        state_data = await state.get_data()

        answer = ce.activate_service(message.from_user.id, "", state_data['service'])

        await bot.send_photo(chat_id=message.chat.id, photo=open(f"cards/{answer[1]}.jpg", "rb"))
        await bot.send_message(message.from_user.id, answer[0], parse_mode='HTML')

        await bot.send_message(message.from_user.id, messages.mainMenuText, reply_markup=kb.mainMenu, parse_mode='HTML')
        await state.finish()

# ---------------------------------------------ВВОД КОДА----------------------------------------------------


@dp.message_handler(state=EnterCode.code, content_types=types.ContentTypes.TEXT)
async def enter_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    state_data = await state.get_data()

    answer = ce.activate_service(str(message.from_user.id), str(state_data['code']), "")

    await bot.send_photo(chat_id=message.chat.id, photo=open(f"cards/{answer[1]}.jpg", "rb"))
    await bot.send_message(message.from_user.id, answer[0], parse_mode='HTML')

    await bot.send_message(message.from_user.id, messages.mainMenuText, reply_markup=kb.mainMenu, parse_mode='HTML')
    await state.finish()


# -------------------------------------ВВОД ИНФОРМАЦИИ О КЛИЕНТЕ--------------------------------------------

# ввод ФИО
@dp.message_handler(state=EnterClientInfo.fullName, content_types=types.ContentTypes.TEXT)
async def enter_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)

    await bot.send_message(message.from_user.id, messages.enterPhoneNumber)
    await EnterClientInfo.phone_number.set()


# ввод номера телефона
@dp.message_handler(state=EnterClientInfo.phone_number, content_types=types.ContentTypes.TEXT)
async def enter_phone_number(message: types.Message, state: FSMContext):
    if check.is_phone_number(message.text):
        await state.update_data(phone_number=message.text)
        user = await bot.get_chat(message.from_user.id)

        telegram_tag = "-"
        try:
            telegram_tag = "@" + user['username']
        except:
            pass

        state_data = await state.get_data()
        client_info = [[str(message.from_user.id), state_data['full_name'],
                        state_data['phone_number'], telegram_tag]]

        user_ids = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "COLUMNS", "A1", "A10000")[0]

        user_index = 0
        if str(message.from_user.id) in user_ids:
            user_index = user_ids.index(str(message.from_user.id)) + 1
        else:
            user_index = len(user_ids) + 1

        gs.write_values(settings.admin_spreadsheet_id, "Клиенты", "ROWS", f"A{user_index}", f"D{user_index}",
                        client_info)

        await bot.send_message(message.from_user.id, messages.infoUpdated)
        await bot.send_message(chat_id=message.from_user.id, text=messages.client_info(message.from_user.id),
                               reply_markup=kb.clientInfoMenu, parse_mode='HTML')
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, messages.reenter)


# ------------------------------------------ЗАДАТЬ ВОПРОС---------------------------------------------------

# ввод вопроса пользователя
@dp.message_handler(state=AskQuestion.question, content_types=types.ContentTypes.TEXT)
async def ask_question(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, messages.questionPassed)

    await bot.send_message(message.from_user.id, messages.mainMenuText, reply_markup=kb.mainMenu, parse_mode='HTML')
    await state.finish()

    await bot.send_message(settings.admin_id, f"❓ Вопрос от {message.from_user.id}: {message.text}")

# -----------------------------------ОБРАБОТЧИКИ КНОПОК БЕЗ СОСТОЯНИЯ---------------------------------------


@dp.callback_query_handler(lambda call: True, state="*")
async def callback_inline(call, state: FSMContext):
    # кнопка "записаться" в главном меню
    if call.data == "appointment":
        users = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "COLUMNS", "A2", "A10000")[0]
        if str(call.message.chat.id) in users:  # если человек есть в базе
            service = ce.has_service(call.message.chat.id)
            if service != "":  # если у человека есть оплаченная услуга
                max_date = date_file.max_date(settings.appointmentTimeRange)

                calendar, step = WMonthTelegramCalendar(
                    current_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
                    min_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).today().date(),
                    max_date=datetime(day=max_date[0], month=max_date[1], year=max_date[2]).date(), locale='ru').build()

                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=messages.chooseAppointmentDate, parse_mode='HTML',
                                            reply_markup=calendar)
                await Appointment.date.set()
                await state.update_data(service=service)
                await state.update_data(type="new")
            else:  # если оплаченных услуг нет
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=messages.haveNotPayedServices, reply_markup=kb.standardMenu,
                                            parse_mode='HTML')
        else:  # если человека нет в базе
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.enterYourInfo)
            await bot.send_message(chat_id=call.message.chat.id, text=messages.enterFullName)
            await EnterClientInfo.fullName.set()
    # кнопка "о нас" в главном меню
    if call.data == "aboutUs":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.aboutUsText, parse_mode='HTML',
                                    reply_markup=kb.standardMenu)
    # кнопка "ввести код" в главном меню
    if call.data == "serviceCode":
        users = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "COLUMNS", "A2", "A10000")[0]
        if str(call.message.chat.id) in users:
            service = ce.has_service(call.message.chat.id)
            if service != "":
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=messages.useYorServicesBeforeActivate, reply_markup=kb.standardMenu)
            else:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=messages.enterCodeText, reply_markup=kb.standardMenu)
                await EnterCode.code.set()
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.enterYourInfo)
            await bot.send_message(chat_id=call.message.chat.id, text=messages.enterFullName)
            await EnterClientInfo.fullName.set()
    # кнопка "оплатить услугу"
    if call.data == "payForService":
        users = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "COLUMNS", "A2", "A10000")[0]
        if str(call.message.chat.id) in users:
            service = ce.has_service(call.message.chat.id)
            if service != "":
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=messages.useYorServicesBeforePay, reply_markup=kb.standardMenu)
            else:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=messages.chooseService, reply_markup=kb.choose_service())
                await PayForService.service.set()
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.enterYourInfo)
            await bot.send_message(chat_id=call.message.chat.id, text=messages.enterFullName)
            await EnterClientInfo.fullName.set()
    # кнопка "информация о клиенте" в главном меню
    if call.data == "clientInfo":
        info = messages.client_info(call.message.chat.id)
        #  если клиента нет в базе
        if info == messages.enterYourInfo:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=info, parse_mode='HTML')
            await bot.send_message(chat_id=call.message.chat.id, text=messages.enterFullName)
            await EnterClientInfo.fullName.set()
        #  если он есть в базе
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=info, reply_markup=kb.clientInfoMenu, parse_mode='HTML')
            await state.finish()
    # кнопка для обновления информации о клиенте
    if call.data == "fillClientInfo":
        await bot.send_message(chat_id=call.message.chat.id, text=messages.enterFullName)
        await EnterClientInfo.fullName.set()
    # кнопка "мои консультации"
    if call.data == "myAppointments":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.my_appointments(call.message.chat.id),
                                    reply_markup=kb.myConsultationsMenu, parse_mode='HTML')
        await state.finish()
    # кнопка "перенести консультацию"
    if call.data == "reschedule":
        answer = messages.reschedule_message(call.message.chat.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.reschedule_message(call.message.chat.id)[0],
                                    reply_markup=kb.rescheduleMenu, parse_mode='HTML')
        await Appointment.appointment.set()

        await state.update_data(type="reschedule")
        await state.update_data(indexes=answer[1])
        await state.update_data(appointments=answer[2])
    # стандартная кнопка возврата в главное меню с учетом админ панели
    if call.data == "backToMainMenu":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.mainMenuText, parse_mode='HTML',
                                    reply_markup=kb.mainMenu)
        await state.finish()
    if call.data == "askQuestion":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.askQuestionText, parse_mode='HTML',
                                    reply_markup=kb.standardMenu)
        await AskQuestion.question.set()


# -----------------------------------------ПОВТОРЯЮЩИЕСЯ ФУНКЦИИ--------------------------------------------

# обновление и сортировка таблицы записей на сегодня для сотрудников, оповещение пользователей
async def usual_function(delay):
    while True:
        await asyncio.sleep(delay)
        try:
            notes = gs.read_values(settings.admin_spreadsheet_id, "Запись", "ROWS", "A2", "F10000")
            users = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "ROWS", "A2", "D10000")
            today_notes = []
            id = 1
            for note in notes:
                id += 1
                date = note[0].split(".")
                time = note[1].split(":")
                full_date = datetime(day=int(date[0]), month=int(date[1]), year=int(date[2]),
                                     hour=int(time[0]), minute=int(time[1]))
                if full_date.date() == datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None).date():
                    full_name = ""
                    phone_number = ""
                    telegram_tag = ""

                    for user in users:
                        if user[0] == str(note[3]):
                            full_name = user[1]
                            phone_number = user[2]
                            telegram_tag = user[3]
                    # для оповещения пользователей
                    if (full_date - datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None)).seconds <= \
                            settings.alert_time * 60 and note[5] == "нет":
                        temp_note = note
                        temp_note[5] = "да"
                        await bot.send_message(chat_id=int(note[3]), text=messages.user_alert(note[1], note[4]))
                        gs.write_values(settings.admin_spreadsheet_id, "Запись", "ROWS", f"A{id}", f"F{id}",
                                        [temp_note])

                    for_eployees_note = [note[1], note[4], note[2], full_name, phone_number, telegram_tag]
                    today_notes.append(for_eployees_note)

            today_notes = sorted(today_notes, key=lambda _note: datetime.strptime(_note[0], '%H:%M'))
            # для того, чтобы не оставались записи прошлых дней
            for i in range(0, 30):
                today_notes.append(["", "", "", "", "", ""])
            gs.write_values(settings.employees_spreadsheet_id, "Расписание", "ROWS", "A2", "F5000", today_notes)
        except:
            pass


# убирает premium статус, если дата крайней консультации меньше текущей
async def update_card_status(delay):
    while True:
        await asyncio.sleep(delay)
        premium_statuses = gs.read_values(settings.admin_spreadsheet_id, "Клиенты", "ROWS", "F2", "G10000")

        for premium_status in premium_statuses:
            try:
                if datetime.strptime(premium_status[1], "%d.%m.%Y").date() < datetime.now().date() and \
                        premium_status[0] == "0":
                    premium_status[0] = ""
                    premium_status[1] = ""
            except:
                pass
        gs.write_values(settings.admin_spreadsheet_id, "Клиенты", "ROWS", "F2", "G10000", premium_statuses)


# ------------------------------------------ЛОНГ ПОЛЛИНГ----------------------------------------------------

# запуск лонг поллинга
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(usual_function(settings.refresh_eployees_table_time))
    loop.create_task(update_card_status(settings.refresh_premium_status_time))
    executor.start_polling(dp, skip_updates=True)


