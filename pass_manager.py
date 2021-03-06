#! /usr/bin/python3

import pyperclip
import os.path
import inspect
import argparse
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from info import ReturnCode

# currently only compatible with linux i think

class PassManager:
    """class that handles retrieval and storage of passwords"""
    
    # fields:
    # pwd_dict -> dictionary containing passwords and the accts they are associated with
    # unsure if this is the correct way to store this key
    # sym_key -> symmetric key for encrypting and decrypting the password file
    
    def __init__(self):
        self.pwd_dict = {}
        self.sym_key = None

    def login(self, input_pwd):
        mpwd_file = self.__get_dirname() + "/master_pass.txt"

        with open(mpwd_file, mode="r+") as mp:
            mp_hash = mp.readline()

            if mp_hash != '':
                input_pwd = input_pwd.encode()

                # check the hash of the password to see if it is correct
                # should hash the password more than once
                if mp_hash == hashlib.sha256(input_pwd).hexdigest():
                    self.__gen_key(input_pwd)
                    return ReturnCode.success
                else:
                    return ReturnCode.incorrect_pwd
            else:
                return ReturnCode.no_master_pwd
        return ReturnCode.unexpected_failure

    def add_new_master_pass(self, input_pwd):
        mpwd_file = self.__get_dirname() + "/master_pass.txt"

        # the user input is hashed before it is written
        input_pwd = input_pwd.encode()
        hashed_pwd_digest = hashlib.sha256(input_pwd).hexdigest()

        with open(mpwd_file, mode="w") as out_file:
            out_file.write(hashed_pwd_digest)

        self.__gen_key(input_pwd)
        return ReturnCode.success

    def mp_exists(self):
        mpwd_file = self.__get_dirname() + "/master_pass.txt"

        # check to see if a master password has been created yet
        if os.path.isfile(mpwd_file):
            with open(mpwd_file, mode="r+") as mp:
                return mp.readline() != ""
        else:
            open(mpwd_file, mode="w")
            return False

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
        self.sym_key = base64.urlsafe_b64encode(kdf.derive(pwd))

    def load_passwords(self):
        if self.pwd_dict:
            return self.pwd_dict
        
        pwd_file = self.__get_dirname() + "/passwords.txt"

        if not os.path.isfile(pwd_file):
            open(pwd_file, mode="w")

        with open(pwd_file, mode="r") as pf:
            fern = Fernet(self.sym_key)
            for line in pf:
                line = line.rstrip()  # remove trailing whitespace

                # get the encrypted password data
                encrypted_key, encrypted_val = line.split(',')

                # decrypt and store the password data
                key = fern.decrypt(encrypted_key.encode())
                val = fern.decrypt(encrypted_val.encode())
                self.pwd_dict[key.decode()] = val.decode()
        
        return self.pwd_dict

    def get_password(self, acct_name = ""):
        if not self.pwd_dict:
            # need to ensure that the program does not run forever
            # ie pwd_dict is empty
            return ReturnCode.no_stored_pwds
        elif acct_name == "":
            return ReturnCode.empty_input
        elif acct_name not in self.pwd_dict:
            return ReturnCode.acct_dne
        
        pyperclip.copy(self.pwd_dict[acct_name])
        return ReturnCode.success

    # should be replaced with a password generating function
    def add_new_password(self, acct_name = "", acct_pwd = ""):
        if acct_name == "" or acct_pwd == "":
            return ReturnCode.empty_input

        if acct_name in self.pwd_dict:
            return ReturnCode.repeat_acct

        self.pwd_dict[acct_name] = acct_pwd
        return ReturnCode.success
    
    def rm_acct(self, acct_name = ""):
        if acct_name == "":
            return ReturnCode.empty_input

        if acct_name not in self.pwd_dict:
            return ReturnCode.acct_dne
        
        self.pwd_dict.pop(acct_name)
        return ReturnCode.success

    # returns a list of names of accounts stored in the program
    def list_account_names(self):
        return list(self.pwd_dict.keys())

    def save_quit(self):
        fname = self.__get_dirname() + "/passwords.txt"
        if not os.path.isfile(fname):
            print("Error: passwords file does not exist, a new password file will be created")
        
        with open(fname, mode = "w") as outfile:
            fern = Fernet(self.sym_key)
            for key in self.pwd_dict:
                encrypted_key = fern.encrypt(key.encode())
                encrypted_val = fern.encrypt(self.pwd_dict[key].encode())
                outfile.write(encrypted_key.decode() + "," + encrypted_val.decode() + "\n")

    def __get_dirname(self):
        return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

'''
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
    parser.add_argument("-a", "--acct", help = "used with -n or -g to either add a new password or retrieve a password, 
        will do nothing if other flags are not specified",
        required = False, default = "", type = str)
    parser.add_argument("-l", "--list", help = "lists the names of the accounts stored in the manager program",
        required = False, action = "store_true")

    args = vars(parser.parse_args())
    manager = PassManager()

    if not manager.login(str(input("Enter master password: "))):
        print("login failed")
        quit()
    
    print("\nlogin successful")
    
    # put all of the user's passwords into a dictionary
    # k = account name
    # v = account password
    manager.load_passwords()

    if args["new"] == True:
        manager.add_new_password(args["acct"])
    elif args["get"] == True:
        manager.get_password(args["acct"])
    elif args["list"] == True:
        manager.list_account_names()
    else:
        run_prog()
        
    manager.save_quit()
'''