from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.schemas.attachment import AttachmentCreate, AttachmentUpdate, MultiAttachment, AttachmentBase, DeleteAttachment
from app.repositories.base import BaseRepository

class AttachmentRepository(BaseRepository[AttachmentBase, AttachmentCreate, AttachmentUpdate, MultiAttachment, DeleteAttachment]):
    """
    Repositorio para operaciones específicas de adjuntos
    """    
    def get_all_by_message_id(self, db: Session, *, message_id: str) -> MultiAttachment:
        """
        Obtiene adjuntos por el ID de mensaje
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_by_message_id(:message_id)"),
            {"message_id": message_id}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    
    
    