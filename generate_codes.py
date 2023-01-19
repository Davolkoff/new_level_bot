import sys

import settings
from settings import admin_spreadsheet_id
import random
import googlesheets_explorer as gs


# поиск крайнего индекса
def last_index(arr, element):
    element_found = True

    last_occurrence = -1

    while element_found:
        try:
            last_occurrence = arr.index(element, last_occurrence + 1)
        except ValueError:
            element_found = False
    return last_occurrence


# бесшовное добавление массива
def insert_array(array1, array2, index):
    return array1[0:index] + array2 + array1[index:len(array1)]


# генератор кодов
def generate_codes(complexity, black, silver, gold, silver_premium, gold_premium):
    table = gs.read_values(settings.admin_spreadsheet_id, "Коды", "COLUMNS", "A1", "C20000")

    existing_codes_ids = table[0]
    existing_codes = table[1]
    existing_codes_names = table[2]

    total_number = black + silver + gold + silver_premium + gold_premium
    # новые коды не должны повторять старые
    total_array_of_codes = range(pow(10, complexity - 1), int("9" * complexity))

    array_of_unused_codes = list(set(total_array_of_codes) - set(existing_codes))

    unused_codes = random.sample(array_of_unused_codes, total_number)  # сгенерированные коды

    types_of_codes = ['BLACK', 'SILVER', 'GOLD', 'SILVER Premium', 'GOLD Premium']  # виды кодов
    number = [black, silver, gold, silver_premium, gold_premium]

    start_index = 0
    # добавление новых промокодов
    for i in range(len(types_of_codes)):
        li = last_index(existing_codes_names, types_of_codes[i])

        if li == -1:  # если кодов для такой карты не существует
            li = len(existing_codes_names)


        try:
            last_id = int(existing_codes_ids[li])
        except:
            last_id = 0

        codes = unused_codes[start_index:start_index+number[i]]  # коды конкретно под определенный тип карты
        start_index = start_index + number[i]

        existing_codes_ids = insert_array(existing_codes_ids, list(range(last_id + 1, last_id + 1 + number[i])),
                                            li+1)
        existing_codes = insert_array(existing_codes, codes, li+1)
        existing_codes_names = insert_array(existing_codes_names, [types_of_codes[i]] * number[i], li+1)

    gs.write_values(admin_spreadsheet_id, "Коды", "COLUMNS", "A1", f"C{len(existing_codes)}",
                    [existing_codes_ids, existing_codes, existing_codes_names])


c = int(input("Введите количество символов: "))
b = int(input("Введите количество BLACK кодов: "))
s = int(input("Введите количество SILVER кодов: "))
g = int(input("Введите количество GOLD кодов: "))
v_s = int(input("Введите количество SILVER Premium кодов: "))
v_g = int(input("Введите количество GOLD Premium кодов: "))

generate_codes(c, b, s, g, v_s, v_g)
print("Промокоды успешно сгенерированы")
