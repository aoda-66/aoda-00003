from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.crud.borrow import (
    get_borrow, get_borrows, get_borrow_by_code, get_borrow_approvals,
    create_borrow, approve_borrow, confirm_borrow, return_borrow,
    update_borrow, delete_borrow, get_pending_approvals,
    get_current_approval_level, get_next_approver,
    check_overdue, get_overdue_report, get_upcoming_reminders, mark_reminder_sent
)
from app.crud.user import get_user
from app.crud.collection import get_collection
from app.security.auth import check_permission
from app.schemas.borrow import (
    BorrowCreate, BorrowUpdate, BorrowResponse,
    BorrowApprovalResponse, BorrowApprovalUpdate,
    OverdueReportResponse, ReminderNotificationResponse
)
from app.models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/borrows", tags=["借阅管理"])

def build_borrow_response(db: Session, borrow) -> BorrowResponse:
    borrower_name = get_user(db, borrow.borrower_id).real_name if borrow.borrower_id else None
    collection = get_collection(db, borrow.collection_id)
    collection_name = collection.name if collection else None
    collection_code = collection.collection_code if collection else None
    current_level = get_current_approval_level(db, borrow.id)
    next_approver = get_next_approver(db, borrow.id)
    next_approver_name = next_approver.real_name if next_approver else None
    
    return BorrowResponse(
        id=borrow.id,
        borrow_code=borrow.borrow_code,
        collection_id=borrow.collection_id,
        collection_name=collection_name,
        collection_code=collection_code,
        borrower_id=borrow.borrower_id,
        borrower_name=borrower_name,
        borrow_date=borrow.borrow_date,
        planned_return_date=borrow.planned_return_date,
        actual_return_date=borrow.actual_return_date,
        status=borrow.status,
        purpose=borrow.purpose,
        remarks=borrow.remarks,
        overdue_days=borrow.overdue_days,
        is_overdue=borrow.is_overdue,
        reminder_sent=borrow.reminder_sent,
        current_approval_level=current_level,
        next_approver_name=next_approver_name,
        created_at=borrow.created_at,
        updated_at=borrow.updated_at
    )

@router.get("/", response_model=list[BorrowResponse])
async def read_borrows(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    borrower_id: Optional[int] = Query(None),
    collection_id: Optional[int] = Query(None),
    is_overdue: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_view"))
):
    borrows = get_borrows(db, skip=skip, limit=limit, status=status, 
                          borrower_id=borrower_id, collection_id=collection_id, is_overdue=is_overdue)
    return [build_borrow_response(db, b) for b in borrows]

@router.get("/{borrow_id}", response_model=BorrowResponse)
async def read_borrow(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_view"))
):
    borrow = get_borrow(db, borrow_id=borrow_id)
    if borrow is None:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    return build_borrow_response(db, borrow)

@router.post("/", response_model=BorrowResponse)
async def create_borrow_info(
    borrow: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_create"))
):
    collection = get_collection(db, borrow.collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="藏品不存在")
    
    active_borrow = get_borrows(db, collection_id=borrow.collection_id, status="borrowed")
    if active_borrow:
        raise HTTPException(status_code=400, detail="该藏品已被借阅")
    
    if borrow.planned_return_date <= borrow.borrow_date:
        raise HTTPException(status_code=400, detail="归还日期必须晚于借阅日期")
    
    result = create_borrow(db=db, borrow=borrow, borrower_id=current_user.id)
    return build_borrow_response(db, result)

@router.put("/{borrow_id}", response_model=BorrowResponse)
async def update_borrow_info(
    borrow_id: int,
    borrow_update: BorrowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_edit"))
):
    borrow = get_borrow(db, borrow_id=borrow_id)
    if borrow is None:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    
    result = update_borrow(db, borrow_id=borrow_id, borrow_update=borrow_update)
    return build_borrow_response(db, result)

@router.delete("/{borrow_id}")
async def delete_borrow_info(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_delete"))
):
    success = delete_borrow(db, borrow_id=borrow_id)
    if not success:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    return {"message": "删除成功"}

