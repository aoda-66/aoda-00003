from sqlalchemy.orm import Session
from app.models.user import User, Role, Permission
from app.schemas.user import UserCreate, UserUpdate, RoleCreate, PermissionCreate
from passlib.context import CryptContext
from typing import Optional, List

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()

def create_role(db: Session, role: RoleCreate) -> Role:
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: int, role_update: RoleCreate) -> Optional[Role]:
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    db_role.name = role_update.name
    db_role.description = role_update.description
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int) -> bool:
    db_role = get_role(db, role_id)
    if not db_role:
        return False
    db.delete(db_role)
    db.commit()
    return True

def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.id == permission_id).first()

def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.code == code).first()

def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    return db.query(Permission).offset(skip).limit(limit).all()

def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    db_permission = Permission(
        name=permission.name,
        code=permission.code,
        description=permission.description
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def assign_permission_to_role(db: Session, role_id: int, permission_id: int) -> bool:
    role = get_role(db, role_id)
    permission = get_permission(db, permission_id)
    if not role or not permission:
        return False
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
    return True

def remove_permission_from_role(db: Session, role_id: int, permission_id: int) -> bool:
    role = get_role(db, role_id)
    permission = get_permission(db, permission_id)
    if not role or not permission:
        return False
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.commit()
    return True