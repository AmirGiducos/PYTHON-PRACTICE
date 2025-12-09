def main():
    x = int(input("What's the value of x?: "))
    even(x)


def even(x=2):
    if x % 2 == 0:
        print(f"{x} is an Even number.")
    else:
        print(f"{x} is an Odd number.")

even()
main()
