from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/employee", 
    tags=["Funcionários"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=schemas.EmployeeResponse)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Verifica se já existe a matrícula ou CPF
    db_emp = db.query(models.Employee).filter(
        (models.Employee.employee_code == employee.employee_code) | 
        (models.Employee.cpf == employee.cpf)
    ).first()
    
    if db_emp:
        raise HTTPException(status_code=400, detail="Código de funcionário ou CPF já cadastrado.")
        
    new_employee = models.Employee(**employee.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.get("/", response_model=list[schemas.EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@router.delete("/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    db.delete(emp)
    db.commit()
    return {"message": "Excluído com sucesso"}

@router.put("/{emp_id}/docs")
def update_employee_docs(emp_id: int, data: schemas.EmployeeUpdateDocs, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    # Atualiza as datas
    emp.aso_date = data.aso_date
    emp.nr12_date = data.nr12_date
    emp.nr13_date = data.nr13_date
    emp.nr35_date = data.nr35_date
    emp.ficha_epi_date = data.ficha_epi_date
    
    db.commit()
    db.refresh(emp)
    return {"message": "Documentos atualizados com sucesso"}