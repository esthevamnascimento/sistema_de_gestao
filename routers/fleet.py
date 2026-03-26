from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
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

router = APIRouter(prefix="/api/fleet", tags=["Frota"])

@router.post("/", response_model=schemas.FleetResponse)
def create_vehicle(vehicle: schemas.FleetCreate, db: Session = Depends(get_db)):
    db_vehicle = db.query(models.Fleet).filter(models.Fleet.plate == vehicle.plate).first()
    if db_vehicle:
        raise HTTPException(status_code=400, detail="Placa já cadastrada no sistema.")
    
    new_vehicle = models.Fleet(**vehicle.dict())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle

@router.get("/")
def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Fleet).all()
    # Regra de negócio: Avisar se a manutenção está próxima ou atrasada
    for v in vehicles:
        v.maintenance_alert = v.next_maintenance_date <= date.today()
    return vehicles

@router.put("/{vehicle_id}/km")
def update_km(vehicle_id: int, km_data: schemas.FleetUpdateKM, db: Session = Depends(get_db)):
    vehicle = db.query(models.Fleet).filter(models.Fleet.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    
    if km_data.new_km < vehicle.current_km:
        raise HTTPException(status_code=400, detail="A nova KM não pode ser menor que a atual.")
        
    vehicle.current_km = km_data.new_km
    db.commit()
    return {"message": "Quilometragem atualizada com sucesso!", "current_km": vehicle.current_km}

@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(models.Fleet).filter(models.Fleet.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    db.delete(vehicle)
    db.commit()
    return {"message": "Veículo excluído com sucesso!"}

@router.post("/{fleet_id}/fuel", response_model=schemas.FuelLogResponse)
def add_fuel_log(fleet_id: int, fuel_log: schemas.FuelLogCreate, db: Session = Depends(get_db)):
    db_fleet = db.query(models.Fleet).filter(models.Fleet.id == fleet_id).first()
    if not db_fleet:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    # Registra o abastecimento
    new_log = models.FuelLog(**fuel_log.dict(), fleet_id=fleet_id)
    
    # Atualiza o KM do veículo automaticamente se o KM da bomba for maior
    if fuel_log.km_at_fill > db_fleet.current_km:
        db_fleet.current_km = fuel_log.km_at_fill
        
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

# --- Adicione no final do arquivo routers/fleet.py ---
@router.get("/{fleet_id}/fuel", response_model=list[schemas.FuelLogResponse])
def get_fuel_logs(fleet_id: int, db: Session = Depends(get_db)):
    # Busca os registros no banco e ordena do mais novo para o mais velho
    logs = db.query(models.FuelLog).filter(models.FuelLog.fleet_id == fleet_id).order_by(models.FuelLog.log_date.desc()).all()
    return logs