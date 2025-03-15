def main():
    print("Hello from class4-15-03-25!")


if __name__ == "__main__":
    main()



count = 1

while count <= 3:
    print("Kacha Papar vs Pakka Papar")
    count += 1

print("Done")

iftar_items: list = ["Mango", "Banana", "Apple", "Orange", "Pineapple"]

for items in iftar_items:
    print(items)


# Dictionary, list, tuple, set

def items(*n):
    sum = 0
    for item in n:
        sum += item
    print(sum)

items(1, 2, 3, 4, 5)


