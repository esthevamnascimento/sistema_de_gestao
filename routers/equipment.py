from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/equipment", 
    tags=["Equipamentos"],
    dependencies=[Depends(get_current_user)] # Rota trancada!
)

@router.post("/", response_model=schemas.EquipmentResponse)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    # Evita cadastrar o mesmo número de série duas vezes
    db_eq = db.query(models.Equipment).filter(models.Equipment.serial_number == equipment.serial_number).first()
    if db_eq:
        raise HTTPException(status_code=400, detail="Número de série já cadastrado.")
    
    new_eq = models.Equipment(**equipment.dict())
    db.add(new_eq)
    db.commit()
    db.refresh(new_eq)
    return new_eq

@router.get("/")
def get_equipments(db: Session = Depends(get_db)):
    equipments = db.query(models.Equipment).all()
    # Verifica dinamicamente se a calibração está vencida
    for eq in equipments:
        eq.is_expired = eq.due_date < date.today()
    return equipments

# ... (código existente de criar e listar) ...

@router.get("/")
def get_equipments(db: Session = Depends(get_db)):
    equipments = db.query(models.Equipment).all()
    for eq in equipments:
        eq.is_expired = eq.due_date < date.today()
    return equipments

# --- ADICIONE ESTE BLOCO NO FINAL DO ARQUIVO ---
@router.delete("/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
    
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado.")
        
    db.delete(equipment)
    db.commit()
    return {"message": "Equipamento excluído com sucesso!"}

@router.put("/{eq_id}/recalibrate")
def recalibrate_equipment(eq_id: int, data: schemas.EquipmentRecalibrate, db: Session = Depends(get_db)):
    eq = db.query(models.Equipment).filter(models.Equipment.id == eq_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    
    # Atualiza as datas com os novos valores
    eq.calibration_date = data.calibration_date
    eq.due_date = data.due_date
    
    db.commit()
    db.refresh(eq)
    return {"message": "Equipamento recalibrado com sucesso"}