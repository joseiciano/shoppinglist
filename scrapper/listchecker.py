import bcrypt
import re
from pricecheck import PriceChecker

# Let's a user login to an account stored in the db
def login(checker):
    print("Log into an account")
    result = False
    while (not result):
        email = input("Enter email: ")
        password = input("Enter password: ")
        result = checker.checkSignIn(email, password)
        if (not result):
            print("invalid login information. Please try again")
    print("Successful login")


# Let's a user register a new account and add it to the db
def register(checker):
    print("Registering account")
    email = input("Enter email: ")
    password = input("Enter password: ")
    hashedpw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    first = last = None
    while (not first and not last):
        name = input("Enter name (first last): ")
        listname = name.split()
        if (len(listname) != 2):
            print("Invalid input. Please try again")
            continue

        redo = False
        for name in listname:
            for i, char in enumerate(name):
                if (not char.isalpha()):
                    if (char == '-') and (i > 0):
                        continue
                    else:
                        redo = True
                        break
            if (redo):
                break
        if (redo):
            print("Invalid name input. Please try again")
            continue

        first, last = listname[0], listname[1]

    if (not checker.checkIfRegistered(email, first, last)):
        checker.adduser(first, last, email, hashedpw)
        print("Successful registration")
    
    loginmenu(checker)


def loginmenu(checker):
    print("1. Login to an account")
    print("2. Register an account")
    option = ''
    user = None
    while (option != '1' and option != '2'):
        option = input("Login or Register: ")
        if (option == '1'):
            login(checker)
        elif (option == '2'):
            register(checker)
        else:
            print("Incorrect option, please try again")
    return user


def optionsmenu(checker):
    choice = None
    while (choice != '5'):
        print("Options: ")
        print("1. Check for any price updates")
        print("2. See previous prices")
        print("3. Insert new items")
        print("4. Delete existing items")
        print("5. Exit")
        choice = input("Option: ")

        if (choice == '1'):
            checker.checkAll()
        elif (choice == '2'):
            checker.query()
        elif (choice == '3'):
            checker.insertAll()
        elif (choice == '4'):
            checker.remove()
        elif (choice == '5'):
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again")


def main():
    mongoCollection = "Users"
    mongoCluster = ""
    with open("cluster.txt", "r") as f:
        mongoCluster = f.readline().strip()

    checker = PriceChecker(mongoCluster)
    checker.setCollection(mongoCollection)
    loginmenu(checker)
    optionsmenu(checker)


if __name__ == '__main__':
    main()
