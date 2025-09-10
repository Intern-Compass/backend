""" Test for Auth Service """

import pytest
from unittest.mock import patch, ANY
from fastapi import HTTPException
from starlette.responses import Response

from tests.utils.utils import (
    create_mock_user,
    create_user_in_model,
    create_mock_verification_code,
    create_intern_in_model
)

pytestmark = pytest.mark.asyncio


class TestCreateUnverifiedNewUser:
    """Tests for the create_unverified_new_user method."""

    async def test_create_new_user_success(self, auth_service, mock_user_repo, mock_intern_repo, mock_code_repo):
        # Setup for a brand new user
        new_user_data = create_user_in_model()
        created_user_mock = create_mock_user(verified=False)
        
        mock_user_repo.get_user_by_email_or_phone.return_value = None
        mock_user_repo.create_new_user.return_value = created_user_mock

        result = await auth_service.create_unverified_new_user(new_user_data)

        # Verify the result
        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once()
        mock_user_repo.create_new_user.assert_awaited_once()
        mock_intern_repo.create_new_intern.assert_not_awaited() # Ensure intern repo is NOT called
        mock_code_repo.create_code.assert_awaited_once_with(conn=ANY, user_id=created_user_mock.id, code=ANY)
        assert result == {"detail": "Verification code sent to email"}

    async def test_create_new_intern_success(self, auth_service, mock_user_repo, mock_intern_repo, mock_code_repo):
        # Setup for a brand new intern. This test covers the `isinstance` check.
        new_intern_data = create_intern_in_model()
        created_user_mock = create_mock_user(verified=False) # The repo returns a User object
        mock_user_repo.get_user_by_email_or_phone.return_value = None
        mock_intern_repo.create_new_intern.return_value = created_user_mock
        # Call the service method
        result = await auth_service.create_unverified_new_user(new_intern_data)

        # Verify the result
        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once()
        mock_intern_repo.create_new_intern.assert_awaited_once()
        mock_user_repo.create_new_user.assert_not_awaited() # Ensure user repo's create is NOT called
        mock_code_repo.create_code.assert_awaited_once_with(conn=ANY, user_id=created_user_mock.id, code=ANY)
        assert result == {"detail": "Verification code sent to email"}

    async def test_existing_unverified_user(self, auth_service, mock_user_repo, mock_code_repo):
        # Setup for a user who exists but is not verified
        new_user_data = create_user_in_model()
        existing_unverified_user = create_mock_user(verified=False)

        mock_user_repo.get_user_by_email_or_phone.return_value = existing_unverified_user

        # Call the service method
        result = await auth_service.create_unverified_new_user(new_user_data)

        # Verify that we don't create a new user, but instead update their code
        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once()
        mock_user_repo.create_new_user.assert_not_awaited()
        mock_code_repo.upsert_code_with_user_id.assert_awaited_once()
        assert result == {"detail": "Verification code sent to email"}

    async def test_existing_verified_user_raises_exception(self, auth_service, mock_user_repo):
        # Setup for a user who already exists and is verified
        new_user_data = create_user_in_model()
        existing_verified_user = create_mock_user(verified=True)
        
        mock_user_repo.get_user_by_email_or_phone.return_value = existing_verified_user

        # The method should raise an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await auth_service.create_unverified_new_user(new_user_data)
        
        assert excinfo.value.status_code == 400
        assert "User already exists" in excinfo.value.detail


class TestVerifyUser:
    """Tests for the verify_user method."""
    
    @patch('src.services.auth_service.generate_access_token', return_value="fake.access.token")
    async def test_verify_user_success(self, mock_generate_token, auth_service, mock_code_repo, mock_user_repo):
        verified_user_obj = create_mock_user(verified=True)
        verification_code_obj = create_mock_verification_code(user_id=verified_user_obj.id)
        
        mock_code_repo.get_code.return_value = verification_code_obj
        mock_user_repo.update.return_value = verified_user_obj
        
        result = await auth_service.verify_user(code="123456")

        mock_code_repo.get_code.assert_awaited_with(conn=auth_service.session, value="123456")
        mock_user_repo.update.assert_awaited_with(conn=auth_service.session, user_id=verification_code_obj.user_id, values={"verified": True})
        mock_code_repo.delete_code.assert_awaited_once()
        mock_generate_token.assert_called_once()
        assert result == {
            "access_token": "fake.access.token",
            "token_type": "Bearer"
        }

    async def test_verify_user_invalid_code(self, auth_service, mock_code_repo):
        # Mock the repo to return None for the code lookup
        mock_code_repo.get_code.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            await auth_service.verify_user(code="invalidcode")
        
        assert excinfo.value.status_code == 400
        assert "Invalid verification code" in excinfo.value.detail


class TestLogin:
    """Tests for the login method."""

    @patch('src.services.auth_service.generate_access_token', return_value="fake.access.token")
    @patch('src.services.auth_service.password_is_correct', return_value=True)
    async def test_login_success(self, mock_password_check, mock_generate_token, auth_service, mock_user_repo):
        existing_verified_user = create_mock_user(verified=True)
        mock_user_repo.get_user_by_email_or_phone.return_value = existing_verified_user
        
        result = await auth_service.login("test@example.com", "correct_password", Response())

        mock_user_repo.get_user_by_email_or_phone.assert_awaited_once()
        mock_password_check.assert_called_once()
        mock_generate_token.assert_called_once()
        assert result["access_token"] == "fake.access.token"
        
    async def test_login_user_not_found(self, auth_service, mock_user_repo):
        mock_user_repo.get_user_by_email_or_phone.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            await auth_service.login("nouser@example.com", "password", Response())
        assert excinfo.value.status_code == 401
        
    @patch('src.services.auth_service.password_is_correct', return_value=False)
    async def test_login_incorrect_password(self, mock_password_check, auth_service, mock_user_repo):
        existing_user = create_mock_user(verified=True)
        mock_user_repo.get_user_by_email_or_phone.return_value = existing_user

        with pytest.raises(HTTPException) as excinfo:
            await auth_service.login("test@example.com", "wrong_password", Response())
        assert excinfo.value.status_code == 401
        
    @patch('src.services.auth_service.password_is_correct', return_value=True)
    async def test_login_user_not_verified(self, mock_password_is_correct, auth_service, mock_user_repo):
        unverified_user = create_mock_user(verified=False)
        mock_user_repo.get_user_by_email_or_phone.return_value = unverified_user

        with pytest.raises(HTTPException) as excinfo:
            await auth_service.login("test@example.com", "any_password", Response())
        assert excinfo.value.status_code == 401

