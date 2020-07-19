import cli_ui as ui
from pass_manager import PassManager

class Locker_UI:
    '''class that acts as the ui for the program'''

    # fields:
    # options -> holds the text describing the actions the user may choose to take
    # manager -> password manager object, model which manages the password data

    def __init__(self):
        ui.setup(verbose=True, timestamp=True)
        self.options = ["Retrieve password", 
            "Add new password", 
            "List passwords", 
            "Save and quit"]
        self.manager = PassManager()

    def login(self):
        if self.manager.login(ui.ask_password("Enter master password: ")):
            ui.info("Login successful")
            self.manager.load_passwords()
        else:
            ui.info("Login failed")
            quit()

    def get_pwd(self):
        acct = ui.ask_string("Enter the name of the account whose password you want:")
        self.manager.get_password(acct)

    def add_new_pwd(self):
        acct = ui.ask_string("Enter the name of the new account:")
        pwd = ui.ask_password("Enter the password for this account:")
        pwd_conf = ui.ask_password("Re-enter the password:")

        if pwd != pwd_conf:
            ui.info("Passwords dont match")
            ui.info("Add password operation failed")
        else:
            self.manager.add_new_password(acct, pwd)

    def list_accts(self):
        self.manager.list_account_names()

    def save_quit(self):
        self.manager.save_quit()

    # begins running the pwdLocker program
    def start(self):
        self.login()

        run = True

        while(run):
            try:
                user_input = ui.ask_choice("Select the action you would like to take.",
                    choices=lui.options)
            except KeyboardInterrupt:
                user_input = None
                quit()
        
            # choices:
            # 1. retrieve pwd
            # 2. add pwd
            # 3. list accts
            # 4. save quit

            if user_input == None:
                continue
            elif user_input == "Retrieve password":
                lui.get_pwd()
            elif user_input == "Add new password":
                lui.add_new_pwd()
            elif user_input == "List passwords":
                lui.list_accts()
            elif user_input == "Save and quit":
                lui.save_quit()
                run = False


if __name__ == "__main__":
    lui = Locker_UI()

    lui.start()
