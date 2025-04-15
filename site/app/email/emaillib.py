#should take the username and password, passes the pw to another function and combines it with the salt for the password verification
def login(user, pw):
    
    return
#sends a OTP 6 digit num for verification, along with the username
def new_user_signup():
    return

#should send a password reset link to the email associated with the user, no real auth plans for this atm
#(does the link need to have some sort of hash to prevent attacks?)
def password_reset(user):
    return

#combines the password with the correct salt, compares the user and the hash of the salt/pw to the stored entry
def verify_user(user, pw, salt):
    return
