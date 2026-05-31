"""
Jumbos - Messages Routes
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Message, MessageStatus, Connection, ConnectionStatus
from app.schemas import MessageSendRequest, MessageResponse
from app.dependencies import get_current_user, require_premium

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


@router.get("/", response_model=list[MessageResponse])
def list_messages(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List messages for the current user (sent and received)."""
    messages = (
        db.query(Message)
        .filter(
            or_(
                Message.sender_id == current_user.id,
                Message.recipient_id == current_user.id,
            )
        )
        .order_by(Message.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return [MessageResponse.model_validate(m) for m in messages]


@router.get("/conversation/{other_user_id}", response_model=list[MessageResponse])
def get_conversation(
    other_user_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the conversation thread with another user."""
    messages = (
        db.query(Message)
        .filter(
            or_(
                (Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id),
                (Message.sender_id == other_user_id) & (Message.recipient_id == current_user.id),
            )
        )
        .order_by(Message.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return [MessageResponse.model_validate(m) for m in messages]


@router.post("/send", response_model=MessageResponse, status_code=201)
def send_message(
    req: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a direct message to another user.
    Both sender and recipient must be connected.
    """
    if current_user.id == req.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    # Verify recipient exists
    recipient = db.query(User).filter(User.id == req.recipient_id, User.is_active == True).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Check they are connected (accepted connection)
    connection = (
        db.query(Connection)
        .filter(
            or_(
                (Connection.requester_id == current_user.id) & (Connection.addressee_id == req.recipient_id),
                (Connection.requester_id == req.recipient_id) & (Connection.addressee_id == current_user.id),
            ),
            Connection.status == ConnectionStatus.ACCEPTED,
        )
        .first()
    )
    if not connection:
        raise HTTPException(
            status_code=403,
            detail="You must be connected with this user to send a message",
        )

    # Free users can only message their connections (already checked above)
    # Premium check for bulk/feature - not blocking basic messaging

    msg = Message(
        id=str(uuid.uuid4()),
        sender_id=current_user.id,
        recipient_id=req.recipient_id,
        subject=req.subject,
        body=req.body,
        status=MessageStatus.SENT,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return MessageResponse.model_validate(msg)


@router.patch("/{message_id}/read", response_model=MessageResponse)
def mark_as_read(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a message as read."""
    msg = db.query(Message).filter(
        Message.id == message_id,
        Message.recipient_id == current_user.id,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    from datetime import datetime, timezone
    msg.status = MessageStatus.READ
    msg.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(msg)
    return MessageResponse.model_validate(msg)


@router.get("/unread/count")
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get count of unread messages."""
    count = db.query(Message).filter(
        Message.recipient_id == current_user.id,
        Message.status != MessageStatus.READ,
    ).count()
    return {"unread_count": count}