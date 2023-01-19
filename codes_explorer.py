import googlesheets_explorer as gs
import settings
from settings import admin_spreadsheet_id
import messages


# активировать услугу
def activate_service(user_id, code, card):  # код для активации по коду, service - для присвоения услуги при оплате
    if card == "":
        codes_table = gs.read_values(admin_spreadsheet_id, "Коды", "COLUMNS", "A1", "C20000")

        ids = codes_table[0]
        codes = codes_table[1]
        names = codes_table[2]
        if code in codes:

            promo_index = codes.index(code)
            card = names[promo_index]  # карта, которая активируется после ввода промокода

            clients_table = gs.read_values(admin_spreadsheet_id, "Клиенты", "COLUMNS", "A1", "A20000")[0]

            # поиск индекса строки с нужным клиентом (+1 из-за нумерации массива)
            client_index = clients_table.index(user_id) + 1

            rows = {"BLACK": 2, "SILVER": 3, "GOLD": 4, "SILVER Premium": 5, "GOLD Premium": 6}
            visits = int(gs.read_values(settings.admin_spreadsheet_id,
                                        "Услуги", "ROWS", f"B{rows[card]}", f"B{rows[card]}")[0][0])
            gs.write_values(admin_spreadsheet_id, "Клиенты", "COLUMNS", f"E{client_index}", f"F{client_index}",
                            [[card], [visits]])


            del ids[promo_index]
            del codes[promo_index]
            del names[promo_index]
            ids.append('')
            codes.append('')
            names.append('')

            gs.write_values(admin_spreadsheet_id, "Коды", "COLUMNS", "A1", f"C{len(codes)}", [ids, codes, names])

            return f"✅ Карта {card} успешно активирована!\n\n" \
                   f"{messages.card_description[card]}\n" \
                   f"Для записи на консультацию нажмите на кнопку \"✅Записаться\" в главном меню", card
        else:
            return "⛔️ Такого кода в нашей базе нет, попробуйте ввести ещё раз", card
    else:
        clients_table = gs.read_values(admin_spreadsheet_id, "Клиенты", "COLUMNS", "A1", "A20000")[0]

        # поиск индекса строки с нужным клиентом (+1 из-за нумерации массива)
        client_index = clients_table.index(str(user_id)) + 1

        rows = {"BLACK": 2, "SILVER": 3, "GOLD": 4, "SILVER Premium": 5, "GOLD Premium": 6}
        visits = int(gs.read_values(settings.admin_spreadsheet_id,
                                    "Услуги", "ROWS", f"B{rows[card]}", f"B{rows[card]}")[0][0])
        gs.write_values(admin_spreadsheet_id, "Клиенты", "COLUMNS", f"E{client_index}", f"F{client_index}",
                        [[card], [visits]])
        return f"✅ Карта {card} успешно активирована!\n\n" \
               f"{messages.card_description[card]}", card


def has_service(user_id):
    clients_table = gs.read_values(admin_spreadsheet_id, "Клиенты", "COLUMNS", "A1", "A20000")[0]

    try:
        user_index = clients_table.index(str(user_id)) + 1
    except:
        return ""

    promos_table = gs.read_values(admin_spreadsheet_id, "Клиенты", "ROWS", f"E{user_index}", f"F{user_index}")[0]

    try:
        if not promos_table[0] == '' and not promos_table[1] == '0':
            return promos_table[0]
        else:
            return ""
    except:
        return ""
