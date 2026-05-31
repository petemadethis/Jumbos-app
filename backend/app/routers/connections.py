"""
Jumbos - Connections Routes
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Connection, ConnectionStatus
from app.schemas import ConnectionRequest, ConnectionResponse
from app.dependencies import get_current_user, require_premium

router = APIRouter(prefix="/api/v1/connections", tags=["Connections"])


@router.get("/", response_model=list[ConnectionResponse])
def list_connections(
    status_filter: str = "accepted",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List connections for the current user."""
    try:
        status_enum = ConnectionStatus(status_filter)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

    connections = db.query(Connection).filter(
        or_(
            Connection.requester_id == current_user.id,
            Connection.addressee_id == current_user.id,
        ),
        Connection.status == status_enum,
    ).order_by(Connection.created_at.desc()).all()

    return [ConnectionResponse.model_validate(c) for c in connections]


@router.post("/request", response_model=ConnectionResponse, status_code=201)
def request_connection(
    req: ConnectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a connection request to another user."""
    if current_user.id == req.addressee_id:
        raise HTTPException(status_code=400, detail="Cannot connect with yourself")

    target = db.query(User).filter(User.id == req.addressee_id, User.is_active == True).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Check existing connection
    existing = db.query(Connection).filter(
        or_(
            (Connection.requester_id == current_user.id) & (Connection.addressee_id == req.addressee_id),
            (Connection.requester_id == req.addressee_id) & (Connection.addressee_id == current_user.id),
        )
    ).first()
    if existing:
        if existing.status == ConnectionStatus.PENDING:
            raise HTTPException(status_code=409, detail="Connection request already pending")
        elif existing.status == ConnectionStatus.ACCEPTED:
            raise HTTPException(status_code=409, detail="Already connected")
        else:
            raise HTTPException(status_code=409, detail="Cannot request connection")

    conn = Connection(
        requester_id=current_user.id,
        addressee_id=req.addressee_id,
        status=ConnectionStatus.PENDING,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return ConnectionResponse.model_validate(conn)


@router.post("/{connection_id}/accept", response_model=ConnectionResponse)
def accept_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a pending connection request."""
    conn = db.query(Connection).filter(
        Connection.id == connection_id,
        Connection.addressee_id == current_user.id,
        Connection.status == ConnectionStatus.PENDING,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Pending connection not found")

    conn.status = ConnectionStatus.ACCEPTED
    db.commit()
    db.refresh(conn)
    return ConnectionResponse.model_validate(conn)


@router.delete("/{connection_id}", status_code=204)
def remove_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove or decline a connection."""
    conn = db.query(Connection).filter(
        Connection.id == connection_id,
        or_(
            Connection.requester_id == current_user.id,
            Connection.addressee_id == current_user.id,
        ),
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    db.delete(conn)
    db.commit()