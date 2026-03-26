from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models, schemas
from database import get_db

# 1. Importe a função que verifica o Token
from routers.auth import get_current_user 

# 2. ÚNICA DECLARAÇÃO: Prefix /api/epi e trancado com segurança
router = APIRouter(
    prefix="/api/epi", 
    tags=["EPIs"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=schemas.EPIResponse)
def create_epi(epi: schemas.EPICreate, db: Session = Depends(get_db)):
    # Clean Code: Verifique se o CA já existe antes de salvar
    db_epi = db.query(models.EPI).filter(models.EPI.ca_number == epi.ca_number).first()
    if db_epi:
        raise HTTPException(status_code=400, detail="Número de CA já cadastrado.") 

    # Criando o novo EPI (o Python já mapeia ca_validity_date do seu schema)
    new_epi = models.EPI(**epi.dict())
    db.add(new_epi)
    db.commit()
    db.refresh(new_epi)
    return new_epi

@router.get("/")
def get_epis(db: Session = Depends(get_db)):
    """Retorna a lista de EPIs e calcula se estão vencidos para o front-end"""
    epis = db.query(models.EPI).all()
    hoje = date.today()
    for epi in epis:
        # Verifica se a data de validade é menor que hoje
        epi.is_expired = epi.ca_validity_date < hoje #
    return epis

@router.delete("/{epi_id}")
def delete_epi(epi_id: int, db: Session = Depends(get_db)):
    """Rota para o botão de excluir"""
    epi = db.query(models.EPI).filter(models.EPI.id == epi_id).first()
    if not epi:
        raise HTTPException(status_code=404, detail="EPI não encontrado.")
    db.delete(epi)
    db.commit()
    return {"message": "EPI excluído com sucesso"}

# Rota para atribuição (opcional, se você estiver usando)
@router.post("/assign")
def assign_epi(assignment: schemas.EPIAssignmentCreate, db: Session = Depends(get_db)):
    new_assignment = models.EPIAssignment(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    return {"message": "EPI atribuído com sucesso"}

@router.post("/request", response_model=schemas.EPIRequestResponse)
def create_epi_request(req: schemas.EPIRequestCreate, db: Session = Depends(get_db)):
    new_req = models.EPIRequest(
        employee_id=req.employee_id,
        epi_description=req.epi_description,
        request_date=req.request_date
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req

@router.get("/request")
def get_epi_requests(db: Session = Depends(get_db)):
    # Busca todos os pedidos, do mais novo para o mais antigo
    requests = db.query(models.EPIRequest).order_by(models.EPIRequest.request_date.desc()).all()
    
    resultado = []
    for r in requests:
        resultado.append({
            "id": r.id,
            "employee_id": r.employee_id,
            "employee_name": r.employee.name if r.employee else "Desconhecido",
            "epi_description": r.epi_description,
            "request_date": r.request_date,
            "status": r.status
        })
    return resultado

@router.put("/request/{req_id}/atender")
def attend_epi_request(req_id: int, db: Session = Depends(get_db)):
    req = db.query(models.EPIRequest).filter(models.EPIRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    req.status = "Atendido" # Muda o status para verde na tela
    db.commit()
    return {"message": "Pedido marcado como atendido"}