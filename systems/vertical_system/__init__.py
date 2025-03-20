from decimal import Decimal, getcontext

# Set the desired precision (number of significant digits)
getcontext().prec = 30  # Adjust as needed

base = [Decimal(1), Decimal(2), Decimal(5)]
available_scales = [
    factor * (Decimal(10) ** e)
    for e in range(-4, 2)
    for factor in base
]

available_scales = available_scales[2:-2]
if __name__ == "__main__":
    print(len(available_scales))
    for scale in available_scales:
        print(scale)