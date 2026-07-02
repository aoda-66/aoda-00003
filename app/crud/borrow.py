from sqlalchemy.orm import Session
from app.models.borrow import Borrow
from app.models.borrow_approval import BorrowApproval
from app.models.collection import Collection
from app.models.user import User, Role
from app.schemas.borrow import BorrowCreate, BorrowUpdate, BorrowApprovalUpdate
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import and_

def generate_borrow_code(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Borrow).filter(Borrow.borrow_code.like(f"BR{today}%")).count() + 1
    return f"BR{today}{str(count).zfill(4)}"

def get_borrow(db: Session, borrow_id: int) -> Optional[Borrow]:
    return db.query(Borrow).filter(Borrow.id == borrow_id).first()

def get_borrow_by_code(db: Session, borrow_code: str) -> Optional[Borrow]:
    return db.query(Borrow).filter(Borrow.borrow_code == borrow_code).first()

def get_borrows(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    borrower_id: Optional[int] = None,
    collection_id: Optional[int] = None,
    is_overdue: Optional[bool] = None
) -> List[Borrow]:
    query = db.query(Borrow)
    
    if status:
        query = query.filter(Borrow.status == status)
    if borrower_id:
        query = query.filter(Borrow.borrower_id == borrower_id)
    if collection_id:
        query = query.filter(Borrow.collection_id == collection_id)
    if is_overdue is not None:
        query = query.filter(Borrow.is_overdue == is_overdue)
    
    return query.order_by(Borrow.created_at.desc()).offset(skip).limit(limit).all()

def get_pending_approvals(db: Session, approver_id: int) -> List[Borrow]:
    approvals = db.query(BorrowApproval).filter(
        and_(
            BorrowApproval.approver_id == approver_id,
            BorrowApproval.status == BorrowApproval.STATUS_PENDING
        )
    ).all()
    borrow_ids = [a.borrow_id for a in approvals]
    return db.query(Borrow).filter(Borrow.id.in_(borrow_ids)).order_by(Borrow.created_at.desc()).all()

def create_borrow(db: Session, borrow: BorrowCreate, borrower_id: int) -> Borrow:
    db_borrow = Borrow(
        **borrow.dict(),
        borrow_code=generate_borrow_code(db),
        borrower_id=borrower_id
    )
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    
    create_approval_flow(db, db_borrow.id)
    
    return db_borrow

def create_approval_flow(db: Session, borrow_id: int):
    approval_levels = [
        {"level": 1, "role_name": "文物管理员"},
        {"level": 2, "role_name": "管理员"}
    ]
    
    for level_info in approval_levels:
        role = db.query(Role).filter(Role.name == level_info["role_name"]).first()
        if role and role.users:
            approver = role.users[0]
            db_approval = BorrowApproval(
                borrow_id=borrow_id,
                approver_id=approver.id,
                approval_level=level_info["level"],
                status=BorrowApproval.STATUS_PENDING
            )
            db.add(db_approval)
    
    db.commit()

def get_current_approval_level(db: Session, borrow_id: int) -> Optional[int]:
    borrow = get_borrow(db, borrow_id)
    if not borrow:
        return None
    
    pending_approvals = db.query(BorrowApproval).filter(
        and_(
            BorrowApproval.borrow_id == borrow_id,
            BorrowApproval.status == BorrowApproval.STATUS_PENDING
        )
    ).order_by(BorrowApproval.approval_level).first()
    
    if pending_approvals:
        return pending_approvals.approval_level
    
    return None

def get_next_approver(db: Session, borrow_id: int) -> Optional[User]:
    borrow = get_borrow(db, borrow_id)
    if not borrow:
        return None
    
    pending_approvals = db.query(BorrowApproval).filter(
        and_(
            BorrowApproval.borrow_id == borrow_id,
            BorrowApproval.status == BorrowApproval.STATUS_PENDING
        )
    ).order_by(BorrowApproval.approval_level).first()
    
    if pending_approvals:
        return db.query(User).filter(User.id == pending_approvals.approver_id).first()
    
    return None

