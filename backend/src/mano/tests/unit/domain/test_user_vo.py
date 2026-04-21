import pytest
import uuid
from mano.domain.models.user import UserId, UserAuthId, PhoneNumber, UserProfile, UserRole


def test_user_id_default_factory():
    uid = UserId()
    assert isinstance(uid.value, str)
    assert uuid.UUID(uid.value)


def test_auth_user_id_default_factory():
    fid = UserAuthId()
    assert isinstance(fid.value, str)
    assert uuid.UUID(fid.value)


def test_phone_number_success():
    phone = PhoneNumber("+38970123456")
    assert str(phone) == "+38970123456"


def test_phone_number_invalid_prefix():
    with pytest.raises(ValueError, match=r"Phone must start with \+389"):
        PhoneNumber("+35570123456")


def test_phone_number_invalid_length():
    with pytest.raises(ValueError, match="Phone must be 12 characters"):
        PhoneNumber("+389701234")


def test_user_profile_role_checks():
    profile = UserProfile(
        id=UserId(), auth_user_id=UserAuthId(), full_name="Test User", phone="+38970111222", role=UserRole.provider
    )
    assert profile.is_provider() is True
    assert profile.is_client() is False
    assert profile.is_admin() is False


def test_user_profile_get_display_name():
    profile = UserProfile(
        id=UserId(),
        auth_user_id=UserAuthId(),
        full_name="John Doe",
        phone="+38970111222",
        role=UserRole.provider,
        company_name="Doe Repair",
    )
    assert profile.get_display_name() == "Doe Repair"

    client_profile = replace_role(profile, UserRole.client)
    assert client_profile.get_display_name() == "John Doe"


def replace_role(profile: UserProfile, role: UserRole) -> UserProfile:
    from dataclasses import replace

    return replace(profile, role=role)


def test_user_profile_complete_check():
    profile = UserProfile(id=UserId(), auth_user_id=UserAuthId(), full_name="John Doe", phone="+38970111222")
    assert profile.has_complete_profile() is True
