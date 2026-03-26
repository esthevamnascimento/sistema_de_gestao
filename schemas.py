from pydantic import BaseModel
from datetime import date
from typing import Optional

# --- Schemas para EPI ---

class EPICreate(BaseModel):
    name: str
    ca_number: str
    ca_validity_date: date # Nome sincronizado com o models.py

class EPIResponse(EPICreate):
    id: int
    is_expired: Optional[bool] = False # Campo auxiliar para o Dashboard

    class Config:
        orm_mode = True

class EPIAssignmentCreate(BaseModel):
    employee_name: str
    epi_id: int
    withdrawal_date: date


# --- Schemas para Frotas ---

class FleetCreate(BaseModel):
    plate: str
    model: str
    current_km: float
    last_maintenance_date: date
    next_maintenance_date: date
    maintenance_type: str # Corrigido: com o 'n' de manutenção

class FleetResponse(FleetCreate):
    id: int
    maintenance_alert: Optional[bool] = False

    class Config:
        orm_mode = True

class FleetUpdateKM(BaseModel):
    new_km: float

    # --- Adicione junto aos schemas de Frotas ---
class FuelLogCreate(BaseModel):
    log_date: date
    liters: float
    total_cost: float
    km_at_fill: float

class FuelLogResponse(FuelLogCreate):
    id: int
    fleet_id: int

    class Config:
        orm_mode = True


# --- Schemas para Estoque ---

class InventoryCreate(BaseModel):
    material_code: str
    name: str
    material_type: str
    quantity: int

class InventoryResponse(InventoryCreate):
    id: int

    class Config:
        orm_mode = True

class InventoryUpdateQuantity(BaseModel):
    quantity_change: int # Valores positivos (entrada) e negativos (saída)

from typing import Optional 

class InventoryLogCreate(BaseModel):
    employee_id: Optional[int] = None # Opcional, pois "Entrada" de compra não tem funcionário
    log_date: date
    quantity_changed: int
    action_type: str

class InventoryLogResponse(InventoryLogCreate):
    id: int
    inventory_id: int
    employee_name: Optional[str] = None # Para mostrar o nome na tela em vez de só o ID

    class Config:
        from_attributes = True


# --- Schemas para Equipamentos (Manômetros) ---

class EquipmentCreate(BaseModel):
    serial_number: str
    code: str
    calibration_date: date
    due_date: date

class EquipmentResponse(EquipmentCreate):
    id: int
    is_expired: Optional[bool] = False

    class Config:
        orm_mode = True
        
class EquipmentRecalibrate(BaseModel):
    calibration_date: date
    due_date: date


# --- Schemas para Funcionários ---
class EmployeeCreate(BaseModel):
    name: str
    employee_code: str
    cpf: str
    role: str
    admission_date: date
    phone: str
    aso_date: Optional[date] = None
    nr12_date: Optional[date] = None
    nr13_date: Optional[date] = None
    nr35_date: Optional[date] = None
    ficha_epi_date: Optional[date] = None

class EmployeeResponse(EmployeeCreate):
    id: int
    class Config:
        orm_mode = True
class EmployeeUpdateDocs(BaseModel):
    aso_date: Optional[date] = None
    nr12_date: Optional[date] = None
    nr13_date: Optional[date] = None
    nr35_date: Optional[date] = None
    ficha_epi_date: Optional[date] = None

class EmployeeResponse(EmployeeCreate):
    id: int
    class Config:
        orm_mode = True

# --- Schemas para Pedidos de EPI ---
from typing import Optional

class EPIRequestCreate(BaseModel):
    employee_id: int
    epi_description: str
    request_date: date

class EPIRequestResponse(EPIRequestCreate):
    id: int
    status: str
    employee_name: Optional[str] = None # Para mostrar o nome do funcionário na tela

    class Config:
        from_attributes = True

# Regras de Ferramentas
class ToolCreate(BaseModel):
    code: str
    name: str
    next_maintenance_date: date

class ToolResponse(ToolCreate):
    id: int
    class Config:
        from_attributes = True

# Regras de SSM (Manutenção)
class SSMCreate(BaseModel):
    employee_id: int
    target_type: str
    target_id: int
    description: str
    request_date: date

class SSMResponse(SSMCreate):
    id: int
    status: str
    employee_name: Optional[str] = None
    target_name: Optional[str] = None # Para mostrar a placa do carro ou nome da ferramenta

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    role: str # 'admin' ou 'operador'

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        from_attributes = True

class UserPasswordReset(BaseModel):
    new_password: str

class UserRoleUpdate(BaseModel):
    role: str