#! /usr/bin/python3

import pyperclip
import os.path
import inspect
import argparse
import hashlib

# currently only compatible with linux i think

def login():
    mpwd_file = get_dirname() + "/master_pass.txt"

    if not os.path.isfile(mpwd_file):
        # if there is not a master password file that exists, create one
        open(mpwd_file, mode="w")

    with open(mpwd_file, mode="r+", encoding = "utf-8") as mp:
        maspass = mp.readline()
        if maspass != '':
            pwd_in = str(input("Enter master password: ")).encode()

            # check the hash of the password to see if it is correct
            if maspass == hashlib.sha256(pwd_in).hexdigest():
                print("correct password")
                return True
            else:
                print("password incorrect")
                return False
        else:
            add_new_master_pass(mp)
            return True
    print("login failed unexpectedly")
    return False

def add_new_master_pass(output_file):
    print("It appears you have not set up a master password to use this password manager with.")
    
    # the user input is hashed before it is outputted
    user_input = str(input("Please enter a password: ")).encode()
    hashed_pwd_digest = hashlib.sha256(user_input).hexdigest()
    output_file.write(hashed_pwd_digest)

def load_passwords():
    pwd_file = get_dirname() + "/passwords.txt"

    if not os.path.isfile(pwd_file):
        open(pwd_file, mode="w")
   
    pass_dict = {}

    with open(pwd_file, mode="r") as pf:
        for line in pf:
            key, val = line.split(',')
            # gets the contents of the line excluding the newline character at the end
            if val[-1] == "\n":
                pass_dict[key] = val[:-1]
            else:
                pass_dict[key] = val
    
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

# should be replaced with a password generating function
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

def list_account_names(password_dict):
    print("\nThe accounts on this machine with associated passwords are:")
    for key in password_dict:
        print(key)

def save_quit(password_dict):
    fname = get_dirname() + "/passwords.txt"
    if not os.path.isfile(fname):
        print("Error: passwords file does not exist, a new password file will be created")
    
    with open(fname, mode = "w") as outfile:
        for key in password_dict:
            outfile.write(str(key) + "," + str(password_dict[key]) + "\n")

def get_dirname():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def run_prog(password_dict):
    user_input = 0
    while user_input != 4:
        print("Enter the number corresponding what you want to do.")
        print("1. Retrieve a password")
        print("2. Add a new password")
        print("3. List accounts")
        print("4. Save and quit")

        user_input = str(input())
        while not user_input.isdecimal():
            user_input = str(input("Please input a valid response: "))

        user_input = int(user_input)
        if user_input == 1:
            get_password(password_dict)
        elif user_input == 2:
            add_new_password(password_dict)
        elif user_input == 3:
            list_account_names(password_dict)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "store and retrieve passwords through the command line")

    # arguments are added in order of precedence
    parser.add_argument("-n", "--new", help = "add a new account and its associated password", 
        required = False, action = "store_true")
    parser.add_argument("-g", "--get", help = "retrieve the password associated with a certain account",
        required = False, action = "store_true")
    parser.add_argument("-a", "--acct", help = '''used with -n or -g to either add a new password or retrieve a password, 
        will do nothing if other flags are not specified''',
        required = False, default = "", type = str)
    parser.add_argument("-l", "--list", help = "lists the names of the accounts stored in the manager program",
        required = False, action = "store_true")

    args = vars(parser.parse_args())

    if not login():
        print("login failed")
        quit()
    
    print("\nlogin successful")
    
    # put all of the user's passwords into a dictionary
    # k = account name
    # v = account password
    passwords = load_passwords()
    
    '''for key in passwords:
        print(key + " " + passwords[key])

    for item in args:
        print(item + " value: " + str(args[item]))
    print("\n")'''

    if args["new"] == True:
        add_new_password(passwords, args["acct"])
    elif args["get"] == True:
        get_password(passwords, args["acct"])
    elif args["list"] == True:
        list_account_names(passwords)
    else:
        run_prog(passwords)
        
    save_quit(passwords)
