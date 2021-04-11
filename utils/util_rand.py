import random

black_list = {ord('A'), ord('E'), ord('I'), ord('O'), ord('U'), ord('0'), ord('3')}

def get_code(i):
    code = ""
    while len(code) < i:
        rand = random.randint(48, 122)
        while not is_valid_character(rand):
            rand = random.randint(48, 122)
        code = chr(rand) + code
    return code


def is_valid_character(num):
    if (num >= 58 and num < 65) or (num >= 91) or num in black_list:
        return False
    else:
        return True


def get_letter():                                    
    rand = random.randint(65,90)
    letter = chr(rand)
    return letter


def get_numbers(amount, length):
    l = set()
    while len(l) < amount:
        l.add(random.randint(0, length - 1))
    return l