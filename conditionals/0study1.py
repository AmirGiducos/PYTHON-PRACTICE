score = int(input("Score: "))


if score >= 90 and score <= 100:
    print(f"Your {score} gave you a grade of A, Congratulations!")
elif score >= 80 and score < 90:
    print(f"Your {score} gave you a grade of B, Congratulations!")
elif score >= 70 and score < 80:
    print(f"Your {score} gave you a grade of C, Congratulations!")
elif score >= 60 and score < 70:
    print(f"Your {score} gave you a grade of D, Congratulations!")
else:
    print(f"Due to a score of {score}, you failed.")
