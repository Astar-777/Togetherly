import string
import random

from sqlalchemy.orm import Session

from app.models.room import Room
from app.models.room_member import RoomMember
from app.models.user import User


def generate_join_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


class RoomService:

    @staticmethod
    def create_room(db: Session, user: User, name: str) -> Room:
        join_code = generate_join_code()

        room = Room(
            name=name,
            owner_id=user.id,
            join_code=join_code
        )

        db.add(room)
        db.commit()
        db.refresh(room)

        membership = RoomMember(
            room_id=room.id,
            user_id=user.id,
            role="Owner"
        )

        db.add(membership)
        db.commit()

        return room
    
    @staticmethod
    def join_room(db: Session, user: User, join_code: str) -> Room:
        room = db.query(Room).filter(Room.join_code == join_code).first()

        if not room:
            raise ValueError("Invalid join code")
        
        existing = db.query(RoomMember).filter(
            RoomMember.room_id == room.id,
            RoomMember.user_id == user.id
        ).first()

        if existing:
            return room
        
        membership = RoomMember(
            room_id=room.id,
            user_id=user.id,
        )

        db.add(membership)
        db.commit()

        return room
    
    @staticmethod
    def get_room(db: Session, user: User, room_id: int) -> Room:
        room = db.query(Room).filter(Room.id == room_id).first()

        if not Room:
            raise ValueError("Room not found")  
        
        membership = db.query(RoomMember).filter(
            RoomMember.room_id == room.id,
            RoomMember.user_id == user.id
        ).first()

        if not membership:
            raise ValueError("User is not a member of this room")
        
        return room
