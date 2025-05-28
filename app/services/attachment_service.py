from sqlalchemy.orm import Session
from app.models.schemas.attachment import AttachmentCreate, AttachmentUpdate, MultiAttachment, AttachmentBase, DeleteAttachment
from app.repositories.attachment_repository import AttachmentRepository

class AttachmentService:
    def __init__(self):
        self.repository = AttachmentRepository()
    
    def get(self, db: Session, *, id: int) -> AttachmentBase:
        return self.repository.get(db, id=id)
    
    def get_all_by_message_id(self, db: Session, *, message_id: str) -> MultiAttachment:
        return self.repository.get_all_by_message_id(db, message_id=message_id)
    
    def get_multi(self, db: Session, *, limit = 100, skip = 0) -> MultiAttachment:
        return self.repository.get_multi(db, limit=limit, skip=skip)
    
    def create(self, db: Session, *, obj_in) -> AttachmentBase:
        return self.repository.create(db, obj_in=obj_in)
    
    def update(self, db: Session, *, obj_in: AttachmentUpdate) -> AttachmentBase:
        db_obj = self.get(db, id=obj_in.id)
        if not db_obj:
            raise Exception("Attachment not found")
        
        # Update the fields of db_obj with the values from obj_in
        return self.repository.update(db, db_obj=db_obj, obj_in=obj_in)