from app.core.security import hash_password, verify_password

password = "Raj@123"

# Hash the password
hashed_password = hash_password(password)

print("Original Password :", password)
print("Hashed Password   :", hashed_password)

# Verify the password
is_valid = verify_password(password, hashed_password)

print("Password Verified :", is_valid)