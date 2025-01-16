import bcrypt

stored_hashed_password = b"$2b$12$Y5uCvUvTATdzaSWQIsrsTOeLB.YkqQbtw6ccv7SiVZ8VivbLAt7Ii"

entered_password = "Jaydip.m.p"

print((stored_hashed_password.decode('utf-8')))
if bcrypt.checkpw(entered_password.encode('utf-8'), stored_hashed_password):
    print("Password is correct!")
else:
    print("Invalid password.")
    