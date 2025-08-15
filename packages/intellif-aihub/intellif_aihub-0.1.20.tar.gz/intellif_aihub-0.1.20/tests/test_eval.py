# !/usr/bin/env python
# -*-coding:utf-8 -*-
import unittest
import uuid
from unittest.mock import Mock, patch

import httpx

from aihub.services.eval import EvalService
from aihub.models.eval import ListEvalResp, EvalRun
from aihub.models.common import APIWrapper

BASE_URL = "http://192.168.13.160:30052"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTI1NDQwNDksImlhdCI6MTc1MVkzOTI0OSwidWlkIjoyfQ.MfB_7LK5oR3RAhga3jtgcvJqYESeUPLbz8Bc_y3fouc"


class TestEvalService(unittest.TestCase):

    def setUp(self):
        self.http_client = Mock(spec=httpx.Client)
        self.eval_service = EvalService(self.http_client)

    def test_list_eval_runs_default(self):
        mock_eval_run = {
            "id": 1,
            "name": "test_eval",
            "description": "Test evaluation",
            "user_id": 1,
            "model_id": 1,
            "model_name": "test_model",
            "dataset_id": 1,
            "dataset_version_id": 1,
            "dataset_name": "test_dataset",
            "status": "completed",
            "prediction_artifact_path": "/path/to/prediction",
            "evaled_artifact_path": "/path/to/eval",
            "run_id": "test_run_123",
            "dataset_summary": {},
            "metrics_summary": {"accuracy": 0.95},
            "viz_summary": {},
            "eval_config": {"metric": "accuracy"},
            "created_at": 1640995200,
            "updated_at": 1640995200
        }

        mock_response = {
            "code": 0,
            "msg": None,
            "data": {
                "total": 1,
                "page_size": 20,
                "page_num": 1,
                "data": [mock_eval_run]
            }
        }

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        result = self.eval_service.list()

        self.assertIsInstance(result, ListEvalResp)
        self.assertEqual(result.total, 1)
        self.assertEqual(result.page_size, 20)
        self.assertEqual(result.page_num, 1)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].id, 1)
        self.assertEqual(result.data[0].name, "test_eval")

        self.http_client.get.assert_called_once_with(
            "/eval-platform/api/v1/run/",
            params={"page_size": 20, "page_num": 1}
        )

    def test_list_eval_runs_with_filters(self):
        mock_response = {
            "code": 0,
            "msg": None,
            "data": {
                "total": 0,
                "page_size": 10,
                "page_num": 1,
                "data": []
            }
        }

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        # 带过滤参数
        result = self.eval_service.list(
            page_size=10,
            page_num=1,
            status="completed",
            name="test",
            model_id=1,
            dataset_id=2,
            dataset_version_id=3,
            run_id="test_run",
            user_id=1,
            model_ids="1,2,3",
            dataset_ids="2,3,4",
            dataset_version_ids="3,4,5"
        )

        self.assertIsInstance(result, ListEvalResp)
        self.assertEqual(result.total, 0)
        self.assertEqual(len(result.data), 0)

        expected_params = {
            "page_size": 10,
            "page_num": 1,
            "status": "completed",
            "name": "test",
            "model_id": 1,
            "dataset_id": 2,
            "dataset_version_id": 3,
            "run_id": "test_run",
            "user_id": 1,
            "model_ids": "1,2,3",
            "dataset_ids": "2,3,4",
            "dataset_version_ids": "3,4,5"
        }
        self.http_client.get.assert_called_once_with(
            "/eval-platform/api/v1/run/",
            params=expected_params
        )

    def test_list_eval_runs_api_error(self):
        """测试列出评测运行 - API错误"""
        # 模拟 API 错误
        mock_response = {
            "code": 1001,
            "msg": "Database connection failed",
            "data": None
        }

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        with self.assertRaises(Exception) as context:
            self.eval_service.list()

        self.assertIn("backend code 1001", str(context.exception))
        self.assertIn("Database connection failed", str(context.exception))

    def test_list_eval_runs_only_specified_filters(self):
        mock_response = {
            "code": 0,
            "msg": None,
            "data": {
                "total": 0,
                "page_size": 20,
                "page_num": 1,
                "data": []
            }
        }

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        result = self.eval_service.list(
            status="completed",
            model_id=1
        )

        expected_params = {
            "page_size": 20,
            "page_num": 1,
            "status": "completed",
            "model_id": 1
        }
        self.http_client.get.assert_called_once_with(
            "/eval-platform/api/v1/run/",
            params=expected_params
        )


if __name__ == "__main__":
    unittest.main()
