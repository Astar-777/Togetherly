from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import func

from app.db.database import Base


class RoomMember(Base):
    __tablename__ = "room_members"

    id = Column(Integer, primary_key=True, index=True)

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    role = Column(String, nullable=False, default="member")

    joined_at = Column(DateTime(timezone=True), server_default=func.now())