from datetime import datetime, UTC

import pytest
from unittest.mock import AsyncMock

from mano.application.dtos.availability_dtos import CreateAvailabilityRequest, UpdateAvailabilityRequest
from mano.application.use_cases.availability_use_cases import AvailabilityUseCases
from mano.domain.exceptions.base import AvailabilityNotFoundError
from mano.domain.models.availability import Availability, AvailabilityId
from mano.domain.models.service_model import ProviderId
from mano.domain.services.availability_service import AvailabilityService


class TestAvailabilityUseCases:
    @pytest.fixture
    def mock_availability_service(self):
        return AsyncMock(spec=AvailabilityService)

    @pytest.fixture
    def use_cases(self, mock_availability_service):
        return AvailabilityUseCases(availability_service=mock_availability_service)

    @pytest.mark.asyncio
    async def test_create_availability(self, use_cases, mock_availability_service):
        request = CreateAvailabilityRequest(
            provider_id=ProviderId(),
            day_of_week=1,
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            specific_date=None,
        )
        created = Availability(
            id=AvailabilityId(),
            provider_id=request.provider_id,
            day_of_week=request.day_of_week,
            start_time=request.start_time,
            end_time=request.end_time,
            is_available=request.is_available,
            specific_date=request.specific_date,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_availability_service.create_availability.return_value = created

        result = await use_cases.create_availability(request)

        mock_availability_service.create_availability.assert_called_once()
        assert result.provider_id == request.provider_id
        assert result.start_time == "09:00"

    @pytest.mark.asyncio
    async def test_get_availability_by_id(self, use_cases, mock_availability_service):
        availability = Availability(
            id=AvailabilityId(),
            provider_id=ProviderId(),
            day_of_week=2,
            start_time="10:00",
            end_time="12:00",
            is_available=True,
            specific_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_availability_service.get_availability_by_id.return_value = availability

        result = await use_cases.get_availability_by_id(str(availability.id))

        mock_availability_service.get_availability_by_id.assert_called_once()
        assert result.id == availability.id

    @pytest.mark.asyncio
    async def test_get_availability_by_id_not_found(self, use_cases, mock_availability_service):
        mock_availability_service.get_availability_by_id.return_value = None

        with pytest.raises(AvailabilityNotFoundError):
            await use_cases.get_availability_by_id(str(AvailabilityId()))

    @pytest.mark.asyncio
    async def test_list_by_provider(self, use_cases, mock_availability_service):
        provider_id = ProviderId()
        mock_availability_service.list_by_provider.return_value = [
            Availability(
                id=AvailabilityId(),
                provider_id=provider_id,
                day_of_week=0,
                start_time="08:00",
                end_time="10:00",
                is_available=True,
                specific_date=None,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

        result = await use_cases.list_by_provider(str(provider_id))

        mock_availability_service.list_by_provider.assert_called_once()
        assert len(result) == 1
        assert result[0].provider_id == provider_id

    @pytest.mark.asyncio
    async def test_list_all(self, use_cases, mock_availability_service):
        mock_availability_service.list_all.return_value = [
            Availability(
                id=AvailabilityId(),
                provider_id=ProviderId(),
                day_of_week=3,
                start_time="11:00",
                end_time="13:00",
                is_available=True,
                specific_date=None,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

        result = await use_cases.list_all()

        mock_availability_service.list_all.assert_called_once()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_update_availability(self, use_cases, mock_availability_service):
        availability = Availability(
            id=AvailabilityId(),
            provider_id=ProviderId(),
            day_of_week=4,
            start_time="09:00",
            end_time="12:00",
            is_available=True,
            specific_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_availability_service.get_availability_by_id.return_value = availability

        updated = availability.update(start_time="10:00", end_time="13:00", is_available=False)
        mock_availability_service.update_availability.return_value = updated

        request = UpdateAvailabilityRequest(start_time="10:00", end_time="13:00", is_available=False)
        result = await use_cases.update_availability(str(availability.id), request)

        mock_availability_service.update_availability.assert_called_once()
        assert result.start_time == "10:00"
        assert result.is_available is False

    @pytest.mark.asyncio
    async def test_update_availability_not_found(self, use_cases, mock_availability_service):
        mock_availability_service.get_availability_by_id.return_value = None

        with pytest.raises(AvailabilityNotFoundError):
            await use_cases.update_availability(str(AvailabilityId()), UpdateAvailabilityRequest())

    @pytest.mark.asyncio
    async def test_delete_availability(self, use_cases, mock_availability_service):
        availability = Availability(
            id=AvailabilityId(),
            provider_id=ProviderId(),
            day_of_week=5,
            start_time="09:00",
            end_time="11:00",
            is_available=True,
            specific_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_availability_service.get_availability_by_id.return_value = availability

        await use_cases.delete_availability(str(availability.id))

        mock_availability_service.delete_availability.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_availability_not_found(self, use_cases, mock_availability_service):
        mock_availability_service.get_availability_by_id.return_value = None

        with pytest.raises(AvailabilityNotFoundError):
            await use_cases.delete_availability(str(AvailabilityId()))
