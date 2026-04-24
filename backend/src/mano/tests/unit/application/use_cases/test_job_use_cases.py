from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from mano.application.dtos.job_dtos import AssignTechnicianRequest, CreateJobRequest, SubmitQuoteRequest
from mano.application.use_cases.job_use_cases import JobUseCases
from mano.domain.models.job import Job, JobId, JobStatus
from mano.domain.models.service_model import CategoryId
from mano.domain.models.user import UserId
from mano.domain.services.job_service import JobService


class TestJobUseCases:
    @pytest.fixture
    def mock_job_service(self) -> AsyncMock:
        return AsyncMock(spec=JobService)

    @pytest.fixture
    def use_cases(self, mock_job_service: AsyncMock) -> JobUseCases:
        return JobUseCases(mock_job_service)

    @pytest.mark.asyncio
    async def test_create_job(self, use_cases: JobUseCases, mock_job_service: AsyncMock) -> None:
        request = CreateJobRequest(
            customer_id=UserId(),
            category_id=CategoryId(),
            description="Bathroom pipe burst during the night",
            latitude=41.9981,
            longitude=21.4254,
            address="Main Street 1",
        )
        created_job = Job(
            id=JobId(),
            customer_id=request.customer_id,
            category_id=request.category_id,
            description=request.description,
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_job_service.create_job.return_value = created_job

        result = await use_cases.create_job(request)

        mock_job_service.create_job.assert_called_once()
        assert result.description == request.description

    @pytest.mark.asyncio
    async def test_assign_technician(self, use_cases: JobUseCases, mock_job_service: AsyncMock) -> None:
        technician_id = UserId()
        existing_job = Job.create(
            customer_id=UserId(),
            category_id=CategoryId(),
            description="Ceiling leak needs inspection",
            latitude=41.9981,
            longitude=21.4254,
            address="Main Street 2",
        )
        assigned_job = existing_job.assign_technician(technician_id)
        mock_job_service.get_job_by_id.return_value = existing_job
        mock_job_service.update_job.return_value = assigned_job

        result = await use_cases.assign_technician(
            str(existing_job.id),
            AssignTechnicianRequest(technician_id=technician_id),
        )

        mock_job_service.update_job.assert_called_once()
        assert result.technician_id == technician_id
        assert result.status == JobStatus.assigned.value

    @pytest.mark.asyncio
    async def test_submit_quote(self, use_cases: JobUseCases, mock_job_service: AsyncMock) -> None:
        existing_job = Job.create(
            customer_id=UserId(),
            category_id=CategoryId(),
            description="Need urgent boiler repair",
            latitude=41.9981,
            longitude=21.4254,
            address="Main Street 3",
        ).assign_technician(UserId())
        quoted_job = existing_job.submit_quote(amount="200", description="Repair and parts")
        mock_job_service.get_job_by_id.return_value = existing_job
        mock_job_service.update_job.return_value = quoted_job

        result = await use_cases.submit_quote(
            str(existing_job.id),
            SubmitQuoteRequest(amount="200", description="Repair and parts"),
        )

        mock_job_service.update_job.assert_called_once()
        assert result.quote_amount == "200"
        assert result.status == JobStatus.diagnosed.value
