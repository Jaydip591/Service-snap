import bcrypt

hashed_password = b"$2b$12$Td7oPCetNTtTg1SgpTOQQ.ikbMeb2m5PraxulAveitUUeesNDHaMG"  # Your bcrypt hash
password_guess = input("Enter password to check: ").encode('utf-8')  

if bcrypt.checkpw(password_guess, hashed_password):
    print("Password matches!")
else:
    print("Incorrect password!")
