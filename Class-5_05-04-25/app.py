import cal

def main():
    response = cal.add(2,3)
    assert response == 5, "Expected 2 + 3 = 5"
    return response


if __name__ == "__main__":
    result = main()
    print(f"Result: {result}")


# # we use return to terminate the state
# my.py
# py.test
# to use test cases we wrtie assert
# pipi pip index python 