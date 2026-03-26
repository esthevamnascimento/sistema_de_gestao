from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/ssm", tags=["SSM"], dependencies=[Depends(get_current_user)])

@router.post("/")
def create_ssm(ssm: schemas.SSMCreate, db: Session = Depends(get_db)):
    new_ssm = models.MaintenanceRequest(**ssm.dict())
    db.add(new_ssm)
    db.commit()
    return {"message": "SSM registrada com sucesso"}

@router.get("/")
def get_ssms(db: Session = Depends(get_db)):
    ssms = db.query(models.MaintenanceRequest).order_by(models.MaintenanceRequest.request_date.desc()).all()
    resultado = []
    
    # Monta a resposta pegando o nome do Carro ou da Ferramenta
    for ssm in ssms:
        target_name = "Desconhecido"
        if ssm.target_type == "Frota":
            frota = db.query(models.Fleet).filter(models.Fleet.id == ssm.target_id).first()
            if frota: target_name = f"{frota.model} ({frota.plate})"
        elif ssm.target_type == "Ferramenta":
            ferramenta = db.query(models.Tool).filter(models.Tool.id == ssm.target_id).first()
            if ferramenta: target_name = ferramenta.name
            
        resultado.append({
            "id": ssm.id,
            "employee_name": ssm.employee.name if ssm.employee else "Desconhecido",
            "target_type": ssm.target_type,
            "target_name": target_name,
            "description": ssm.description,
            "request_date": ssm.request_date,
            "status": ssm.status
        })
    return resultado

@router.put("/{ssm_id}/concluir")
def complete_ssm(ssm_id: int, db: Session = Depends(get_db)):
    ssm = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.id == ssm_id).first()
    if not ssm:
        raise HTTPException(status_code=404, detail="SSM não encontrada")
    ssm.status = "Concluído"
    db.commit()
    return {"message": "SSM Concluída"}