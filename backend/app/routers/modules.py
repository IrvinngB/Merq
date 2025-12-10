from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleResponse
from app.services.module_service import ModuleService

router = APIRouter(prefix="/courses/{course_id}/modules", tags=["modules"])


@router.get("/", response_model=list[ModuleResponse])
def get_modules(course_id: int, db: Session = Depends(get_db)):
    service = ModuleService(db)
    return service.get_by_course(course_id)


@router.get("/{module_id}", response_model=ModuleResponse)
def get_module(course_id: int, module_id: int, db: Session = Depends(get_db)):
    service = ModuleService(db)
    module = service.get_by_id(module_id)
    if not module or module.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return module


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(course_id: int, data: ModuleCreate, db: Session = Depends(get_db)):
    service = ModuleService(db)
    return service.create(
        title=data.title,
        description=data.description,
        course_id=course_id,
    )


@router.patch("/{module_id}", response_model=ModuleResponse)
def update_module(course_id: int, module_id: int, data: ModuleUpdate, db: Session = Depends(get_db)):
    service = ModuleService(db)
    module = service.get_by_id(module_id)
    if not module or module.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return service.update(module_id, **data.model_dump(exclude_unset=True))


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(course_id: int, module_id: int, db: Session = Depends(get_db)):
    service = ModuleService(db)
    module = service.get_by_id(module_id)
    if not module or module.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    service.delete(module_id)
