from decimal import Decimal, getcontext

# Set the desired precision (number of significant digits)
getcontext().prec = 30  # Adjust as needed

base = [Decimal(1), Decimal(2), Decimal(5)]
available_timebases = [
    item * (Decimal(10) ** Decimal(i))
    for i in range(-9, 3)
    for item in ( [base[0]] if i == 2 else base )
]

if __name__ == "__main__":
    for tb in available_timebases:
        print(tb)