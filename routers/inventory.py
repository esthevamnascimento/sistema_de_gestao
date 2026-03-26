from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db


# 1. Importe a função que verifica o Token
from routers.auth import get_current_user 

# 2. Adicione a dependência (dependencies) para trancar todas as rotas deste arquivo!
router = APIRouter(
    prefix="/api/epi", 
    tags=["EPIs"],
    dependencies=[Depends(get_current_user)]
)


router = APIRouter(prefix="/api/inventory", tags=["Estoque"])

@router.post("/", response_model=schemas.InventoryResponse)
def create_material(material: schemas.InventoryCreate, db: Session = Depends(get_db)):
    db_material = db.query(models.Inventory).filter(models.Inventory.material_code == material.material_code).first()
    if db_material:
        raise HTTPException(status_code=400, detail="Código de material já cadastrado.")
    
    new_material = models.Inventory(**material.dict())
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    return new_material

@router.get("/")
def get_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()

@router.put("/{material_id}/quantity")
def update_quantity(material_id: int, update_data: schemas.InventoryUpdateQuantity, db: Session = Depends(get_db)):
    material = db.query(models.Inventory).filter(models.Inventory.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    
    nova_quantidade = material.quantity + update_data.quantity_change
    if nova_quantidade < 0:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente em estoque.")
        
    material.quantity = nova_quantidade
    db.commit()
    return {"message": "Estoque atualizado!", "new_quantity": material.quantity}

@router.post("/{inv_id}/log")
def add_inventory_log(inv_id: int, log_data: schemas.InventoryLogCreate, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inv_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    # Se for SAÍDA, verifica se tem estoque suficiente
    if log_data.action_type == "SAÍDA" and item.quantity < log_data.quantity_changed:
        raise HTTPException(status_code=400, detail="Estoque insuficiente para esta retirada!")

    # Atualiza a quantidade do estoque principal
    if log_data.action_type == "ENTRADA":
        item.quantity += log_data.quantity_changed
    else:
        item.quantity -= log_data.quantity_changed

    # Cria o registro no histórico
    new_log = models.InventoryLog(
        inventory_id=inv_id,
        employee_id=log_data.employee_id,
        log_date=log_data.log_date,
        quantity_changed=log_data.quantity_changed,
        action_type=log_data.action_type
    )
    
    db.add(new_log)
    db.commit()
    return {"message": "Movimentação registrada com sucesso!"}

@router.get("/{inv_id}/log")
def get_inventory_logs(inv_id: int, db: Session = Depends(get_db)):
    # Busca os logs ordenados do mais recente para o mais antigo
    logs = db.query(models.InventoryLog).filter(models.InventoryLog.inventory_id == inv_id).order_by(models.InventoryLog.log_date.desc()).all()
    
    resultado = []
    for log in logs:
        # Pega o nome do funcionário se existir
        emp_name = log.employee.name if log.employee else "Sistema / Compra"
        
        resultado.append({
            "id": log.id,
            "inventory_id": log.inventory_id,
            "employee_id": log.employee_id,
            "employee_name": emp_name,
            "log_date": log.log_date,
            "quantity_changed": log.quantity_changed,
            "action_type": log.action_type
        })
    return resultado