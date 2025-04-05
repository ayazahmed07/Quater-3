import cal

def test_main():
    response1 = cal.add(2,3)
    assert response1 == 5, "Expected 2 + 3 = 5"
    response2 = cal.add(0,0)
    assert response2 == 0, "Expected 0 + 0 = 0"
    response3 = cal.add(-2,-2)
    assert response3 == -4, "Expected -2 + -2 = -4"
    response4 = cal.add(1,4)
    assert response4 == 5, "Expected 2 + 3 = 5"
    

if __name__ == "__main__":
    result = test_main()
    print(f"Result: {result}")


# # we use return to terminate the state
# my.py
# py.test