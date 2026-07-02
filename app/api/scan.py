from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.security.auth import get_current_user, check_permission
from app.adapters.scanner import ScannerFactory
from app.crud.image import create_image
from app.schemas.image import ImageCreate
from app.models.user import User

router = APIRouter(prefix="/scan", tags=["三维扫描"])

@router.post("/connect")
async def connect_scanner(
    adapter_type: str = "mock",
    config: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(check_permission("scan_control"))
):
    try:
        adapter = ScannerFactory.get_adapter(adapter_type)
        result = adapter.connect(config or {})
        if result:
            return {"message": "扫描设备连接成功", "adapter_type": adapter_type}
        else:
            raise HTTPException(status_code=500, detail="扫描设备连接失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接失败: {str(e)}")

@router.post("/disconnect")
async def disconnect_scanner(
    adapter_type: str = "mock",
    current_user: User = Depends(check_permission("scan_control"))
):
    try:
        adapter = ScannerFactory.get_adapter(adapter_type)
        result = adapter.disconnect()
        if result:
            return {"message": "扫描设备断开成功"}
        else:
            raise HTTPException(status_code=500, detail="扫描设备断开失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"断开失败: {str(e)}")

@router.post("/{collection_id}")
async def perform_scan(
    collection_id: int,
    adapter_type: str = "mock",
    options: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("scan_perform"))
):
    try:
        adapter = ScannerFactory.get_adapter(adapter_type)
        
        if not adapter.get_status()["connected"]:
            adapter.connect({})
        
        scan_result = adapter.scan(collection_id, options)
        
        if scan_result.get("success"):
            image_create = ImageCreate(
                collection_id=collection_id,
                file_name=scan_result["file_name"],
                file_path=scan_result["file_path"],
                file_type="application/octet-stream",
                file_size=scan_result["file_size"],
                description=f"三维扫描数据 - {scan_result['scan_id']}"
            )
            
            create_image(db=db, image=image_create, uploaded_by=current_user.id)
            
            return {
                "message": "扫描完成",
                "scan_id": scan_result["scan_id"],
                "file_path": scan_result["file_path"],
                "point_count": scan_result["point_count"],
                "resolution": scan_result["resolution"]
            }
        else:
            raise HTTPException(status_code=500, detail=scan_result.get("message", "扫描失败"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"扫描失败: {str(e)}")

@router.get("/status")
async def get_scanner_status(
    adapter_type: str = "mock",
    current_user: User = Depends(check_permission("scan_view"))
):
    try:
        adapter = ScannerFactory.get_adapter(adapter_type)
        return adapter.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")