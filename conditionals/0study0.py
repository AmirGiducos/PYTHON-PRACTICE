'''

> is greater than
< is less than
>= greater than or equal 
<= less than or equal
!= not equal
== equal

'''
x = int(input("What's the value of x? "))
y = int(input("What's the value of y? "))

if (x != y):
    print(f"{x} is not equal to {y}")
else:
    print(f"{x} is equal to {y}")