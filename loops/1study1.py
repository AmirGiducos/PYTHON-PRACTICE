def main():
    number = numberCounter()
    doTask(number)

    
def numberCounter():
    while True:
        try:
            n = int(input("Enter amount of times you want to do task (Enter positive number): "))
            if n > 0:
                return n
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def doTask(n):
    for i in range(n):
        print("Task finished...")


main()
