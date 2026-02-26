from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.rooms import RoomCreate, RoomJoin, RoomResponse
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/create", response_model=RoomResponse)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = RoomService.create_room(db, current_user, payload.name)
    return room


@router.post("/join", response_model=RoomResponse)
def join_room(
    payload: RoomJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        room = RoomService.join_room(db, current_user, payload.join_code)
        return room
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        room = RoomService.get_room(db, current_user, room_id)
        return room
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))   
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
