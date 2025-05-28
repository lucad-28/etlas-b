from typing import Union, List
from sqlalchemy.orm import Session
from app.models.schemas.message import MessageCreate, MessageUpdate, MultiMessage, MessageBase, DeleteMessage, MessageWithAttachment, ListMessage, ContentAi
from app.models.schemas.chat import ChatUpdate
from app.repositories.message_repository import MessageRepository
from .attachment_service import AttachmentService
from .scheme_service import SchemeService
from .chat_service import ChatService
from .prompt_sys_manager import PromptSysManager
from .iaclient import ChatGPTClient, ApiMessage
from app.config.config import settings
from app.utils.utils import content_ai_to_string


class MessageService:
    def __init__(self):
        self.repository = MessageRepository()
        self.scheme_service = SchemeService()
        self.attachment_service = AttachmentService()
        self.chat_service = ChatService()
    
    def get(self, db: Session, *, id: int) -> MessageBase:
        return self.repository.get(db, id=id)
    
    def get_by_user_id(self, db: Session, *, user_id: str) -> MultiMessage:
        return self.repository.get_by_user_id(db, user_id=user_id)
    
    def get_by_chat_id(self, db: Session, *, chat_id: str, limit: int = 10, skip: int = 0) -> MultiMessage:
        return self.repository.get_by_chat_id(db, chat_id=chat_id, limit=limit, skip=skip)
    
    def get_multi(self, db: Session, *, limit = 100, skip = 0) -> MultiMessage:
        return self.repository.get_multi(db, limit=limit, skip=skip)
    
    def get_all_with_attachments_by_chat_id(self, db: Session, *, chat_id: str) -> MultiMessage:
        return self.repository.get_all_with_attachments_by_chat_id(db, chat_id=chat_id)
    
    def create(self, db: Session, *, obj_in: MessageCreate) -> Union[MessageBase, MessageWithAttachment]:

        new_message = self.repository.create(db, obj_in=obj_in)
        if not new_message:
            raise Exception("Message not created")
        
        if (obj_in.attachments and len(obj_in.attachments) > 0):
            # Validate attachments
            new_message.attachments = []

            for attachment in obj_in.attachments:
                new_attachment = self.attachment_service.create(db, obj_in=attachment)
                if not new_attachment:
                    raise Exception("Attachment not created")
                new_message.attachments.append(new_attachment)

            return MessageWithAttachment(**new_message.model_dump(), attachments=new_message.attachments)
        
        return new_message
    
    def update(self, db: Session, *, obj_in: MessageUpdate) -> MessageBase:
        db_obj = self.get(db, id=obj_in.id)
        if not db_obj:
            raise Exception("Message not found")
        
        # Update the fields of db_obj with the values from obj_in
        return self.repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def send_message(self, db: Session, *, obj_in: MessageCreate) -> MessageBase:

        history_data = self.repository.get_full_messages_by_chat_id(db, chat_id=obj_in.chat_id)
        history: List[ApiMessage] = []
        print("History Data:", history_data.data)
        for message in history_data.data:
            history.append(
                ApiMessage(
                    role="assistant" if message.role == "ai"  else message.role,
                    content=message.content.content if message.role == "user" else content_ai_to_string(message.content),
                )
            )

        aiclient = ChatGPTClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.MODEL_NAME,
            conversion_history=history,
            base_prompt_json=PromptSysManager.load_prompt_template()
        )

        scheme = self.scheme_service.get_by_chat_id(db, chat_id=obj_in.chat_id).data[0]  
        if scheme:
            history = aiclient.initialize_conversation(scheme=scheme.content)
        else:
            history = aiclient.initialize_conversation()
        
        self.create(
            db=db,
            obj_in=MessageCreate(
                chat_id=obj_in.chat_id,
                role="user",
                content=obj_in.content,
            )
        )

        ai_response = aiclient.send_message(
            message=ApiMessage(
                role="user",
                content=obj_in.content.content,
            ),
            title= len(history) == 1
        )

        if ai_response.title:
            self.chat_service.update(
                db=db,
                obj_in=ChatUpdate(
                    id=obj_in.chat_id,
                    name_chat=ai_response.title
                )
            )

        ai_message = self.create(
            db=db,
            obj_in=MessageCreate(
                chat_id=obj_in.chat_id,
                role="ai",
                content=ContentAi(
                    content_analysis=ai_response.content_analysis,
                    content_comment=ai_response.content_comment,
                    content_code=ai_response.content_code,
                    content_executable_code=ai_response.content_executable_code,
                )
            )
        )

        return ai_message

    