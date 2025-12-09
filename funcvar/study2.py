# Def lesson
def main():
    name = input("What's your name? ").title().strip()
    greetUser(name)

def greetUser(name="world"):
    print(f"How are you doing, {name}?")

greetUser()
main()
main()

