"""Tests for auth router."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.routers.auth.actions import (
    create_user_admin,
    get_current_user,
    login,
    logout,
    refresh_tokens,
    require_admin,
    user_to_read,
)
from src.routers.auth.dal import UserDAL
from src.routers.auth.enums import ADMIN_ROLE, USER_ROLE
from src.routers.auth.models import User
from src.routers.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserCreateResponse,
    UserRead,
)
from src.routers.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_password,
    hash_password,
    verify_password,
)


def make_user(uid=None, username="admin", role="admin", is_active=True):
    """Создать мок User."""
    u = MagicMock(spec=User)
    u.id = uid or uuid4()
    u.username = username
    u.role = role
    u.is_active = is_active
    u.password_hash = hash_password("secret")
    return u


class TestAuthSecurity:
    """Test auth security functions."""

    def test_hash_verify_password(self):
        """hash_password and verify_password work."""
        pw = "secret123"
        h = hash_password(pw)
        assert verify_password(pw, h) is True
        assert verify_password("wrong", h) is False

    def test_generate_password(self):
        """generate_password creates random password."""
        pw = generate_password()
        assert len(pw) == 12
        assert pw != generate_password()

    def test_create_decode_access_token(self):
        """create_access_token and decode_token work."""
        uid = uuid4()
        token = create_access_token(uid)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == str(uid)
        assert payload["type"] == "access"

    def test_create_decode_refresh_token(self):
        """create_refresh_token has type refresh."""
        uid = uuid4()
        token = create_refresh_token(uid)
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        """decode_token returns None for invalid token."""
        assert decode_token("invalid") is None


class TestAuthSchemas:
    """Test auth schemas."""

    def test_token_response(self):
        """TokenResponse schema."""
        r = TokenResponse(access_token="at", refresh_token="rt")
        assert r.token_type == "bearer"

    def test_login_request(self):
        """LoginRequest schema."""
        r = LoginRequest(username="u", password="p")
        assert r.username == "u"

    def test_user_create_role(self):
        """UserCreate validates role."""
        r = UserCreate(username="user1", role="user")
        assert r.role == "user"
        r2 = UserCreate(username="adm", role="admin")
        assert r2.role == "admin"


class TestUserDAL:
    """Test UserDAL."""

    @pytest.mark.asyncio
    async def test_get_by_username_none(self):
        """get_by_username returns None when not found."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = UserDAL(mock_session)
        result = await dal.get_by_username("unknown")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_none(self):
        """get_by_id returns None when not found."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = UserDAL(mock_session)
        result = await dal.get_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_create_user(self):
        """create adds user and returns it."""
        mock_session = MagicMock()
        mock_session.add = MagicMock()

        async def refresh(obj):
            obj.id = uuid4()

        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(side_effect=refresh)

        dal = UserDAL(mock_session)
        user = await dal.create("newuser", "hash", "user")
        assert user.username == "newuser"
        assert user.role == "user"
        assert user.password_hash == "hash"
        assert user.id is not None
        mock_session.add.assert_called_once()


class TestAuthActions:
    """Test auth actions."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """login returns tokens when credentials valid."""
        user = make_user()
        mock_session = AsyncMock()
        with (
            patch.object(UserDAL, "get_by_username", new_callable=AsyncMock, return_value=user),
            patch(
                "src.routers.auth.actions.RedisController.set",
                new_callable=AsyncMock,
                return_value=True,
            ),
        ):
            access, refresh, u = await login(mock_session, "admin", "secret")
            assert u is user
            assert len(access) > 0
            assert len(refresh) > 0
            assert decode_token(access)["type"] == "access"

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        """login raises 401 when user not found."""
        mock_session = AsyncMock()
        with patch.object(UserDAL, "get_by_username", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc:
                await login(mock_session, "unknown", "pass")
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """login raises 401 when password wrong."""
        user = make_user()
        user.password_hash = hash_password("correct")
        mock_session = AsyncMock()
        with patch.object(UserDAL, "get_by_username", new_callable=AsyncMock, return_value=user):
            with pytest.raises(HTTPException) as exc:
                await login(mock_session, "admin", "wrong")
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        """login raises 401 when user inactive."""
        user = make_user(is_active=False)
        mock_session = AsyncMock()
        with patch.object(UserDAL, "get_by_username", new_callable=AsyncMock, return_value=user):
            with pytest.raises(HTTPException) as exc:
                await login(mock_session, "admin", "secret")
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_success(self):
        """refresh_tokens returns new tokens."""
        user = make_user()
        refresh = create_refresh_token(user.id)
        mock_session = AsyncMock()
        with (
            patch(
                "src.routers.auth.actions.RedisController.get",
                new_callable=AsyncMock,
                return_value=str(user.id),
            ),
            patch(
                "src.routers.auth.actions.RedisController.delete",
                new_callable=AsyncMock,
                return_value=1,
            ),
            patch(
                "src.routers.auth.actions.RedisController.set",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch.object(UserDAL, "get_by_id", new_callable=AsyncMock, return_value=user),
        ):
            access, new_refresh, u = await refresh_tokens(mock_session, refresh)
            assert u is user
            assert len(access) > 0
            assert len(new_refresh) > 0

    @pytest.mark.asyncio
    async def test_refresh_token_expired(self):
        """refresh_tokens raises 401 when token not in Redis."""
        mock_session = AsyncMock()
        refresh = create_refresh_token(uuid4())
        with patch(
            "src.routers.auth.actions.RedisController.get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(HTTPException) as exc:
                await refresh_tokens(mock_session, refresh)
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self):
        """refresh_tokens raises 401 for invalid token."""
        mock_session = AsyncMock()
        with pytest.raises(HTTPException) as exc:
            await refresh_tokens(mock_session, "invalid-jwt")
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_logout(self):
        """logout deletes token from Redis."""
        with patch(
            "src.routers.auth.actions.RedisController.delete",
            new_callable=AsyncMock,
            return_value=1,
        ) as mock_del:
            await logout("some-token")
            mock_del.assert_called_once()

    @pytest.mark.asyncio
    async def test_logout_none(self):
        """logout with None does nothing."""
        with patch(
            "src.routers.auth.actions.RedisController.delete",
            new_callable=AsyncMock,
        ) as mock_del:
            await logout(None)
            mock_del.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """get_current_user returns user from payload."""
        user = make_user()
        payload = {"sub": str(user.id)}
        mock_session = AsyncMock()
        with patch.object(UserDAL, "get_by_id", new_callable=AsyncMock, return_value=user):
            u = await get_current_user(mock_session, payload)
            assert u is user

    @pytest.mark.asyncio
    async def test_get_current_user_no_sub(self):
        """get_current_user raises when no sub in payload."""
        mock_session = AsyncMock()
        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_session, {})
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_create_user_admin_success(self):
        """create_user_admin creates user with generated password."""
        mock_session = AsyncMock()
        admin_user = make_user(role="admin")
        with (
            patch.object(UserDAL, "get_by_username", new_callable=AsyncMock, return_value=None),
            patch.object(UserDAL, "create", new_callable=AsyncMock) as mock_create,
        ):
            mock_user = MagicMock()
            mock_user.id = uuid4()
            mock_user.username = "newuser"
            mock_user.role = "user"
            mock_create.return_value = mock_user

            result = await create_user_admin(
                mock_session,
                UserCreate(username="newuser", role="user"),
                admin_user,
            )
            assert isinstance(result, UserCreateResponse)
            assert result.username == "newuser"
            assert result.role == "user"
            assert len(result.password) >= 12

    @pytest.mark.asyncio
    async def test_create_user_admin_duplicate(self):
        """create_user_admin raises 400 when username exists."""
        mock_session = AsyncMock()
        admin_user = make_user(role="admin")
        existing = make_user(username="existing")
        with patch.object(
            UserDAL, "get_by_username", new_callable=AsyncMock, return_value=existing
        ):
            with pytest.raises(HTTPException) as exc:
                await create_user_admin(
                    mock_session,
                    UserCreate(username="existing", role="user"),
                    admin_user,
                )
            assert exc.value.status_code == 400

    def test_user_to_read(self):
        """user_to_read converts User to UserRead."""
        user = make_user()
        r = user_to_read(user)
        assert isinstance(r, UserRead)
        assert r.username == user.username
        assert r.role == user.role


class TestRequireAdmin:
    """Test require_admin."""

    def test_require_admin_ok(self):
        """require_admin passes for admin role."""
        user = MagicMock()
        user.role = ADMIN_ROLE
        require_admin(user)

    def test_require_admin_fails(self):
        """require_admin raises for non-admin role."""
        user = MagicMock()
        user.role = USER_ROLE
        with pytest.raises(HTTPException) as exc_info:
            require_admin(user)
        assert exc_info.value.status_code == 403


class TestAuthEndpoints:
    """Test auth API endpoints."""

    def test_login_200(self, client_with_mock_db):
        """POST /api/auth/login returns 200 with tokens."""
        with (
            patch(
                "src.routers.auth.router.login",
                new_callable=AsyncMock,
                return_value=("access-tok", "refresh-tok", MagicMock()),
            ),
        ):
            response = client_with_mock_db.post(
                "/api/auth/login",
                json={"username": "admin", "password": "secret"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "access-tok"
            assert data["refresh_token"] == "refresh-tok"
            assert data["token_type"] == "bearer"

    def test_login_401(self, client_with_mock_db):
        """POST /api/auth/login returns 401 on invalid credentials."""
        with (
            patch(
                "src.routers.auth.router.login",
                new_callable=AsyncMock,
                side_effect=HTTPException(status_code=401, detail="Неверный логин"),
            ),
        ):
            response = client_with_mock_db.post(
                "/api/auth/login",
                json={"username": "bad", "password": "wrong"},
            )
            assert response.status_code == 401

    def test_refresh_200(self, client_with_mock_db):
        """POST /api/auth/refresh returns 200 with new tokens."""
        with (
            patch(
                "src.routers.auth.router.refresh_tokens",
                new_callable=AsyncMock,
                return_value=("new-access", "new-refresh", MagicMock()),
            ),
        ):
            response = client_with_mock_db.post(
                "/api/auth/refresh",
                json={"refresh_token": "old-refresh"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "new-access"

    def test_logout_204(self, client_with_mock_db):
        """POST /api/auth/logout returns 204."""
        with patch(
            "src.routers.auth.router.logout",
            new_callable=AsyncMock,
        ):
            response = client_with_mock_db.post(
                "/api/auth/logout",
                json={"refresh_token": "tok"},
            )
            assert response.status_code == 204

    def test_me_200(self, client_with_mock_db):
        """GET /api/auth/me returns 200 when authenticated."""
        from src.main import app
        from src.routers.auth.dependencies import get_current_user_required

        user = make_user()

        async def override_user():
            return user

        app.dependency_overrides[get_current_user_required] = override_user
        try:
            response = client_with_mock_db.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer any"},
            )
            assert response.status_code == 200
            assert response.json()["username"] == "admin"
        finally:
            app.dependency_overrides.pop(get_current_user_required, None)

    def test_me_401_no_token(self, client_with_mock_db):
        """GET /api/auth/me returns 401 without token."""
        response = client_with_mock_db.get("/api/auth/me")
        assert response.status_code == 401

    def test_create_user_201(self, client_with_mock_db):
        """POST /api/auth/users returns 201 when admin creates user."""
        from src.main import app
        from src.routers.auth.dependencies import get_current_admin

        admin = make_user(role="admin")
        resp = UserCreateResponse(
            id=uuid4(),
            username="newuser",
            role="user",
            password="GenPass123!",
        )

        async def override_admin():
            return admin

        app.dependency_overrides[get_current_admin] = override_admin
        with patch(
            "src.routers.auth.router.create_user_admin",
            new_callable=AsyncMock,
            return_value=resp,
        ):
            try:
                response = client_with_mock_db.post(
                    "/api/auth/users",
                    json={"username": "newuser", "role": "user"},
                    headers={"Authorization": "Bearer admin-token"},
                )
                assert response.status_code == 201
                data = response.json()
                assert data["username"] == "newuser"
                assert "password" in data
            finally:
                app.dependency_overrides.pop(get_current_admin, None)
