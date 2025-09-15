"""Test for Auth Service"""

from uuid import uuid4
import pytest
from unittest.mock import AsyncMock, patch, ANY
from fastapi import HTTPException

from src.common import UserType
from src.schemas.intern_schemas import InternOutModel
from src.schemas.supervisor_schemas import SupervisorOutModel
from src.services.auth_service import AuthService
from src.utils import TokenType
from tests.utils.utils import (
    create_mock_user,
    create_mock_intern,
    create_mock_supervisor,
    create_user_in_model,
    create_intern_in_model,
    create_supervisor_in_model,
    create_mock_verification_code,
)

pytestmark = pytest.mark.asyncio


class TestCreateUnverifiedNewUser:
    """Tests for the create_unverified_new_user method."""

    async def test_create_new_user_success(
        self,
        auth_service: AuthService,
        mock_user_repo: AsyncMock,
        mock_intern_repo: AsyncMock,
        mock_supervisor_repo: AsyncMock,
        mock_code_repo: AsyncMock,
    ):
        # Setup for a brand new user
        new_user_data = create_user_in_model()
        created_user_mock = create_mock_user(verified=False)

        mock_user_repo.get_user_by_email_or_phone.return_value = None
        mock_user_repo.create_new_user.return_value = created_user_mock

        result = await auth_service.create_unverified_new_user(new_user_data)

        # Verify the result
        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once_with(
            conn=auth_service.session,
            email=new_user_data.email,
            phone_number=new_user_data.phone_number,
        )
        mock_user_repo.create_new_user.assert_awaited_once_with(
            conn=auth_service.session,
            new_user=new_user_data,
            skill_repo=auth_service.skill_repo,
        )
        mock_intern_repo.create_new_intern.assert_not_awaited()  # Ensure intern repo is NOT called
        mock_supervisor_repo.create_new_supervisor.assert_not_awaited()  # Ensure supervisor repo is NOT called
        mock_code_repo.create_code.assert_awaited_once_with(
            conn=auth_service.session, user_id=created_user_mock.id, code=ANY
        )
        assert result == {"detail": "Verification code sent to email"}

    async def test_create_new_intern_success(
        self,
        auth_service: AuthService,
        mock_user_repo: AsyncMock,
        mock_intern_repo: AsyncMock,
        mock_supervisor_repo: AsyncMock,
        mock_code_repo: AsyncMock,
    ):
        # Setup for a brand new intern. This test covers the `isinstance` check.
        new_intern_data = create_intern_in_model()
        created_user_mock = create_mock_user(
            verified=False,
        )  # The repo returns a User object
        created_intern_mock = create_mock_intern(created_user_mock)
        mock_user_repo.get_user_by_email_or_phone.return_value = None
        mock_user_repo.create_new_user.return_value = created_user_mock
        mock_intern_repo.create_new_intern.return_value = created_intern_mock
        # Call the service method
        result = await auth_service.create_unverified_new_user(new_intern_data)

        # Verify the result
        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once_with(
            conn=auth_service.session,
            email=new_intern_data.email,
            phone_number=new_intern_data.phone_number,
        )
        mock_user_repo.create_new_user.assert_awaited_once_with(
            conn=auth_service.session,
            new_user=new_intern_data,
            skill_repo=auth_service.skill_repo,
        )
        mock_intern_repo.create_new_intern.assert_awaited_once_with(
            conn=auth_service.session,
            new_intern=new_intern_data,
            user=created_user_mock,
        )
        mock_supervisor_repo.create_new_supervisor.assert_not_awaited()  # Ensure supervisor repo's create is NOT called
        mock_code_repo.create_code.assert_awaited_once_with(
            conn=auth_service.session, user_id=created_intern_mock.id, code=ANY
        )
        assert result == {"detail": "Verification code sent to email"}

    async def test_create_new_supervisor_success(
        self,
        auth_service,
        mock_user_repo,
        mock_intern_repo,
        mock_supervisor_repo,
        mock_code_repo,
    ):
        # Setup for a brand new intern. This test covers the `isinstance` check.
        new_supervisor_data = create_supervisor_in_model()
        created_user_mock = create_mock_user(
            verified=False,
        )  # The repo returns a User object
        created_supervisor_mock = create_mock_supervisor(created_user_mock)
        mock_user_repo.get_user_by_email_or_phone.return_value = None
        mock_user_repo.create_new_user.return_value = created_user_mock
        mock_supervisor_repo.create_new_supervisor.return_value = (
            created_supervisor_mock
        )
        # Call the service method
        result = await auth_service.create_unverified_new_user(new_supervisor_data)

        # Verify the result
        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once_with(
            conn=auth_service.session,
            email=new_supervisor_data.email,
            phone_number=new_supervisor_data.phone_number,
        )
        mock_user_repo.create_new_user.assert_awaited_once_with(
            conn=auth_service.session,
            new_user=new_supervisor_data,
            skill_repo=auth_service.skill_repo,
        )
        mock_supervisor_repo.create_new_supervisor.assert_awaited_once_with(
            conn=auth_service.session,
            new_supervisor=new_supervisor_data,
            user=created_user_mock,
        )
        mock_intern_repo.create_new_intern.assert_not_awaited()  # Ensure supervisor repo's create is NOT called
        mock_code_repo.create_code.assert_awaited_once_with(
            conn=auth_service.session, user_id=created_supervisor_mock.id, code=ANY
        )
        assert result == {"detail": "Verification code sent to email"}

    async def test_existing_unverified_user(
        self, auth_service, mock_user_repo, mock_code_repo
    ):
        # Setup for a user who exists but is not verified
        new_user_data = create_user_in_model()
        existing_unverified_user = create_mock_user(verified=False)

        mock_user_repo.get_user_by_email_or_phone.return_value = (
            existing_unverified_user
        )

        # Call the service method
        result = await auth_service.create_unverified_new_user(new_user_data)

        # Verify that we don't create a new user, but instead update their code
        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once_with(
            conn=auth_service.session,
            email=new_user_data.email,
            phone_number=new_user_data.phone_number,
        )
        mock_user_repo.create_new_user.assert_not_awaited()
        mock_code_repo.upsert_code_with_user_id.assert_awaited_once_with(
            conn=auth_service.session, user_id=existing_unverified_user.id, value=ANY
        )
        assert result == {"detail": "Verification code sent to email"}

    async def test_existing_verified_user_raises_exception(
        self, auth_service, mock_user_repo
    ):
        # Setup for a user who already exists and is verified
        new_user_data = create_user_in_model()
        existing_verified_user = create_mock_user(verified=True)

        mock_user_repo.get_user_by_email_or_phone.return_value = existing_verified_user

        # The method should raise an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await auth_service.create_unverified_new_user(new_user_data)

        assert excinfo.value.status_code == 409
        assert (
            "User already exists with specified email or phone number. Please log in"
            in excinfo.value.detail
        )


