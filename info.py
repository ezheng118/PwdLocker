import enum

# enumerator containing return code information 
# used when passing information between the password
# manager and the ui
class ReturnCode(enum.Enum):
    success = 0
    incorrect_pwd = 1

    no_master_pwd = 2
    no_stored_pwds = 3

    unexpected_failure = 100

    repeat_acct = 4
    acct_dne = 5
    empty_input = 6