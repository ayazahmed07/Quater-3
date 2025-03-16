import random

print(f"Welcome to the Number Guessing Game!!")

chances: int = int(input("Enter your number of attempts: "))

print(f"You got {chances} attempts to guess the number between 1 to 20")

random_number = random.randrange(1, 10)

guess_counter: int = 0;

while guess_counter < chances:
    guess_counter += 1
    my_guess = int(input("Enter your guess number: "))

    if my_guess == random_number:
        print(f"(You guess the correct number!! Your number is {random_number} and you guess in {guess_counter} attempt!!)")
        break
    elif guess_counter >= chances and my_guess != random_number:
        print(f"You failed to guess the number, the correct number is {random_number} better luck next time!!")

    elif my_guess < random_number:
        print("Your guess is too low try again!!")

    elif my_guess > random_number:
        print("Your guess is too high try again!!")