class TestVerifyUser:
    """Tests for the verify_user method of the AuthService."""

    @pytest.mark.parametrize(
        "user_type, mock_creator_func, expected_out_model",
        [
            (UserType.INTERN, create_mock_intern, InternOutModel),
            (UserType.SUPERVISOR, create_mock_supervisor, SupervisorOutModel),
        ],
    )
    @patch("src.services.auth_service.AccessToken", return_value="fake.access.token")
    async def test_verify_user_success_for_all_types(
        self,
        mock_access_token,
        auth_service,
        mock_code_repo,
        mock_user_repo,
        mock_background_tasks,
        user_type,
        mock_creator_func,
        expected_out_model,
    ):
        base_user = create_mock_user(verified=True, user_type=user_type)
        verified_user_obj = mock_creator_func(base_user)

        verification_code_obj = create_mock_verification_code(
            user_id=verified_user_obj.id
        )

        mock_code_repo.get_code.return_value = verification_code_obj
        mock_user_repo.update.return_value = verified_user_obj
        mock_access_token.new.return_value = "fake.access.token"

        result = await auth_service.verify_user(code="123456")

        mock_code_repo.get_code.assert_awaited_with(
            conn=auth_service.session, value="123456"
        )

        mock_user_repo.update.assert_awaited_with(
            conn=auth_service.session,
            user_id=verification_code_obj.user_id,
            values={"verified": True},
        )

        mock_code_repo.delete_code.assert_awaited_with(
            conn=auth_service.session, value="123456"
        )

        mock_access_token.new.assert_called_once()
        user_to_login_arg = mock_access_token.new.call_args[1]["user"]
        assert isinstance(user_to_login_arg, expected_out_model)

        mock_background_tasks.add_task.assert_called_once()

        assert result == {"access_token": "fake.access.token", "token_type": "Bearer"}

    async def test_verify_user_raises_exception_for_invalid_code(
        self, auth_service, mock_code_repo
    ):
        mock_code_repo.get_code.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.verify_user(code="invalidcode")

        assert exc_info.value.status_code == 400
        assert "Invalid verification code" in exc_info.value.detail

    async def test_verify_user_raises_exception_if_user_update_fails(
        self, auth_service, mock_code_repo, mock_user_repo
    ):
        verification_code_obj = create_mock_verification_code(uuid4())
        mock_code_repo.get_code.return_value = verification_code_obj
        mock_user_repo.update.return_value = None  # Simulate update failure

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.verify_user(code="123456")

        assert exc_info.value.status_code == 500
        assert "Something went wrong" in exc_info.value.detail