def update_borrow(db: Session, borrow_id: int, borrow_update: BorrowUpdate) -> Optional[Borrow]:
    db_borrow = get_borrow(db, borrow_id)
    if not db_borrow:
        return None
    
    for key, value in borrow_update.dict(exclude_unset=True).items():
        setattr(db_borrow, key, value)
    
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def delete_borrow(db: Session, borrow_id: int) -> bool:
    db_borrow = get_borrow(db, borrow_id)
    if not db_borrow:
        return False
    db.delete(db_borrow)
    db.commit()
    return True

def get_borrow_approvals(db: Session, borrow_id: int) -> List[BorrowApproval]:
    return db.query(BorrowApproval).filter(
        BorrowApproval.borrow_id == borrow_id
    ).order_by(BorrowApproval.approval_level).all()

def approve_borrow(db: Session, borrow_id: int, approver_id: int, approval_update: BorrowApprovalUpdate) -> Optional[BorrowApproval]:
    approval = db.query(BorrowApproval).filter(
        and_(
            BorrowApproval.borrow_id == borrow_id,
            BorrowApproval.approver_id == approver_id,
            BorrowApproval.status == BorrowApproval.STATUS_PENDING
        )
    ).first()
    
    if not approval:
        return None
    
    approval.status = approval_update.status
    approval.comment = approval_update.comment
    approval.approved_at = datetime.now()
    db.commit()
    db.refresh(approval)
    
    update_borrow_status_after_approval(db, borrow_id)
    
    return approval

def update_borrow_status_after_approval(db: Session, borrow_id: int):
    borrow = get_borrow(db, borrow_id)
    if not borrow:
        return
    
    approvals = get_borrow_approvals(db, borrow_id)
    
    if any(a.status == BorrowApproval.STATUS_REJECTED for a in approvals):
        borrow.status = Borrow.STATUS_REJECTED
    elif all(a.status == BorrowApproval.STATUS_APPROVED for a in approvals):
        borrow.status = Borrow.STATUS_APPROVED
    else:
        borrow.status = Borrow.STATUS_PENDING
    
    db.commit()
    db.refresh(borrow)

def confirm_borrow(db: Session, borrow_id: int) -> Optional[Borrow]:
    borrow = get_borrow(db, borrow_id)
    if not borrow or borrow.status != Borrow.STATUS_APPROVED:
        return None
    
    borrow.status = Borrow.STATUS_BORROWED
    borrow.borrow_date = datetime.now()
    db.commit()
    db.refresh(borrow)
    return borrow

def return_borrow(db: Session, borrow_id: int) -> Optional[Borrow]:
    borrow = get_borrow(db, borrow_id)
    if not borrow or borrow.status not in [Borrow.STATUS_BORROWED, Borrow.STATUS_OVERDUE]:
        return None
    
    borrow.status = Borrow.STATUS_RETURNED
    borrow.actual_return_date = datetime.now()
    borrow.is_overdue = False
    borrow.overdue_days = 0
    db.commit()
    db.refresh(borrow)
    return borrow

def check_overdue(db: Session) -> List[Borrow]:
    now = datetime.now()
    borrowed_borrows = db.query(Borrow).filter(
        Borrow.status == Borrow.STATUS_BORROWED
    ).all()
    
    overdue_list = []
    for borrow in borrowed_borrows:
        if borrow.planned_return_date < now:
            overdue_days = (now - borrow.planned_return_date).days
            borrow.is_overdue = True
            borrow.overdue_days = overdue_days
            borrow.status = Borrow.STATUS_OVERDUE
            overdue_list.append(borrow)
    
    if overdue_list:
        db.commit()
    
    return overdue_list

def get_overdue_report(db: Session) -> List[Borrow]:
    return db.query(Borrow).filter(
        Borrow.is_overdue == True
    ).order_by(Borrow.overdue_days.desc()).all()

def get_upcoming_reminders(db: Session, days_before: int = 3) -> List[Borrow]:
    now = datetime.now()
    reminder_date = now + timedelta(days=days_before)
    
    return db.query(Borrow).filter(
        and_(
            Borrow.status == Borrow.STATUS_BORROWED,
            Borrow.planned_return_date <= reminder_date,
            Borrow.planned_return_date > now,
            Borrow.reminder_sent == False
        )
    ).order_by(Borrow.planned_return_date).all()

def mark_reminder_sent(db: Session, borrow_id: int) -> bool:
    borrow = get_borrow(db, borrow_id)
    if not borrow:
        return False
    borrow.reminder_sent = True
    db.commit()
    return True