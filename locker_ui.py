import curses
import cli_ui as ui
from pass_manager import PassManager
from info import ReturnCode

class LockerUI:
    '''class that acts as the ui for the program'''

    # fields:
    # manager -> password manager object, model which manages the password data
    # scrn -> curses screen object, not currently in use

    def __init__(self, stdscr):
        ui.setup(verbose=True, timestamp=True)
        self.manager = PassManager()
        
        self.scrn = stdscr
        self.scrn.clear()

    def __login(self):
        h, w = self.scrn.getmaxyx()

        if self.manager.mp_exists():
            # print login info towards the center of the screen
            cursor_y = (h // 2) - 2
            cursor_x = (w // 2)

            mp_prompt = "Enter master password:"
            
            self.scrn.addstr(cursor_y, cursor_x - (len(mp_prompt) // 2), 
                mp_prompt, curses.color_pair(1))
            cursor_y += 1

            # echo characters typed
            curses.echo()

            # get password
            pwd_in = self.scrn.getstr(cursor_y, cursor_x - (len(mp_prompt) // 2))
            cursor_y += 1
            
            # turn character echoing back off
            curses.noecho()

            # returns the string as byts so it needs to be decoded
            pwd_in = pwd_in.decode()

            # check login credentials
            ret_val = self.manager.login(pwd_in)
            
            if ret_val == ReturnCode.success:
                self.scrn.addstr(cursor_y, cursor_x - 8, 
                    "Login successful", curses.color_pair(1))
                cursor_y += 1
                
                self.manager.load_passwords()

                self.scrn.addstr(cursor_y, cursor_x - 13, 
                    "Press any key to continue", curses.color_pair(1))

                self.scrn.getch()

                return True
            elif ret_val == ReturnCode.no_master_pwd:
                print("Error: master password existence check failed")
                return False
            else:
                print("Login failed")
                return False
        else: # need to set up a new password
            cursor_y = 0
            cursor_x = 0

            self.scrn.addstr(cursor_y, cursor_x, 
                "It appears you have not set up a master password to use this password manager with.",
                curses.color_pair(1))
            cursor_y += 1

            self.scrn.addstr(cursor_y, cursor_x,
                "Please enter a new master password:",
                curses.color_pair(1))
            cursor_y += 1
            
            curses.echo()

            pwd = self.scrn.getstr(cursor_y, cursor_x)
            cursor_y += 1

            self.scrn.addstr(cursor_y, cursor_x,
                "Re-enter the password:",
                curses.color_pair(1))
            cursor_y += 1
            
            pwd_conf = self.scrn.getstr(cursor_y, cursor_x)
            cursor_y += 1

            curses.noecho()

            pwd = pwd.decode()
            pwd_conf = pwd_conf.decode()

            if pwd == pwd_conf:
                ret_val = self.manager.add_new_master_pass(pwd)

                if ret_val == ReturnCode.success:
                    ui.info("New master password created successfully")
                    self.manager.load_passwords()
            else:
                ui.info("Passwords do not match")
                ui.info("Add password operation failed")

                return False
            
    def __get_pwd(self):
        acct = ui.ask_string("Enter the name of the account whose password you want:")
        self.manager.get_password(acct)

    def __add_new_pwd(self):
        acct = ui.ask_string("Enter the name of the new account:")
        pwd = ui.ask_password("Enter the password for this account:")
        pwd_conf = ui.ask_password("Re-enter the password:")

        if pwd == pwd_conf:
            self.manager.add_new_password(acct, pwd)
        else:
            ui.info("Passwords do not match")
            ui.info("Add password operation failed")

    def __rm_acct(self):
        acct = ui.ask_string("Enter the name of the new account:")
        self.manager.rm_acct(acct)

    def __list_accts(self):
        self.manager.list_account_names()

    def __save_quit(self):
        self.manager.save_quit()

    # begins running the pwdLocker program
    def start(self):
        # make screen blank
        self.scrn.clear()
        self.scrn.refresh()

        # start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        if self.__login():
            self.draw_menu()

    def draw_menu(self):
        k = 0
        # cursor_x = 0
        cursor_y = 1

        while(k != ord('q')):
            self.scrn.clear()
            h, w = self.scrn.getmaxyx()

            if k == curses.KEY_DOWN or k == ord('s'):
                cursor_y = cursor_y + 1
            elif k == curses.KEY_UP or k == ord('w'):
                cursor_y = cursor_y - 1
            elif k == curses.KEY_ENTER:
                # launch into specific function based off
                # of the cursor position
                if cursor_y == 1:
                    # retrieve pwd
                    self.__get_pwd()
                elif cursor_y == 1:
                    # add new password
                    self.__add_new_pwd()
                elif cursor_y == 1:
                    # remove acct and associated pwd
                    self.__rm_acct()
                elif cursor_y == 1:
                    # list pwds
                    self.__list_accts()

            ''' no need to move left or right atm
            elif k == curses.KEY_RIGHT or k == ord('d'):
                cursor_x = cursor_x + 1
            elif k == curses.KEY_LEFT or k == ord('a'):
                cursor_x = cursor_x - 1'''

            # keep cursor within menu bounds
            cursor_y = max(1, cursor_y)
            cursor_y = min(h-1, 4, cursor_y)

            # text to be displayed
            prompt = "Please select the action you'd like to take."[:w-1]
            options = ["Retrieve password", "Add new account",
                "Remove account", "List passwords"]
            statusbar_str = f"Press 'q' to exit | Press 'enter' to select | Pos: 0, {cursor_y}"[:w-1]
            
            # render the prompt for the user
            self.scrn.addstr(0, 0, prompt)

            for option, text in enumerate(options, 1):
                if option == cursor_y:
                    self.scrn.addstr(option, 0, text, curses.color_pair(1))
                else:
                    self.scrn.addstr(option, 0, text)

            # render status bar
            self.scrn.attron(curses.color_pair(3))
            self.scrn.addstr(h-1, 0, statusbar_str)
            self.scrn.addstr(h-1, len(statusbar_str), " " * (w - len(statusbar_str) - 1))
            self.scrn.attroff(curses.color_pair(3))

            self.scrn.refresh()

            # wait for the next input
            k = self.scrn.getch()
        self.__save_quit()

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)

    lui = LockerUI(stdscr)

    curses.wrapper(lui.start())
    # lui.start()

    curses.curs_set(1)
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


    '''
    # status text to be displayed
    title = "test"[:w-1]
    subtitle = "adapted from McLeod"[:w-1]
    key_str = f"Last key pressed: {k}"[:w-1]
    statusbar_str = f"Press 'q' to exit | STATUS BAR | Pos: {cursor_x}, {cursor_y}"

    if k == 0:
        key_str = "No key press detected..."[:w-1]
            
    # centering calculations
    start_x_title = int((w // 2) - (len(title) // 2) -len(title) % 2)
    start_x_subtitle = int((w // 2) - (len(subtitle) // 2) -len(subtitle) % 2)
    start_x_keystr = int((w // 2) - (len(key_str) // 2) -len(key_str) % 2)
    start_y = int((h // 2) - 2)

    # rendering the text
    whstr = f"Width: {w}, Height: {h}"
    self.scrn.addstr(0, 0, whstr, curses.color_pair(1))

    # render status bar
    self.scrn.attron(curses.color_pair(3))
    self.scrn.addstr(h-1, 0, statusbar_str)
    self.scrn.addstr(h-1, len(statusbar_str), " " * (w - len(statusbar_str) - 1))
    self.scrn.attroff(curses.color_pair(3))

    # render title
    self.scrn.attron(curses.color_pair(2))
    self.scrn.attron(curses.A_BOLD)

    self.scrn.addstr(start_y, start_x_title, title)
            
    self.scrn.attroff(curses.color_pair(2))
    self.scrn.attroff(curses.A_BOLD)

    # render the rest of the text
    self.scrn.addstr(start_y + 1, start_x_subtitle, subtitle)
    self.scrn.addstr(start_y + 3, (w // 2) - 2, "-" * 4)
    self.scrn.addstr(start_y + 5, start_x_keystr, key_str)
            
    self.scrn.move(cursor_y, cursor_x)
'''