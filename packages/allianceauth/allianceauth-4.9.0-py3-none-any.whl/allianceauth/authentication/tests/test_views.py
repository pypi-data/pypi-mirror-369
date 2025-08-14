import json
import requests_mock
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from allianceauth.authentication.views import task_counts, esi_check
from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.authentication.constants import ESI_ERROR_MESSAGE_OVERRIDES

MODULE_PATH = "allianceauth.authentication.views"


def jsonresponse_to_dict(response) -> dict:
    return json.loads(response.content)


@patch(MODULE_PATH + ".queued_tasks_count")
@patch(MODULE_PATH + ".active_tasks_count")
class TestRunningTasksCount(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.user = AuthUtils.create_user("bruce_wayne")
        cls.user.is_superuser = True
        cls.user.save()

    def test_should_return_data(
        self, mock_active_tasks_count, mock_queued_tasks_count
    ):
        # given
        mock_active_tasks_count.return_value = 2
        mock_queued_tasks_count.return_value = 3
        request = self.factory.get("/")
        request.user = self.user
        # when
        response = task_counts(request)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            jsonresponse_to_dict(response), {
                "tasks_running": 2, "tasks_queued": 3}
        )

    def test_su_only(
        self, mock_active_tasks_count, mock_queued_tasks_count
    ):
        self.user.is_superuser = False
        self.user.save()
        self.user.refresh_from_db()
        # given
        mock_active_tasks_count.return_value = 2
        mock_queued_tasks_count.return_value = 3
        request = self.factory.get("/")
        request.user = self.user
        # when
        response = task_counts(request)
        # then
        self.assertEqual(response.status_code, 302)


class TestEsiCheck(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.user = AuthUtils.create_user("bruce_wayne")
        cls.user.is_superuser = True
        cls.user.save()

    @requests_mock.Mocker()
    def test_401_data_returns_200(
        self, m
    ):
        error_json = {
            "error": "You have been banned from using ESI. Please contact Technical Support. (support@eveonline.com)"
        }
        status_code = 401
        m.get(
            "https://esi.evetech.net/latest/status/?datasource=tranquility",
            text=json.dumps(error_json),
            status_code=status_code
        )
        # given
        request = self.factory.get("/")
        request.user = self.user
        # when
        response = esi_check(request)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            jsonresponse_to_dict(response), {
                "status": status_code,
                "data": error_json
            }
        )

    @requests_mock.Mocker()
    def test_504_data_returns_200(
        self, m
    ):
        error_json = {
            "error": "Gateway timeout message",
            "timeout": 5000
        }
        status_code = 504
        m.get(
            "https://esi.evetech.net/latest/status/?datasource=tranquility",
            text=json.dumps(error_json),
            status_code=status_code
        )
        # given
        request = self.factory.get("/")
        request.user = self.user
        # when
        response = esi_check(request)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            jsonresponse_to_dict(response), {
                "status": status_code,
                "data": error_json
            }
        )

    @requests_mock.Mocker()
    def test_420_data_override(
        self, m
    ):
        error_json = {
            "error": "message from CCP",
        }
        status_code = 420
        m.get(
            "https://esi.evetech.net/latest/status/?datasource=tranquility",
            text=json.dumps(error_json),
            status_code=status_code
        )
        # given
        request = self.factory.get("/")
        request.user = self.user
        # when
        response = esi_check(request)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            jsonresponse_to_dict(response)["data"],
            error_json
        )
        self.assertDictEqual(
            jsonresponse_to_dict(response), {
                "status": status_code,
                "data": {
                    "error": ESI_ERROR_MESSAGE_OVERRIDES.get(status_code)
                }
            }
        )

    @requests_mock.Mocker()
    def test_200_data_returns_200(
        self, m
    ):
        good_json = {
            "players": 5,
            "server_version": "69420",
            "start_time": "2030-01-01T23:59:59Z"
        }
        status_code = 200

        m.get(
            "https://esi.evetech.net/latest/status/?datasource=tranquility",
            text=json.dumps(good_json),
            status_code=status_code
        )
        # given
        request = self.factory.get("/")
        request.user = self.user
        # when
        response = esi_check(request)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            jsonresponse_to_dict(response), {
                "status": status_code,
                "data": good_json
            }
        )

    def test_su_only(
        self,
    ):
        self.user.is_superuser = False
        self.user.save()
        self.user.refresh_from_db()
        # given
        request = self.factory.get("/")
        request.user = self.user
        # when
        response = esi_check(request)
        # then
        self.assertEqual(response.status_code, 302)
