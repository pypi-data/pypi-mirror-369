import time

def login():
    username = input("Enter your username: ")
    password = input("Enter the password: ")
    veripassword = input("Verify the password: ")

    enter = input("Type 'redenter' to continue: ")

    if enter == "redenter":
        print(f"Hello! {username}, your account has been initialized.")
        time.sleep(1)
    else:
        print("Something went wrong.")
