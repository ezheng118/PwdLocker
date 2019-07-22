#! python3
import pyperclip
import os.path
import argparse

#add the ability to make and retrieve accounts using -a "acctname"
#make a local chrome extension for autofilling passwords
#add a feature to backup password file

def login():
    if not os.path.isfile("./master_pass.txt"):
        open("master_pass.txt", mode="w")

    with open("master_pass.txt", mode="r+", encoding = "utf-8") as mp:
        maspass = mp.readline()
        if maspass != '':
            #print("mp file not empty")
            print("Enter master password: ")
            pwd_in = str(input())
            if maspass == pwd_in:
                print("correct password")
                return True
            else:
                print("password incorrect")
                return False
        else:
            #print("file empty but exists")
            add_new_master_pass(mp)
            return True
    print("login failed unexpectedly")
    return False

def add_new_master_pass(output_file):
    print("It appears you have not set up a master password to use this password manager with.")
    print("Please enter a password: ")
    output_file.write(str(input()))

def load_passwords():
    if not os.path.isfile("./passwords.txt"):
        open("passwords.txt", mode="w")
   
    pass_dict = {}

    with open("passwords.txt", mode="r") as pf:
        for line in pf:
            item = line.split(',')
            #gets the contents of the line excluding the newline character at the end
            if item[1][-1] == "\n":
                pass_dict[item[0]] = item[1][:-1]
            else:
                pass_dict[item[0]] = item[1]
    
    return pass_dict

def get_password(password_dict, acct_name = ""):
    if acct_name == "":
        print("Enter the name of the account you would like the password for: ")
        acct_name = str(input())

    while acct_name not in password_dict:
        print("The account name you entered is not valid")
        print("Please enter the name of a valid account: ")
        acct_name = str(input())
    
    pyperclip.copy(password_dict[acct_name])
    print("password for " + acct_name + " copied to clipboard")

#should be replaced with a password generating function
def add_new_password(password_dict, acct_name = ""):
    if acct_name == "":
        print("Enter account name: ")
        acct_name = str(input())

    while acct_name in password_dict:
        print("The account name you entered already has an associated password.\nPlease enter a different account name:")
        acct_name = str(input())

    print("Enter account password: ")
    pwd = str(input())
    password_dict[acct_name] = pwd

def save_quit(password_dict):
    fname = "./passwords.txt"
    if not os.path.isfile(fname):
        print("Error: passwords file does not exist, a new password file will be created")
    
    with open(fname, mode = "w") as outfile:
        for key in password_dict:
            outfile.write(str(key) + "," + str(password_dict[key]) + "\n")

def run_prog(password_dict):
    user_input = 0
    while user_input != 3:
        print("Enter the number corresponding what you want to do.")
        print("1. Retrieve a password")
        print("2. Add a new password")
        print("3. Save and quit")

        user_input = str(input())
        while not user_input.isdecimal():
            print("Please input a valid response: ")
            user_input = str(input())

        user_input = int(user_input)
        if user_input == 1:
            get_password(password_dict)
        elif user_input == 2:
            add_new_password(password_dict)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "store and retrieve passwords through the command line")

    parser.add_argument("-n", "--new", help = "optional flag to add a new account and its associated password", 
        required = False, action = "store_true")
    parser.add_argument("-g", "--get", help = "optional flag to retrieve the password associated with a certain account",
        required = False, action = "store_true")
    parser.add_argument("-a", "--acct", help = '''used with -n or -g to either add a new password or retrieve a password, 
        will do nothing if other flags are not specified''',
        required = False, default = "", type = str)

    args = vars(parser.parse_args())

    if not login():
        print("login failed")
        quit()
    
    print("\nlogin successful\n")
    
    #put all of the user's passwords into a dictionary
    #k = account name
    #v = account password
    passwords = load_passwords()
    
    for key in passwords:
        print(key + " " + passwords[key])

    for item in args:
        print(item + " value: " + str(args[item]))
    print("\n")

    if args["new"] == True:
        add_new_password(passwords, args["acct"])
    elif args["get"] == True:
        get_password(passwords, args["acct"])
    else:
        run_prog(passwords)
        
    save_quit(passwords)
