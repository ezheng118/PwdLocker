import enum

# enumerator containing return code information 
# used when passing information between the password
# manager and the ui
class ReturnCode(enum.Enum):
    success = 0
    incorrect_pwd = 1
    no_master_pwd = 2
    unexpected_failure = 100
    
    repeat_acct = 3
    empty_input = 4
