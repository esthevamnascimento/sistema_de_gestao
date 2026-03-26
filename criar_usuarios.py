from database import SessionLocal, engine, Base
import models
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)
db = SessionLocal()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# 1. Verifica se o Admin existe. Se não existir, ele cria.
admin = db.query(models.User).filter(models.User.username == "admin").first()
if not admin:
    novo_admin = models.User(
        username="admin", 
        hashed_password=pwd_context.hash("admin123"), 
        role="admin"
    )
    db.add(novo_admin)
    print("-> Usuário ADMIN criado!")
else:
    # Se já existir, garante que o perfil dele é admin
    admin.role = "admin"
    print("-> Usuário ADMIN já existia. Perfil atualizado.")

# 2. Verifica se o Operador existe. Se não, ele cria.
operador = db.query(models.User).filter(models.User.username == "operador").first()
if not operador:
    novo_operador = models.User(
        username="operador", 
        hashed_password=pwd_context.hash("operador123"), 
        role="operador"
    )
    db.add(novo_operador)
    print("-> Usuário OPERADOR criado!")
else:
    print("-> Usuário OPERADOR já existia.")

db.commit()
print("✅ Tudo pronto! Pode fazer o login.")