@router.get("/{borrow_id}/approvals", response_model=list[BorrowApprovalResponse])
async def read_borrow_approvals(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_view"))
):
    borrow = get_borrow(db, borrow_id=borrow_id)
    if borrow is None:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    
    approvals = get_borrow_approvals(db, borrow_id=borrow_id)
    return [
        BorrowApprovalResponse(
            id=a.id,
            borrow_id=a.borrow_id,
            approver_id=a.approver_id,
            approver_name=get_user(db, a.approver_id).real_name if a.approver_id else None,
            approval_level=a.approval_level,
            status=a.status,
            comment=a.comment,
            approved_at=a.approved_at,
            created_at=a.created_at
        )
        for a in approvals
    ]

@router.post("/{borrow_id}/approve")
async def approve_borrow_info(
    borrow_id: int,
    approval_update: BorrowApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_approve"))
):
    if approval_update.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="审批状态只能是approved或rejected")
    
    approval = approve_borrow(db, borrow_id=borrow_id, approver_id=current_user.id, 
                              approval_update=approval_update)
    if approval is None:
        raise HTTPException(status_code=400, detail="无待审批记录或无权限审批")
    
    borrow = get_borrow(db, borrow_id=borrow_id)
    return {
        "message": "审批成功",
        "approval": BorrowApprovalResponse(
            id=approval.id,
            borrow_id=approval.borrow_id,
            approver_id=approval.approver_id,
            approver_name=current_user.real_name,
            approval_level=approval.approval_level,
            status=approval.status,
            comment=approval.comment,
            approved_at=approval.approved_at,
            created_at=approval.created_at
        ),
        "borrow_status": borrow.status
    }

@router.post("/{borrow_id}/confirm")
async def confirm_borrow_info(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_confirm"))
):
    borrow = confirm_borrow(db, borrow_id=borrow_id)
    if borrow is None:
        raise HTTPException(status_code=400, detail="该借阅申请未通过审批，无法确认借阅")
    return {"message": "借阅确认成功", "borrow": build_borrow_response(db, borrow)}

@router.post("/{borrow_id}/return")
async def return_borrow_info(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_return"))
):
    borrow = return_borrow(db, borrow_id=borrow_id)
    if borrow is None:
        raise HTTPException(status_code=400, detail="该借阅记录无法归还")
    return {"message": "归还成功", "borrow": build_borrow_response(db, borrow)}

@router.get("/approvals/pending", response_model=list[BorrowResponse])
async def read_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_approve"))
):
    borrows = get_pending_approvals(db, approver_id=current_user.id)
    return [build_borrow_response(db, b) for b in borrows]

@router.get("/overdue/check", response_model=list[BorrowResponse])
async def check_overdue_borrows(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_view"))
):
    overdue_list = check_overdue(db)
    return [build_borrow_response(db, b) for b in overdue_list]

@router.get("/overdue/report", response_model=list[OverdueReportResponse])
async def read_overdue_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_view"))
):
    overdue_list = get_overdue_report(db)
    return [
        OverdueReportResponse(
            borrow_id=b.id,
            borrow_code=b.borrow_code,
            collection_name=get_collection(db, b.collection_id).name if b.collection_id else None,
            collection_code=get_collection(db, b.collection_id).collection_code if b.collection_id else None,
            borrower_name=get_user(db, b.borrower_id).real_name if b.borrower_id else None,
            borrow_date=b.borrow_date,
            planned_return_date=b.planned_return_date,
            actual_return_date=b.actual_return_date,
            overdue_days=b.overdue_days,
            status=b.status,
            created_at=b.created_at
        )
        for b in overdue_list
    ]

@router.get("/reminders/upcoming", response_model=list[ReminderNotificationResponse])
async def read_upcoming_reminders(
    days_before: int = Query(3, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_view"))
):
    reminders = get_upcoming_reminders(db, days_before=days_before)
    now = datetime.now()
    return [
        ReminderNotificationResponse(
            borrow_id=b.id,
            borrow_code=b.borrow_code,
            collection_name=get_collection(db, b.collection_id).name if b.collection_id else None,
            borrower_name=get_user(db, b.borrower_id).real_name if b.borrower_id else None,
            planned_return_date=b.planned_return_date,
            days_until_due=(b.planned_return_date - now).days,
            status=b.status
        )
        for b in reminders
    ]

@router.post("/{borrow_id}/reminder/sent")
async def mark_reminder_as_sent(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("borrow_edit"))
):
    success = mark_reminder_sent(db, borrow_id=borrow_id)
    if not success:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    return {"message": "提醒已标记为发送"}