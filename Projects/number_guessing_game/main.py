import random

print("Welcome to the Number Guessing Game!! \n You got 5 attempts to guess the number between 1 and 30, lets start the game")

random_number = random.randrange(1, 30)

chances: int = 5

guess_counter: int = 0;

while guess_counter < chances:
    guess_counter += 1
    my_guess = int(input("Enter your guess number: "))

    if my_guess == random_number:
        print(f"(You guess the correct number!! {random_number} in the {guess_counter} attempt)")
        break
    elif guess_counter >= and chances   





