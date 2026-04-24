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


def test_phone_number_valid() -> None:
    phone = PhoneNumber("+393401234567")
    assert str(phone) == "+393401234567"


def test_phone_number_invalid_prefix() -> None:
    with pytest.raises(ValueError, match=r"Phone must start with \+39"):
        PhoneNumber("+1234567890123")


def test_phone_number_invalid_length() -> None:
    with pytest.raises(ValueError, match="Phone must be 13 characters"):
        PhoneNumber("+393401234")


def test_user_profile_role_checks():
    profile = UserProfile(
        id=UserId(),
        auth_user_id=UserAuthId(),
        name="Arben",
        surname="Ahmeti",
        phone="+393401112220",
        role=UserRole.provider,
    )
    assert profile.is_provider() is True
    assert profile.is_client() is False
    assert profile.is_admin() is False


def test_user_profile_get_display_name():
    profile = UserProfile(
        id=UserId(),
        auth_user_id=UserAuthId(),
        name="John",
        surname="Doe",
        phone="+393401112220",
        role=UserRole.provider,
        company_name="Doe Repair",
    )
    assert profile.get_display_name() == "Doe Repair"

    client_profile = replace_role(profile, UserRole.client)
    assert client_profile.get_display_name() == "John Doe"


def replace_role(profile: UserProfile, role: UserRole) -> UserProfile:
    from dataclasses import replace

    return replace(profile, role=role)


def test_user_profile_full_name() -> None:
    profile = UserProfile(id=UserId(), auth_user_id=UserAuthId(), name="John", surname="Doe", phone="+393401112220")
    assert profile.full_name == "John Doe"


def test_user_profile_full_name_no_surname() -> None:
    profile = UserProfile(id=UserId(), auth_user_id=UserAuthId(), name="John", surname="", phone="+393401112220")
    assert profile.has_complete_profile() is True
