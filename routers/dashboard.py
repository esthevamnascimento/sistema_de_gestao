from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc # <-- NOVO: adicionado o desc para o Ranking
from datetime import date
import models
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/dashboard", 
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    hoje = date.today()
    primeiro_dia_mes = hoje.replace(day=1)
    
    # Resumo de Funcionários
    total_funcionarios = db.query(models.Employee).count()
    funcionarios_vencidos = db.query(models.Employee).filter(
        or_(
            models.Employee.aso_date < hoje,
            models.Employee.nr12_date < hoje,
            models.Employee.nr13_date < hoje,
            models.Employee.nr35_date < hoje,
            models.Employee.ficha_epi_date < hoje,
        )
    ).count()
    
    # Resumo de EPIs
    total_epis = db.query(models.EPI).count()
    epis_vencidos = db.query(models.EPI).filter(models.EPI.ca_validity_date < hoje).count()
    pedidos_pendentes = db.query(models.EPIRequest).filter(models.EPIRequest.status == "Pendente").count()
    
    # Resumo de Frotas
    total_veiculos = db.query(models.Fleet).count()
    veiculos_manutencao = db.query(models.Fleet).filter(models.Fleet.next_maintenance_date <= hoje).count()
    gasto_combustivel = db.query(func.sum(models.FuelLog.total_cost)).filter(
        models.FuelLog.log_date >= primeiro_dia_mes
    ).scalar() or 0.0 
    
    # Resumo de Estoque e Equipamentos
    total_materiais = db.query(models.Inventory).count()
    estoque_baixo = db.query(models.Inventory).filter(models.Inventory.quantity <= 5).count()
    
    total_equipamentos = db.query(models.Equipment).count()
    equipamentos_vencidos = db.query(models.Equipment).filter(models.Equipment.due_date < hoje).count()

    # --- NOVO: Resumo de Ferramentas ---
    total_ferramentas = db.query(models.Tool).count()
    ferramentas_vencidas = db.query(models.Tool).filter(models.Tool.next_maintenance_date < hoje).count()

    # --- NOVO: Resumo de SSM (Chamados) ---
    ssms_pendentes = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.status == "Pendente").count()
    ssms_concluidas = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.status == "Concluído").count()

    # --- NOVO: RANKING DOS MAIS DEFEITUOSOS (Top 3) ---
    top_targets_query = db.query(
        models.MaintenanceRequest.target_type,
        models.MaintenanceRequest.target_id,
        func.count(models.MaintenanceRequest.id).label('total_ssm')
    ).group_by(
        models.MaintenanceRequest.target_type,
        models.MaintenanceRequest.target_id
    ).order_by(
        desc('total_ssm') # Ordena do que deu mais defeito para o menor
    ).limit(3).all() # Pega apenas os 3 primeiros

    top_problemas = []
    for t_type, t_id, total in top_targets_query:
        nome = "Desconhecido"
        # Traduz o ID no nome real do carro ou da ferramenta
        if t_type == "Frota":
            frota = db.query(models.Fleet).filter(models.Fleet.id == t_id).first()
            if frota: nome = f"{frota.model} ({frota.plate})"
        elif t_type == "Ferramenta":
            ferramenta = db.query(models.Tool).filter(models.Tool.id == t_id).first()
            if ferramenta: nome = ferramenta.name
            
        top_problemas.append({"nome": nome, "total": total})
    
    return {
        "funcionarios": {"total": total_funcionarios, "alertas": funcionarios_vencidos},
        "epis": {"total": total_epis, "alertas": epis_vencidos},
        "pedidos_epi": {"pendentes": pedidos_pendentes},
        "frotas": {"total": total_veiculos, "alertas": veiculos_manutencao, "gasto_mes": float(gasto_combustivel)},
        "estoque": {"total": total_materiais, "alertas": estoque_baixo},
        "equipamentos": {"total": total_equipamentos, "alertas": equipamentos_vencidos},
        "ferramentas": {"total": total_ferramentas, "alertas": ferramentas_vencidas}, # Enviando Ferramentas
        "ssm": {
            "pendentes": ssms_pendentes,
            "concluidas": ssms_concluidas,
            "top_problemas": top_problemas # Enviando o Ranking
        }
    }