class TestLogin:
    """Tests for the login method of the AuthService."""

    @pytest.mark.parametrize(
        "user_type, mock_creator_func, expected_out_model",
        [
            (UserType.INTERN, create_mock_intern, InternOutModel),
            (UserType.SUPERVISOR, create_mock_supervisor, SupervisorOutModel),
        ],
    )
    @patch("src.services.auth_service.AccessToken")
    @patch("src.services.auth_service.password_is_correct", return_value=True)
    async def test_login_success_for_all_types(
        self,
        mock_password_check,
        mock_access_token,
        auth_service,
        mock_user_repo,
        user_type,
        mock_creator_func,
        expected_out_model,
    ):
        base_user = create_mock_user(verified=True, user_type=user_type)
        existing_user = mock_creator_func(base_user)
        mock_user_repo.get_user_by_email_or_phone.return_value = existing_user
        mock_access_token.new.return_value = "fake.access.token"

        result = await auth_service.login(
            username="test@example.com", password="correct_password"
        )

        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once_with(
            conn=auth_service.session, email="test@example.com"
        )
        mock_password_check.assert_called_once_with(
            existing_user.password, "correct_password"
        )
        mock_access_token.new.assert_called_once()
        user_to_login_arg = mock_access_token.new.call_args[
            1
        ][
            "user"
        ]  # Access the first positional argument passed to the mock_generate_token function
        assert isinstance(user_to_login_arg, expected_out_model)
        assert result == {"access_token": "fake.access.token", "token_type": "Bearer"}

    async def test_login_fails_for_non_existent_user(
        self, auth_service, mock_user_repo
    ):
        mock_user_repo.get_user_by_email_or_phone.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(
                username="nouser@example.com", password="any_password"
            )

        assert exc_info.value.status_code == 401
        assert "Invalid login credentials" in exc_info.value.detail

    @patch("src.services.auth_service.password_is_correct", return_value=False)
    async def test_login_fails_for_incorrect_password(
        self, mock_password_check, auth_service, mock_user_repo
    ):
        existing_user = create_mock_user(verified=True)
        mock_user_repo.get_user_by_email_or_phone.return_value = existing_user

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(
                username="test@example.com", password="wrong_password"
            )

        assert exc_info.value.status_code == 401
        assert "Invalid login credentials" in exc_info.value.detail
        mock_password_check.assert_called_once()

    @patch("src.services.auth_service.password_is_correct", return_value=True)
    async def test_login_fails_for_unverified_user(
        self, mock_password_check, auth_service, mock_user_repo
    ):
        unverified_user = create_mock_user(verified=False)
        mock_user_repo.get_user_by_email_or_phone.return_value = unverified_user

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(
                username="unverified@example.com", password="correct_password"
            )

        assert exc_info.value.status_code == 401
        assert "Invalid login credentials" in exc_info.value.detail


class TestRequestResetPassword:
    """Tests for the request_reset_password method."""

    @patch("src.services.auth_service.PasswordResetToken")
    async def test_request_reset_password_for_existing_user(
        self,
        mock_password_reset_token,
        auth_service,
        mock_user_repo,
        mock_background_tasks,
    ):
        existing_user = create_mock_user(verified=True)
        mock_user_repo.get_user_by_email_or_phone.return_value = existing_user
        mock_password_reset_token.new.return_value = "fake.password.reset.token"

        response = await auth_service.request_reset_password(email="test@example.com")

        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once_with(
            conn=auth_service.session, email="test@example.com"
        )
        mock_password_reset_token.new.assert_called_once_with(user_id=existing_user.id)
        mock_background_tasks.add_task.assert_called_once()
        assert (
            "If this email exists, a password reset email will be sent."
            in response["detail"]
        )

    @patch("src.services.auth_service.PasswordResetToken")
    async def test_request_reset_password_for_non_existent_user(
        self,
        mock_password_reset_token,
        auth_service,
        mock_user_repo,
        mock_background_tasks,
    ):
        mock_user_repo.get_user_by_email_or_phone.return_value = None

        response = await auth_service.request_reset_password(email="nouser@example.com")

        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once_with(
            conn=auth_service.session, email="nouser@example.com"
        )
        mock_password_reset_token.new.assert_not_called()
        mock_background_tasks.add_task.assert_not_called()
        assert (
            "If this email exists, a password reset email will be sent."
            in response["detail"]
        )


class TestVerifyCodeAndResetPassword:
    """Tests for the verify_code_and_reset_password method."""

    @patch(
        "src.services.auth_service.hash_password", return_value="new_hashed_password"
    )
    async def test_reset_password_success(
        self, mock_hash_password, auth_service, mock_user_repo, mock_background_tasks
    ):
        user_id = uuid4()

        updated_user_mock = create_mock_user(verified=True)
        mock_user_repo.update.return_value = updated_user_mock

        response = await auth_service.reset_password(
            user_id=user_id, new_password="newStrongPassword123"
        )

        mock_hash_password.assert_called_once_with("newStrongPassword123")
        mock_user_repo.update.assert_awaited_once_with(
            conn=auth_service.session,
            user_id=user_id,
            values={"password": "new_hashed_password"},
        )
        mock_background_tasks.add_task.assert_called_once()
        assert (
            "Your password has been reset successfully, please proceed to log in"
            in response["detail"]
        )
