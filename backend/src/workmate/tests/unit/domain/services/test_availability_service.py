from datetime import datetime, UTC

import pytest
from unittest.mock import AsyncMock

from workmate.domain.exceptions.base import DomainError
from workmate.domain.models.availability import Availability, AvailabilityId
from workmate.domain.models.service_model import ProviderId
from workmate.domain.repositories.availability_repository import AvailabilityRepository
from workmate.domain.services.availability_service import AvailabilityService


class TestAvailabilityService:
    @pytest.mark.asyncio
    async def test_create_availability(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)

        availability = Availability(
            id=AvailabilityId(),
            provider_id=ProviderId(),
            day_of_week=1,
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            specific_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_repo.create_availability.return_value = availability

        result = await service.create_availability(availability)

        mock_repo.create_availability.assert_called_once_with(availability)
        assert result == availability

    @pytest.mark.asyncio
    async def test_create_availability_invalid_time(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)

        availability = Availability(
            id=AvailabilityId(),
            provider_id=ProviderId(),
            day_of_week=1,
            start_time="17:00",
            end_time="09:00",
            is_available=True,
            specific_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with pytest.raises(DomainError, match="start_time must be before end_time"):
            await service.create_availability(availability)

    @pytest.mark.asyncio
    async def test_create_availability_invalid_day(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)

        availability = Availability(
            id=AvailabilityId(),
            provider_id=ProviderId(),
            day_of_week=7,
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            specific_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with pytest.raises(DomainError, match="day_of_week must be between 0 and 6"):
            await service.create_availability(availability)

    @pytest.mark.asyncio
    async def test_get_availability_by_id(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)
        availability_id = AvailabilityId()
        expected = AsyncMock(spec=Availability)
        mock_repo.get_availability_by_id.return_value = expected

        result = await service.get_availability_by_id(availability_id)

        mock_repo.get_availability_by_id.assert_called_once_with(availability_id)
        assert result == expected

    @pytest.mark.asyncio
    async def test_list_by_provider(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)
        provider_id = ProviderId()
        expected = [AsyncMock(spec=Availability)]
        mock_repo.list_by_provider.return_value = expected

        result = await service.list_by_provider(provider_id)

        mock_repo.list_by_provider.assert_called_once_with(provider_id)
        assert result == expected

    @pytest.mark.asyncio
    async def test_list_all(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)
        expected = [AsyncMock(spec=Availability)]
        mock_repo.list_all.return_value = expected

        result = await service.list_all()

        mock_repo.list_all.assert_called_once()
        assert result == expected

    @pytest.mark.asyncio
    async def test_update_availability(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)
        availability = AsyncMock(spec=Availability)
        availability.day_of_week = 1
        availability.start_time = "09:00"
        availability.end_time = "17:00"
        mock_repo.update_availability.return_value = availability

        result = await service.update_availability(availability)

        mock_repo.update_availability.assert_called_once_with(availability)
        assert result == availability

    @pytest.mark.asyncio
    async def test_delete_availability(self):
        mock_repo = AsyncMock(spec=AvailabilityRepository)
        service = AvailabilityService(availability_repository=mock_repo)
        availability_id = AvailabilityId()
        mock_repo.delete_availability.return_value = None

        await service.delete_availability(availability_id)

        mock_repo.delete_availability.assert_called_once_with(availability_id)
