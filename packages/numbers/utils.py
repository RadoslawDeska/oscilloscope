import numpy as np

PREFIXES = {-15: "f", -12: "p", -9: "n", -6: "u", -3: "m"}

def get_multiplier_letter(value):
    if value == 0:
        return 0, 0, ""
    
    sign = np.sign(value)
    value = abs(value)
    
    exponent = int(np.floor(np.log10(float(value))))
    
    if exponent < 0:
        base = float(value) / (10 ** exponent)
        
        if -12 > exponent:  # for anything smaller than 1 pico it becomes femto
            base *= 10 ** (15 + exponent)  # value = 1.2345e-14 produces 12.345f
            letter = PREFIXES[-15]
        elif -9 > exponent >= -12:
            base *= 10 ** (12 + exponent)  # value = 1.2345e-11 produces 12.345p
            letter = PREFIXES[-12]
        elif -6 > exponent >= -9:
            base *= 10 ** (9 + exponent)  # value = 1.2345e-8 produces 12.345n
            letter = PREFIXES[-9]
        elif -3 > exponent >= -6:
            base *= 10 ** (6 + exponent)  # value = 1.2345e-5 produces 12.345u
            letter = PREFIXES[-6]
        else:  # anything between zero and 1 milli
            base *= 10 ** (3 + exponent)  # value = 1.2345e-2 produces 12.345m
            letter = PREFIXES[-3]
    
    else:  # anything bigger than zero
        base = float(value)
        letter = ""
        
    return sign*base, exponent, letter

def get_exponent_from_letter(letter_value):
    return next((exponent for exponent, letter in PREFIXES.items() if letter == letter_value), None)

def get_letter_from_exponent(exponent_value):
    return next((letter for exponent, letter in PREFIXES.items() if exponent == exponent_value), None)