from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.queue_item import QueueItem
from app.models.room_member import RoomMember
from app.models.user import User

from app.core.redis import redis_client
from app.core.exceptions import RateLimitError
import json


def check_rate_limit(user_id: int, room_id: int):
    key = f"rate:{user_id}:{room_id}"

    count = redis_client.incr(key)

    if count == 1:
        redis_client.expire(key, 60)

    if count > 5:
        raise RateLimitError("Rate limit exceeded")


class QueueService:

    @staticmethod
    def _ensure_member(db: Session, user: User, room_id: int):
        membership = db.query(RoomMember).filter(
            RoomMember.user_id == user.id,
            RoomMember.room_id == room_id
        ).first()

        if not membership:
            raise ValueError("Not a member of this room")
        
    @staticmethod
    def _lock_room_queue(db: Session, room_id: int):
        db.query(QueueItem).filter(
            QueueItem.room_id == room_id
        ).with_for_update().all()
            
    @staticmethod
    def get_queue(db: Session, user: User, room_id: int):
        QueueService._ensure_member(db, user, room_id)

        cache_key = f"queue:{room_id}"

        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        items = db.query(QueueItem).filter(
            QueueItem.room_id == room_id
        ).order_by(QueueItem.position).all()

        result = [
            {
                "id": item.id,
                "title": item.title,
                "position": item.position,
                "added_by": item.added_by
            }
            for item in items
        ]

        redis_client.setex(cache_key, 60, json.dumps(result))

        return result

    @staticmethod
    def add_item(db: Session, user: User, room_id: int, title: str):
        QueueService._ensure_member(db, user, room_id)
        QueueService._lock_room_queue(db, room_id)

        check_rate_limit(user.id, room_id)

        max_position = db.query(func.max(QueueItem.position)).filter(
            QueueItem.room_id == room_id
        ).scalar()

        next_position = (max_position or 0) + 1

        item = QueueItem(
            room_id=room_id,
            added_by=user.id,
            title=title,
            position=next_position
        )

        db.add(item)
        db.commit()
        redis_client.delete(f"queue:{room_id}")
        db.refresh(item)
        
        return item

    @staticmethod
    def move_item(db: Session, user: User, room_id: int, item_id: int, new_position: int):
        QueueService._ensure_member(db, user, room_id)
        QueueService._lock_room_queue(db, room_id)

        item = db.query(QueueItem).filter(
            QueueItem.id == item_id,
            QueueItem.room_id == room_id
        ).first()

        if not item:
            raise ValueError("Item not found")

        old_position = item.position

        if new_position == old_position:
            return item
        
        max_position = db.query(func.max(QueueItem.position)).filter(
            QueueItem.room_id == room_id
        ).scalar()

        if new_position < 1 or new_position > max_position:
            raise ValueError("Invalid new position")
        
        if new_position < old_position:
            db.query(QueueItem).filter(
                QueueItem.room_id == room_id,
                QueueItem.position >= new_position,
                QueueItem.position < old_position
            ).update(
                {QueueItem.position: QueueItem.position + 1},
                synchronize_session=False
            )

        else:
            db.query(QueueItem).filter(
                QueueItem.room_id == room_id,
                QueueItem.position > old_position,
                QueueItem.position <= new_position
            ).update(
                {QueueItem.position: QueueItem.position - 1},
                synchronize_session=False
            )

        item.position = new_position

        db.commit()
        redis_client.delete(f"queue:{room_id}")
        db.refresh(item)

        return item

    @staticmethod
    def delete_item(db: Session, user: User, room_id: int, item_id: int):
        QueueService._ensure_member(db, user, room_id)
        QueueService._lock_room_queue(db, room_id)

        item = db.query(QueueItem).filter(
            QueueItem.id == item_id,
            QueueItem.room_id == room_id
        ).first()

        if not item:
            raise ValueError("Item not found")
        
        deleted_position = item.position

        db.delete(item)

        db.query(QueueItem).filter(
            QueueItem.room_id == room_id,
            QueueItem.position > deleted_position
        ).update(
            {QueueItem.position: QueueItem.position - 1},
            synchronize_session=False
        )

        db.commit()
        redis_client.delete(f"queue:{room_id}")
