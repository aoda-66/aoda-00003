from app.core.database import SessionLocal, engine
from app.models.user import User, Role, Permission
from app.crud.user import create_role, create_permission, create_user, assign_permission_to_role
from app.schemas.user import UserCreate, RoleCreate, PermissionCreate

PERMISSIONS = [
    {"name": "用户创建", "code": "user_create"},
    {"name": "用户查看", "code": "user_view"},
    {"name": "用户编辑", "code": "user_edit"},
    {"name": "用户删除", "code": "user_delete"},
    {"name": "藏品创建", "code": "collection_create"},
    {"name": "藏品查看", "code": "collection_view"},
    {"name": "藏品编辑", "code": "collection_edit"},
    {"name": "藏品删除", "code": "collection_delete"},
    {"name": "病害创建", "code": "disease_create"},
    {"name": "病害查看", "code": "disease_view"},
    {"name": "病害编辑", "code": "disease_edit"},
    {"name": "病害删除", "code": "disease_delete"},
    {"name": "修复创建", "code": "restoration_create"},
    {"name": "修复查看", "code": "restoration_view"},
    {"name": "修复编辑", "code": "restoration_edit"},
    {"name": "修复删除", "code": "restoration_delete"},
    {"name": "巡护创建", "code": "patrol_create"},
    {"name": "巡护查看", "code": "patrol_view"},
    {"name": "巡护编辑", "code": "patrol_edit"},
    {"name": "巡护删除", "code": "patrol_delete"},
    {"name": "影像上传", "code": "image_upload"},
    {"name": "影像查看", "code": "image_view"},
    {"name": "影像编辑", "code": "image_edit"},
    {"name": "影像删除", "code": "image_delete"},
    {"name": "流转创建", "code": "transfer_create"},
    {"name": "流转查看", "code": "transfer_view"},
    {"name": "流转编辑", "code": "transfer_edit"},
    {"name": "流转删除", "code": "transfer_delete"},
    {"name": "数据导出", "code": "data_export"},
    {"name": "扫描控制", "code": "scan_control"},
    {"name": "扫描执行", "code": "scan_perform"},
    {"name": "扫描查看", "code": "scan_view"},
]

ROLES = [
    {
        "name": "管理员",
        "description": "系统管理员，拥有所有权限",
        "permissions": [p["code"] for p in PERMISSIONS]
    },
    {
        "name": "文物管理员",
        "description": "文物管理员，负责藏品管理",
        "permissions": [
            "collection_create", "collection_view", "collection_edit", "collection_delete",
            "disease_create", "disease_view", "disease_edit",
            "image_upload", "image_view", "image_edit",
            "data_export"
        ]
    },
    {
        "name": "修复师",
        "description": "文物修复师，负责修复工作",
        "permissions": [
            "restoration_create", "restoration_view", "restoration_edit",
            "disease_view", "image_upload", "image_view"
        ]
    },
    {
        "name": "巡护员",
        "description": "文物巡护员，负责巡护工作",
        "permissions": [
            "patrol_create", "patrol_view", "patrol_edit",
            "collection_view", "disease_view"
        ]
    },
    {
        "name": "普通用户",
        "description": "普通用户，仅可查看公开藏品",
        "permissions": ["collection_view"]
    }
]

def init_permissions(db):
    for perm in PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == perm["code"]).first()
        if not existing:
            create_permission(db, PermissionCreate(**perm))

def init_roles(db):
    for role_data in ROLES:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = create_role(db, RoleCreate(name=role_data["name"], description=role_data["description"]))
            for perm_code in role_data["permissions"]:
                perm = db.query(Permission).filter(Permission.code == perm_code).first()
                if perm:
                    assign_permission_to_role(db, role.id, perm.id)

def init_admin(db):
    existing = db.query(User).filter(User.username == "admin").first()
    if not existing:
        admin_role = db.query(Role).filter(Role.name == "管理员").first()
        create_user(db, UserCreate(
            username="admin",
            password="admin123",
            real_name="管理员",
            email="admin@museum.com",
            role_id=admin_role.id if admin_role else None
        ))
        db.commit()
        
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            admin_user.is_admin = True
            db.commit()

def main():
    from app import init_db
    init_db()
    
    db = SessionLocal()
    try:
        print("初始化权限...")
        init_permissions(db)
        
        print("初始化角色...")
        init_roles(db)
        
        print("初始化管理员用户...")
        init_admin(db)
        
        print("初始化完成！")
        print("默认管理员账号: admin/admin123")
    finally:
        db.close()

if __name__ == "__main__":
    main()