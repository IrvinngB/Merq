from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username.lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, email: str, username: str, password: str, full_name: str, role: str = "student") -> User:
        hashed = hash_password(password)
        user = User(
            email=email,
            username=username.lower(),
            password=hashed,
            full_name=full_name,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def update(self, user_id: int, **kwargs) -> User | None:
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        if "password" in kwargs and kwargs["password"]:
            kwargs["password"] = hash_password(kwargs["password"])
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    def deactivate(self, user_id: int) -> User | None:
        return self.update(user_id, is_active=False)
