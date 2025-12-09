x = 1

while x <= 10:
    print(x)
    x += 1

count = 1

while count <= 5:
    print("Hello")
    count += 1

evenNumbers = 0

while evenNumbers <= 20:
    print(evenNumbers)
    evenNumbers += 2

password = input("Enter password: ")

while password.lower() != ("secret"):
    print("Wrong!")
    password = input("Enter password: ")

if password.lower() == ("secret"):
    print("Access granted!")

    
    