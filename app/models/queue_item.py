from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy import func

from app.db.database import Base


class QueueItem(Base):
    __tablename__ = "queue_items"

    id = Column(Integer, primary_key=True, index=True)

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    position = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index(
    "idx_queue_room_position",
    QueueItem.room_id,
    QueueItem.position
)

