def main():
    even = [2, 4, 6, 8, 10]
    odd = [1,3,5,7,9,11]
    prime = [2,3,5,7]
    evenchecker(even)
    evenchecker(odd)
    evenchecker(prime)

def evenchecker(even):
    for i in even:
        if i % 2 == 0:
            print(f"{i} is an even number")
        elif i % 2 == 1:
            print(f"{i} is an odd number")
        else:
            print(f"{i} is a prime number")


main()
