from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.security.auth import get_current_user, check_permission
from app.utils.export import export_to_excel
from app.models.user import User

router = APIRouter(prefix="/export", tags=["数据导出"])

EXPORT_TYPES = ["collection", "disease", "restoration", "patrol", "transfer", "user"]

@router.get("/{export_type}")
async def export_data(
    export_type: str,
    desensitize: bool = Query(False, description="是否脱敏导出"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("data_export"))
):
    if export_type not in EXPORT_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的导出类型，支持的类型: {', '.join(EXPORT_TYPES)}")
    
    excel_data = export_to_excel(db, export_type, desensitize)
    
    filename = f"{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    if desensitize:
        filename = f"desensitized_{filename}"
    
    return StreamingResponse(
        iter([excel_data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )