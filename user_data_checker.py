def is_full_name(full_name):
    if full_name.count(" ") == 2:
        name = full_name.split(" ")
        for word in name:
            for i in word:
                if not i.isalpha():
                    return False
        return True
    else:
        return False


def is_phone_number(number):
    if number[0] != "+" and not number[0].isdigit():
        return False

    if len(number) > 14 or len(number) < 10:
        return False

    for i in str(number[1:]):
        if not i.isdigit():
            return False
    return True
