"""Unit tests for constants module."""

from mano.common.constans import HTTPStatus, FieldLength, Pagination


class TestHTTPStatus:
    """Test HTTP status constants."""

    def test_success_codes(self):
        """Test success status codes."""
        assert HTTPStatus.OK == 200
        assert HTTPStatus.CREATED == 201
        assert HTTPStatus.ACCEPTED == 202
        assert HTTPStatus.NO_CONTENT == 204

    def test_client_error_codes(self):
        """Test client error status codes."""
        assert HTTPStatus.BAD_REQUEST == 400
        assert HTTPStatus.UNAUTHORIZED == 401
        assert HTTPStatus.FORBIDDEN == 403
        assert HTTPStatus.NOT_FOUND == 404

    def test_server_error_codes(self):
        """Test server error status codes."""
        assert HTTPStatus.INTERNAL_SERVER_ERROR == 500
        assert HTTPStatus.BAD_GATEWAY == 502
        assert HTTPStatus.SERVICE_UNAVAILABLE == 503


class TestFieldLength:
    """Test field length constants."""

    def test_user_fields(self):
        """Test user field lengths."""
        assert FieldLength.EMAIL == 255
        assert FieldLength.NAME == 255
        assert FieldLength.PHONE == 20
        assert FieldLength.BIO == 1000

    def test_service_fields(self):
        """Test service field lengths."""
        assert FieldLength.TITLE == 255
        assert FieldLength.DESCRIPTION == 5000
        assert FieldLength.SHORT_DESCRIPTION == 500


class TestPagination:
    """Test pagination constants."""

    def test_default_values(self):
        """Test default pagination values."""
        assert Pagination.DEFAULT_LIMIT == 20
        assert Pagination.MAX_LIMIT == 100
        assert Pagination.MIN_LIMIT == 1
        assert Pagination.DEFAULT_OFFSET == 0

    def test_specific_limits(self):
        """Test specific pagination limits."""
        assert Pagination.SEARCH_RESULTS_LIMIT == 50
        assert Pagination.REVIEWS_LIMIT == 20
        assert Pagination.BOOKINGS_LIMIT == 20
