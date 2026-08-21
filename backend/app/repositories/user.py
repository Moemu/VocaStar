from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    """Data access layer for user entities.

    Keeps write methods explicit and small; avoids leaking ORM details to
    service & API layers. All methods return domain objects or simple
    primitives to aid testing.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        通过用户名获得用户对象
        """
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱获得用户对象
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_addition_order(self, prefix: str) -> int:
        """Return next numeric order for auto-generated usernames.

        Args:
            prefix: Username prefix to count existing rows.
        Returns:
            The next sequence number (1-based). Safe if none exist.
        """
        user = await self.session.execute(select(func.count(User.id)).where(User.username.startswith(prefix)))
        total_users = user.scalar() or 0
        return total_users + 1

    async def create_user(
        self,
        username: str,
        password_hash: str,
        email: str,
        nickname: Optional[str] = None,
        role: UserRole = UserRole.user,
        is_active: bool = True,
    ) -> Optional[User]:
        """
        创建一个用户

        :param username: 用户名
        :param password_hash: 用户密码哈希
        :param email: 邮箱
        :param nickname: 昵称
        :param role: 用户角色(user/admin)
        :param is_active: 用户状态(激活/禁用)

        :raise IntegrityError: 用户名或邮箱已存在

        :return: 用户对象。失败则返回 None
        """

        user = User(
            username=username,
            password_hash=password_hash,
            email=email,
            nickname=nickname,
            role=role,
            is_active=is_active,
        )

        self.session.add(user)
        await self.session.commit()

        return user

    async def edit_info(
        self,
        user: User,
        nickname: Optional[str] = None,
        is_active: Optional[bool] = None,
        role: Optional[UserRole] = None,
        email: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> bool:
        """Edit mutable user fields in-place.

        Only provided (non-None) arguments update the entity. Commit is
        attempted immediately to minimize inconsistent session state.

        Returns:
            True if committed successfully; False when an IntegrityError
            (duplicate email/username) occurs.
        """
        if nickname is not None:
            user.nickname = nickname
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        if email is not None:
            user.email = email
        if avatar_url is not None:
            user.avatar_url = avatar_url

        try:
            await self.session.commit()
        except IntegrityError:
            return False

        return True

    async def change_password(self, user: User, new_password_hash: str):
        """
        修改用户密码

        :param user: 用户对象
        :param new_password_hash: 新密码哈希
        """
        user.password_hash = new_password_hash
        await self.session.commit()

    def _term_filter(self, course_date_column, term: str):
        """Internal helper producing a JSON term filter expression.

        Supports MySQL & SQLite; falls back to generic json path access for
        other dialects.
        """
        bind = self.session.get_bind()
        if bind.dialect.name == "mysql":
            return course_date_column.op("->>")("$.term") == term
        elif bind.dialect.name == "sqlite":
            return func.json_extract(course_date_column, "$.term") == term
        else:  # pragma: no cover
            return course_date_column["term"] == term

    async def delete_user(self, user: User):
        """
        删除用户

        :param user: 用户对象
        """
        await self.session.delete(user)
        await self.session.commit()

    async def update_last_login(self, user: User):
        """
        更新用户最后登录时间

        :param user: 用户对象
        """
        user.last_login_at = func.now()
        await self.session.commit()
