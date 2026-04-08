from argon2 import PasswordHasher

ph = PasswordHasher()
password = "admin123"
hash_genere = ph.hash(password)

print("-" * 30)
print(f"Mot de passe : {password}")
print(f"Empreinte a copier : {hash_genere}")
print("-" * 30)