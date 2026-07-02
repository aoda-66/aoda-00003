import pandas as pd
from io import BytesIO
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.collection import Collection
from app.models.disease import Disease
from app.models.restoration import Restoration
from app.models.patrol import Patrol
from app.models.transfer import Transfer
from app.models.user import User
from app.utils.desensitization import apply_desensitization

def export_to_excel(db: Session, export_type: str, desensitize: bool = False) -> bytes:
    try:
        buffer = BytesIO()
        
        if export_type == "collection":
            data = db.query(Collection).all()
            records = []
            for item in data:
                record = {
                    "藏品编号": item.collection_code,
                    "藏品名称": item.name,
                    "类别": item.category,
                    "年代": item.era,
                    "来源": item.origin,
                    "材质": item.material,
                    "尺寸": item.size,
                    "重量": item.weight,
                    "状况": item.condition,
                    "描述": item.description,
                    "位置": item.location,
                    "是否公开": "是" if item.is_public else "否",
                    "创建时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                    "更新时间": item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                }
                if desensitize:
                    record = apply_desensitization(record, "collection", db)
                records.append(record)
            
            df = pd.DataFrame(records)
            df.to_excel(buffer, index=False, sheet_name="藏品档案")
        
        elif export_type == "disease":
            data = db.query(Disease).all()
            records = []
            for item in data:
                record = {
                    "病害ID": item.id,
                    "藏品ID": item.collection_id,
                    "病害类型": item.disease_type,
                    "严重程度": item.severity,
                    "面积": item.area,
                    "位置": item.location,
                    "描述": item.description,
                    "记录人ID": item.recorded_by,
                    "创建时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                    "更新时间": item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                }
                if desensitize:
                    record = apply_desensitization(record, "disease", db)
                records.append(record)
            
            df = pd.DataFrame(records)
            df.to_excel(buffer, index=False, sheet_name="病害记录")
        
        elif export_type == "restoration":
            data = db.query(Restoration).all()
            records = []
            for item in data:
                record = {
                    "修复编号": item.restoration_code,
                    "藏品ID": item.collection_id,
                    "状态": item.status,
                    "描述": item.description,
                    "修复方法": item.method,
                    "使用材料": item.materials,
                    "修复前状况": item.before_condition,
                    "修复后状况": item.after_condition,
                    "操作人ID": item.operator_id,
                    "开始日期": item.start_date.strftime("%Y-%m-%d") if item.start_date else "",
                    "结束日期": item.end_date.strftime("%Y-%m-%d") if item.end_date else "",
                    "是否完成": "是" if item.is_completed else "否",
                    "创建时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                    "更新时间": item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                }
                if desensitize:
                    record = apply_desensitization(record, "restoration", db)
                records.append(record)
            
            df = pd.DataFrame(records)
            df.to_excel(buffer, index=False, sheet_name="修复记录")
        
        elif export_type == "patrol":
            data = db.query(Patrol).all()
            records = []
            for item in data:
                record = {
                    "巡护编号": item.patrol_code,
                    "藏品ID": item.collection_id,
                    "状态": item.status,
                    "检查结果": item.check_result,
                    "描述": item.description,
                    "巡护人ID": item.patrol_by,
                    "巡护日期": item.patrol_date.strftime("%Y-%m-%d") if item.patrol_date else "",
                    "是否正常": "是" if item.is_normal else "否",
                    "创建时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                    "更新时间": item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                }
                if desensitize:
                    record = apply_desensitization(record, "patrol", db)
                records.append(record)
            
            df = pd.DataFrame(records)
            df.to_excel(buffer, index=False, sheet_name="巡护记录")
        
        elif export_type == "transfer":
            data = db.query(Transfer).all()
            records = []
            for item in data:
                record = {
                    "流转编号": item.transfer_code,
                    "藏品ID": item.collection_id,
                    "流转类型": item.transfer_type,
                    "原位置": item.from_location,
                    "目标位置": item.to_location,
                    "状态": item.status,
                    "描述": item.description,
                    "操作人ID": item.operator_id,
                    "流转日期": item.transfer_date.strftime("%Y-%m-%d") if item.transfer_date else "",
                    "创建时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                    "更新时间": item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                }
                if desensitize:
                    record = apply_desensitization(record, "transfer", db)
                records.append(record)
            
            df = pd.DataFrame(records)
            df.to_excel(buffer, index=False, sheet_name="流转记录")
        
        elif export_type == "user":
            data = db.query(User).all()
            records = []
            for item in data:
                record = {
                    "用户ID": item.id,
                    "用户名": item.username,
                    "真实姓名": item.real_name,
                    "邮箱": item.email,
                    "电话": item.phone,
                    "角色ID": item.role_id,
                    "是否活跃": "是" if item.is_active else "否",
                    "是否管理员": "是" if item.is_admin else "否",
                    "创建时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                    "更新时间": item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                }
                if desensitize:
                    record = apply_desensitization(record, "user", db)
                records.append(record)
            
            df = pd.DataFrame(records)
            df.to_excel(buffer, index=False, sheet_name="用户档案")
        
        else:
            raise HTTPException(status_code=400, detail="不支持的导出类型")
        
        buffer.seek(0)
        return buffer.getvalue()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")