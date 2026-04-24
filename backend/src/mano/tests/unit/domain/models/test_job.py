from mano.domain.exceptions.base import JobStateError
from mano.domain.models.job import Job, JobStatus
from mano.domain.models.service_model import CategoryId
from mano.domain.models.user import UserId


def test_job_quote_approval_unlocks_chat() -> None:
    customer_id = UserId()
    technician_id = UserId()
    category_id = CategoryId()

    job = Job.create(
        customer_id=customer_id,
        category_id=category_id,
        description="Kitchen sink is leaking badly",
        latitude=41.9981,
        longitude=21.4254,
        address="Main Street 1",
    )
    assigned_job = job.assign_technician(technician_id)
    quoted_job = assigned_job.submit_quote(amount="150.00", description="Replacement parts and labor")
    approved_job = quoted_job.approve_quote()

    assert approved_job.status == JobStatus.quote_approved.value
    assert approved_job.chat_unlocked is True
    assert approved_job.call_out_fee_paid is True
    assert approved_job.quote_approved_at is not None


def test_job_cannot_skip_directly_to_completed() -> None:
    job = Job.create(
        customer_id=UserId(),
        category_id=CategoryId(),
        description="Water heater stopped working today",
        latitude=41.9981,
        longitude=21.4254,
        address="Second Street 2",
    ).assign_technician(UserId())

    try:
        job.change_status(JobStatus.completed.value)
    except JobStateError as exc:
        assert "Cannot transition job" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected invalid status transition to fail")
