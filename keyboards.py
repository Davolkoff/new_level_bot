from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import googlesheets_explorer as gs

# стандартная клавиатура для возврата в главное меню
import settings

backToMainMenu = InlineKeyboardButton('⬅️ Вернуться в главное меню', callback_data='backToMainMenu')
standardMenu = InlineKeyboardMarkup().add(backToMainMenu)

# клавиатура главного меню
appointment = InlineKeyboardButton('✅ Записаться', callback_data='appointment')
serviceCode = InlineKeyboardButton('✏️ Ввести код', callback_data='serviceCode')
payForService = InlineKeyboardButton('💳 Оплата услуг', callback_data='payForService')
clientInfo = InlineKeyboardButton('👤 Мой профиль', callback_data='clientInfo')
askQuestion = InlineKeyboardButton('❓ Задать вопрос', callback_data='askQuestion')
aboutUs = InlineKeyboardButton('🎩 О нас', callback_data='aboutUs')
mainMenu = InlineKeyboardMarkup(row_width=2).add(appointment).add(serviceCode, payForService).\
    add(clientInfo, askQuestion).add(aboutUs)


# клавиатура для вкладки "информация о клиенте", если клиент есть в базе
fillClientInfo = InlineKeyboardButton('📝 Обновить личную информацию', callback_data='fillClientInfo')
myAppointments = InlineKeyboardButton('📒 Мои консультации', callback_data='myAppointments')
clientInfoMenu = InlineKeyboardMarkup(row_width=1).add(fillClientInfo, myAppointments, backToMainMenu)


# клавиатура в меню "мои консультации"
reschedule = InlineKeyboardButton('🗓 Перенести консультацию', callback_data='reschedule')
backToCLientInfo = InlineKeyboardButton('⬅️ Вернуться к моему профилю', callback_data='clientInfo')
myConsultationsMenu = InlineKeyboardMarkup(row_width=1).add(reschedule, backToCLientInfo, backToMainMenu)

# клавиатура в переносе консультации
rescheduleMenu = InlineKeyboardMarkup(row_width=1).add(backToCLientInfo, backToMainMenu)


# клавиатура для выбора времени приёма
def adaptive_time_keyboard(schedule):
    time_keyboard = InlineKeyboardMarkup(row_width=1)

    for note in schedule:
        time_button = InlineKeyboardButton(note, callback_data=str(note))
        time_keyboard.add(time_button)
    return time_keyboard


# клавиатура подтверждения записи
refill = InlineKeyboardButton('🔄 Заполнить заново', callback_data='refill')
accept = InlineKeyboardButton('✅ Подтвердить', callback_data='accept')
acceptanceMenu = InlineKeyboardMarkup(row_width=1).add(refill, accept)


# клавиатура выбора услуги
def choose_service():
    keyboard = InlineKeyboardMarkup(row_width=1)
    services = gs.read_values(settings.admin_spreadsheet_id, "Услуги", "ROWS", "A2", "C6")
    for service in services:
        keyboard.add(InlineKeyboardButton(f'{service[0]} - {service[2]} Руб', callback_data=service[0]))
    return keyboard.add(backToMainMenu)


# клавиатура просмотра информации об услуге
pay = InlineKeyboardButton('💳 Оплатить', callback_data='pay')
backToServices = InlineKeyboardButton('⬅️ Вернуться к выбору услуги', callback_data='backToServicesMenu')
aboutServiceMenu = InlineKeyboardMarkup(row_width=1).add(pay, backToServices)