import requests

def main():
    response = requests.get("https://www.google.com")
    return response.status_code


if __name__ == "__main__":
    print(main())


# python just in time complier mypy
# pytest