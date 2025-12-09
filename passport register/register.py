def main():
    print(f"Hello welcome to Philippine Airlines!")
    print(f"Would you like to register? (Y/N)")
    print(f"Press Y if you would like to register.")
    print(f"Press N if you already have an account.")
    key0 = input(": ")
    answer0(key0)
    
def answer0(choices):
    choices = choices.lower().strip()

    if (choices == "y"):
        print("Welcome to Philippines Airline Registration: ")
    elif (choices == "n"):
        print("Welcome to Philippine Airlines! Login now.")
    else:
        print("Please input a valid key. (Y/N)")

def register(key):
    a = a

main()