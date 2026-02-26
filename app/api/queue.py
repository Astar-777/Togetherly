from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.queue import QueueItemCreate, QueueItemResponse, MoveItemRequest
from app.services.queue_service import QueueService

router = APIRouter(prefix="/rooms/{room_id}/queue", tags=["queue"])


@router.get("", response_model=list[QueueItemResponse])
def get_queue(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return QueueService.get_queue(db, current_user, room_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    

@router.post("", response_model=QueueItemResponse)
def add_item(
    room_id: int,
    payload: QueueItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return QueueService.add_item(db, current_user, room_id, payload.title)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{item_id}/move", response_model=QueueItemResponse)
def move_item(
    room_id: int,
    item_id: int,
    payload: MoveItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return QueueService.move_item(db, current_user, room_id, item_id, payload.new_position)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{item_id}/delete")
def delete_item(
    room_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        QueueService.delete_item(db, current_user, room_id, item_id)
        return {"message": "Item deleted"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
