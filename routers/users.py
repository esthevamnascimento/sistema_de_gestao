from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["Usuários do Sistema"])

# Reutiliza a criptografia segura
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Trava de Segurança: Verifica se quem está a chamar a rota é ADMIN
def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Área restrita a administradores.")
    return current_user

@router.get("/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    return db.query(models.User).all()

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    # Verifica se já existe um utilizador com esse nome
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Este nome de usuário já está em uso.")
    
    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}/password")
def reset_password(user_id: int, data: schemas.UserPasswordReset, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    db_user.hashed_password = pwd_context.hash(data.new_password)
    db.commit()
    return {"message": "Senha atualizada com sucesso."}

@router.put("/{user_id}/role")
def update_role(user_id: int, data: schemas.UserRoleUpdate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    # Bloqueia o admin de tirar o próprio acesso por acidente
    if db_user.id == admin.id and data.role != "admin":
        raise HTTPException(status_code=400, detail="Você não pode remover o seu próprio acesso de Admin!")

    db_user.role = data.role
    db.commit()
    return {"message": "Perfil de acesso atualizado."}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    # Bloqueia o admin de se excluir
    if db_user.id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir a sua própria conta logada.")
        
    db.delete(db_user)
    db.commit()
    return {"message": "Usuário excluído."}