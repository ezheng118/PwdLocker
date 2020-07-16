#! /usr/bin/python3

import pyperclip
import os.path
import inspect
import argparse
import hashlib
import base64
from cryptography.fernet import Fernet as fnet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# currently only compatible with linux i think

class PassManager:
    """class that handles retrieval and storage of passwords"""
    
    # fields:
    # pwd_dict = dictionary containing passwords and the accts they are associated with
    # unsure if this is the correct way to store this key
    # key = symmetric key for encrypting and decrypting the password file
    
    def __init__(self):
        self.pwd_dict = {}
        self.key = None

    def login(self):
        mpwd_file = self.__get_dirname() + "/master_pass.txt"

        if not os.path.isfile(mpwd_file):
            # if there is not a master password file that exists, create one
            open(mpwd_file, mode="w")

        with open(mpwd_file, mode="r+", encoding = "utf-8") as mp:
            mp_hash = mp.readline()
            if mp_hash != '':
                input_pwd = str(input("Enter master password: ")).encode()

                # check the hash of the password to see if it is correct
                # should hash the password more than once
                if mp_hash == hashlib.sha256(input_pwd).hexdigest():
                    self.__gen_key(input_pwd)
                    print("correct password")
                    return True
                else:
                    print("password incorrect")
                    return False
            else:
                return self.__add_new_master_pass(mp)
        print("login failed unexpectedly")
        return False

    def __add_new_master_pass(self, output_file):
        print("It appears you have not set up a master password to use this password manager with.")
        
        # the user input is hashed before it is outputted
        input_pwd = str(input("Please enter a password: ")).encode()
        hashed_pwd_digest = hashlib.sha256(user_input).hexdigest()
        output_file.write(hashed_pwd_digest)

        self.__gen_key(input_pwd)
        return True

    def __gen_key(self, pwd):
        # need to figure out how to produce a better salt
        key_salt = b"saltine"
        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,
            salt = key_salt,
            iterations = 100, # doesn't need to actually be secure so only hashing a few times
            backend = default_backend()
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(pwd))

    def load_passwords(self):
        if self.pwd_dict:
            return self.pwd_dict
        
        pwd_file = self.__get_dirname() + "/passwords.txt"

        if not os.path.isfile(pwd_file):
            open(pwd_file, mode="w")

        with open(pwd_file, mode="r") as pf:
            for line in pf:
                key, val = line.split(',')
                # gets the contents of the line excluding the newline character at the end
                if val[-1] == "\n":
                    self.pwd_dict[key] = val[:-1]
                else:
                    self.pwd_dict[key] = val
        
        return self.pwd_dict

    def get_password(self, acct_name = ""):
        if acct_name == "":
            print("Enter the name of the account you would like the password for: ")
            acct_name = str(input())

        # need to ensure that the prorgam does not run forever
        # ie pwd_dict is empty
        while acct_name not in self.pwd_dict:
            print("The account name you entered is not valid")
            print("Please enter the name of a valid account: ")
            acct_name = str(input())
        
        pyperclip.copy(self.pwd_dict[acct_name])
        print("password for " + acct_name + " copied to clipboard")

    # should be replaced with a password generating function
    def add_new_password(self, acct_name = ""):
        if acct_name == "":
            print("Enter account name: ")
            acct_name = str(input())

        while acct_name in self.pwd_dict:
            print("The account name you entered already has an associated password.")
            print("Please enter a different account name:")
            acct_name = str(input())

        print("Enter account password: ")
        pwd = str(input())
        self.pwd_dict[acct_name] = pwd

    def list_account_names(self):
        print("\nThe accounts on this machine with associated passwords are:")
        for key in self.pwd_dict:
            print(key)

    def save_quit(self):
        fname = self.__get_dirname() + "/passwords.txt"
        if not os.path.isfile(fname):
            print("Error: passwords file does not exist, a new password file will be created")
        
        with open(fname, mode = "w") as outfile:
            for key in self.pwd_dict:
                outfile.write(str(key) + "," + str(self.pwd_dict[key]) + "\n")

    def __get_dirname(self):
        return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def run_prog():
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
            manager.get_password()
        elif user_input == 2:
            manager.add_new_password()
        elif user_input == 3:
            manager.list_account_names()

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
    manager = PassManager()

    if not manager.login():
        print("login failed")
        quit()
    
    print("\nlogin successful")
    
    # put all of the user's passwords into a dictionary
    # k = account name
    # v = account password
    manager.load_passwords()
    
    '''for key in passwords:
        print(key + " " + passwords[key])

    for item in args:
        print(item + " value: " + str(args[item]))
    print("\n")'''

    if args["new"] == True:
        manager.add_new_password(args["acct"])
    elif args["get"] == True:
        manager.get_password(args["acct"])
    elif args["list"] == True:
        manager.list_account_names()
    else:
        run_prog()
        
    manager.save_quit()
