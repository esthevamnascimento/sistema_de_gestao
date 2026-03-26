from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # NOVO: Define se é 'admin' ou 'operador'
    role = Column(String, default="operador")
    
class Fleet(Base):
    __tablename__ = 'fleets'
    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, unique=True, index=True)
    model = Column(String)
    current_km = Column(Float)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    maintenance_type = Column(String)
    
    # NOVO: Conecta o carro ao seu histórico de combustível
    fuel_logs = relationship("FuelLog", back_populates="fleet", cascade="all, delete-orphan")

class EPI(Base):
    __tablename__ = 'epis'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ca_number = Column(String, unique=True, index=True)
    ca_validity_date = Column(Date)

class EPIAssignment(Base):
    __tablename__ = 'epi_assignments'
    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String)
    epi_id = Column(Integer, ForeignKey('epis.id'))
    withdrawal_date = Column(Date)
    epi = relationship("EPI")

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, index=True)
    material_code = Column(String, unique=True, index=True)
    name = Column(String)
    material_type = Column(String)
    quantity = Column(Integer)
    
    # A linha de relacionamento fica AQUI, no Estoque!
    logs = relationship("InventoryLog", back_populates="inventory", cascade="all, delete-orphan")


class Equipment(Base):
    __tablename__ = "equipments"
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, index=True)
    code = Column(String, index=True)
    calibration_date = Column(Date)
    due_date = Column(Date)

class FuelLog(Base):
    __tablename__ = 'fuel_logs'
    id = Column(Integer, primary_key=True, index=True)
    fleet_id = Column(Integer, ForeignKey('fleets.id'))
    log_date = Column(Date)
    liters = Column(Float)
    total_cost = Column(Float)
    km_at_fill = Column(Float) # KM marcado na bomba

    fleet = relationship("Fleet", back_populates="fuel_logs")

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    employee_code = Column(String, unique=True, index=True) # Matrícula/Código
    cpf = Column(String, unique=True, index=True)
    role = Column(String) # Cargo (ex: Encanador, Motorista, Auxiliar)
    admission_date = Column(Date) # Data que entrou
    phone = Column(String) # Telefone de contato
    # NOVAS COLUNAS DE SEGURANÇA E SAÚDE (nullable=True porque nem todos têm todos os cursos)
    aso_date = Column(Date, nullable=True)
    nr12_date = Column(Date, nullable=True)
    nr13_date = Column(Date, nullable=True)
    nr35_date = Column(Date, nullable=True)
    ficha_epi_date = Column(Date, nullable=True)


class InventoryLog(Base):
    __tablename__ = 'inventory_logs'
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey('inventory.id'))
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True) # Pode ser nulo se for uma "Entrada" de compra
    log_date = Column(Date)
    quantity_changed = Column(Integer) # Quantos itens entraram ou saíram
    action_type = Column(String) # "ENTRADA" ou "SAÍDA"

    inventory = relationship("Inventory", back_populates="logs")
    employee = relationship("Employee") # Puxa os dados do funcionário

class EPIRequest(Base):
    __tablename__ = 'epi_requests'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    epi_description = Column(String) # Ex: "Bota Bico de PVC Tam 42"
    request_date = Column(Date)
    status = Column(String, default="Pendente") # Pendente ou Atendido

    # Conecta com a tabela de funcionários para puxar o nome depois
    employee = relationship("Employee")

class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # Ex: FUR-01 (Furadeira)
    name = Column(String)
    next_maintenance_date = Column(Date)

class MaintenanceRequest(Base):
    __tablename__ = 'maintenance_requests'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    target_type = Column(String) # Será "Frota" ou "Ferramenta"
    target_id = Column(Integer) # O ID do Carro ou da Ferramenta
    description = Column(String)
    request_date = Column(Date)
    status = Column(String, default="Pendente") # Pendente ou Concluído

    # Relacionamento para puxar o nome do funcionário
    employee = relationship("Employee")