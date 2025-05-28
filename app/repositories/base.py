from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Callable
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, UUID4
from sqlalchemy.orm import Session
from sqlalchemy import text

ModelType = TypeVar("ModelType", bound=BaseModel)
MultiSchemaType = TypeVar("MultiSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
DeleteSchemaType = TypeVar("DeleteSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType, MultiSchemaType, DeleteSchemaType]):
    """
    Repositorio CRUD base con operaciones por defecto
    """
    def __init__(self):
        self.__tablename__ = self.__orig_bases__[0].__args__[0].__tablename__
        self.base_validator: Callable[[Any], ModelType] = self.__orig_bases__[0].__args__[0].model_validate
        self.multi_validator: Callable[[Any], MultiSchemaType] = self.__orig_bases__[0].__args__[3].model_validate
        self.delete_validator: Callable[[Any], DeleteSchemaType] = self.__orig_bases__[0].__args__[4].model_validate
    
    def get(self, db: Session, id: UUID4) -> ModelType:
        """
        Obtiene un registro por su ID usando un procedimiento almacenado
        """
        result = db.execute(
            text(f"SELECT * FROM get_{self.__tablename__}_by_id(:id)"),
            {"id": id}
        )
        db.commit()
        record = result.scalar()

        if not record:
            return None
    
        return self.base_validator(record)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 10
    ) -> MultiSchemaType:
        """
        Obtiene múltiples registros con paginación usando un procedimiento almacenado
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s(:limit, :skip)"),
            {"limit": limit, "skip": skip} 
        )
        db.commit()

        records = result.scalar()

        return self.multi_validator(records)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Crea un nuevo registro usando un procedimiento almacenado
        """
        obj_in_data = jsonable_encoder(obj_in)

        # Preparar parámetros para el procedimiento almacenado
        params = {k: v for k, v in obj_in_data.items() if v is not None}
        order_params = {k: params[k] if k in params else None for k in obj_in_data["ordered_params"]}
        
        # Construir la llamada al procedimiento
        param_names = ", ".join([f":{k}" for k in order_params.keys()])
        
        result = db.execute(
            text(f"SELECT * FROM create_{self.__tablename__}({param_names})"),
            order_params
        )
        db.commit()
        
        # El procedimiento debería devolver el registro creado
        record = result.scalar()

        if not record:
            raise Exception("Error creating record")

        obj_in_data["id"] = record["id"]
        obj_in_data["created_at"] = record["created_at"]
        return self.base_validator(obj_in_data)

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Actualiza un registro existente usando un procedimiento almacenado
        """
        update_data = jsonable_encoder(obj_in)
        
        # Incluir el ID en los parámetros
        params = {"id": db_obj.id}
        params.update({k: v for k, v in update_data.items() if v is not None})
        # Ordernar los parámetros según el esquema
        params = {k: params[k] if k in params else None for k in update_data["ordered_params"]}
        
        # Construir la llamada al procedimiento
        param_names = ", ".join([f":{k}" for k in params.keys()])

        try:
            result = db.execute(
                text(f"SELECT * FROM update_{self.__tablename__}({param_names})"),
                params
            )
            db.commit()
            
            # El procedimiento debería devolver el registro actualizado
            record = result.scalar()
            
            if not record:
                raise Exception("Error getting updated record")
            
            updated_obj = {}

            for key, value in jsonable_encoder(db_obj).items():
                if key not in params or params[key] is None:
                    updated_obj[key] = value
                else:
                    updated_obj[key] = params[key]
            
            return self.base_validator(updated_obj)
        except Exception as e:
            db.rollback()
            raise Exception(f"Error updating record: {e}")
        


    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Elimina un registro usando un procedimiento almacenado
        """
        result = db.execute(
            text(f"SELECT * FROM delete_{self.__tablename__}(:id)"),
            {"id": id}
        )
        db.commit()
        
        # El procedimiento debería devolver el registro eliminado
        record = result.scalar()
        return self.delete_validator(record)
    