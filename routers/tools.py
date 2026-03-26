from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/tool", tags=["Ferramentas"], dependencies=[Depends(get_current_user)])

@router.post("/", response_model=schemas.ToolResponse)
def create_tool(tool: schemas.ToolCreate, db: Session = Depends(get_db)):
    db_tool = db.query(models.Tool).filter(models.Tool.code == tool.code).first()
    if db_tool:
        raise HTTPException(status_code=400, detail="Código de ferramenta já existe.")
    new_tool = models.Tool(**tool.dict())
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    return new_tool

@router.get("/", response_model=list[schemas.ToolResponse])
def get_tools(db: Session = Depends(get_db)):
    return db.query(models.Tool).all()

@router.delete("/{tool_id}")
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Ferramenta não encontrada")
    db.delete(tool)
    db.commit()
    return {"message": "Ferramenta excluída"}