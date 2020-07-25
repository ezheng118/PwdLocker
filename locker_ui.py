import curses
import cli_ui as ui
from pass_manager import PassManager

class Locker_UI:
    '''class that acts as the ui for the program'''

    # fields:
    # options -> holds the text describing the actions the user may choose to take
    # manager -> password manager object, model which manages the password data
    # scrn -> curses screen object, not currently in use

    def __init__(self):
        ui.setup(verbose=True, timestamp=True)
        self.options = ["Retrieve password", 
            "Add new account", 
            "Remove account",
            "List passwords", 
            "Save and quit"]
        self.manager = PassManager()
        
        # self.scrn = stdscr
        # self.scrn.clear()

    def __login(self):
        if self.manager.login(ui.ask_password("Enter master password: ")):
            ui.info("Login successful")
            self.manager.load_passwords()
        else:
            ui.info("Login failed")
            quit()

    def __get_pwd(self):
        acct = ui.ask_string("Enter the name of the account whose password you want:")
        self.manager.get_password(acct)

    def __add_new_pwd(self):
        acct = ui.ask_string("Enter the name of the new account:")
        pwd = ui.ask_password("Enter the password for this account:")
        pwd_conf = ui.ask_password("Re-enter the password:")

        if pwd != pwd_conf:
            ui.info("Passwords dont match")
            ui.info("Add password operation failed")
        else:
            self.manager.add_new_password(acct, pwd)

    def __rm_acct(self):
        acct = ui.ask_string("Enter the name of the new account:")
        self.manager.rm_acct(acct)

    def __list_accts(self):
        self.manager.list_account_names()

    def __save_quit(self):
        self.manager.save_quit()

    def __menu(self):
        choice = ui.ask_choice("Select an action", choices=self.options)

        if choice == "Retrieve password":
            self.__get_pwd()
        elif choice == "Add new account":
            self.__add_new_pwd()
        elif choice == "Remove account":
            self.__rm_acct()
        elif choice == "List passwords":
            self.__list_accts()
        elif choice == "Save and quit":
            self.__save_quit()
            return False

        return True

    # begins running the pwdLocker program
    def start(self):
        self.__login()
        
        run = True
        while(run):
            run = self.__menu()

'''
    def ui_test(self):
        k = 0
        curs_x = 0
        curs_y = 0

        # h, w = self.scrn.getmaxyx()

        heart = ui.Symbol("❤", "<3")

        self.scrn.clear()
        self.scrn.refresh()
        ui.info(ui.blue, "line 1")

        curs_y = curs_y + 1
        self.scrn.move(curs_y, curs_x)
        ui.info(ui.red, "line 2")

        curs_y = curs_y + 1
        self.scrn.move(curs_y, curs_x)
        ui.info(ui.green, "press any button to continue", ui.fuschia, heart)

        k = self.scrn.getch()

        return True

    def draw_screen(self):
        k = 0
        cursor_x = 0
        cursor_y = 0

        # make screen blank
        self.scrn.clear()
        self.scrn.refresh()

        # start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        while(k != ord('q')):
            self.scrn.clear()
            h, w = self.scrn.getmaxyx()

            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 1
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 1
            elif k == curses.KEY_RIGHT:
                cursor_x = cursor_x + 1
            elif k == curses.KEY_LEFT:
                cursor_x = cursor_x - 1

            # keep cursor within screen bounds
            cursor_x = max(0, cursor_x)
            cursor_x = min(w-1, cursor_x)

            cursor_y = max(0, cursor_y)
            cursor_y = min(h-1, cursor_y)


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

            self.scrn.refresh()

            # wait for the next input
            k = self.scrn.getch()
'''

if __name__ == "__main__":
    '''
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)

    lui = Locker_UI(stdscr)

    # curses.wrapper(lui.start())
    lui.start()

    curses.curs_set(1)
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    '''
    lui = Locker_UI()
    lui.start()