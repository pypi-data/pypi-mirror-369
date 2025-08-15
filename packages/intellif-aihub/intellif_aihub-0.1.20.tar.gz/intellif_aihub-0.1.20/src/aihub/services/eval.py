# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""评测平台服务模块

本模块围绕 **“模型评测（Run → Report）”** 提供能力：

- **创建评测任务 / 评测报告**
- **获取评测任务列表**
"""

import httpx

from ..exceptions import APIError
from ..models.common import APIWrapper
from ..models.eval import CreateEvalReq, CreateEvalResp, ListEvalReq, ListEvalResp

_BASE = "/eval-platform/api/v1"


class EvalService:
    """评测服务"""

    def __init__(self, http: httpx.Client):
        self._http = http
        self._eval = _Eval(http)

    def create(
        self,
        dataset_version_name: str,
        prediction_artifact_path: str,
        evaled_artifact_path: str,
        report_json: dict,
        run_id,
    ) -> int:
        """创建评测报告

        Args:
            run_id (str): RUN ID
            report_json (dict): 报告内容
            evaled_artifact_path:   评测结果制品路径
            prediction_artifact_path: 推理结果制品路径
            dataset_version_name (str): 数据集名称


        Returns:
            id (int): 评测报告id

        """
        from .dataset_management import DatasetManagementService

        dataset_service = DatasetManagementService(self._http)
        dataset_version = dataset_service.get_dataset_version_by_name(
            dataset_version_name
        )
        payload = CreateEvalReq(
            dataset_id=dataset_version.dataset_id,
            dataset_version_id=dataset_version.id,
            evaled_artifact_path=evaled_artifact_path,
            prediction_artifact_path=prediction_artifact_path,
            report=report_json,
            run_id=run_id,
        )

        return self._eval.create(payload)

    def list(
        self,
        page_size: int = 20,
        page_num: int = 1,
        status: str = None,
        name: str = None,
        model_id: int = None,
        dataset_id: int = None,
        dataset_version_id: int = None,
        run_id: str = None,
        user_id: int = None,
        model_ids: str = None,
        dataset_ids: str = None,
        dataset_version_ids: str = None,
    ) -> ListEvalResp:
        """列出评测结果

        Args:
            page_size (int): 页面大小，默认为20
            page_num (int): 页码，默认为1
            status (str, optional): 状态过滤
            name (str, optional): 名称过滤
            model_id (int, optional): 模型ID过滤
            dataset_id (int, optional): 数据集ID过滤
            dataset_version_id (int, optional): 数据集版本ID过滤
            run_id (str, optional): 运行ID过滤
            user_id (int, optional): 用户ID过滤
            model_ids (str, optional): 模型ID列表过滤（逗号分隔）
            dataset_ids (str, optional): 数据集ID列表过滤（逗号分隔）
            dataset_version_ids (str, optional): 数据集版本ID列表过滤（逗号分隔）

        Returns:
            ListEvalResp: 评测结果列表响应
        """
        payload = ListEvalReq(
            page_size=page_size,
            page_num=page_num,
            status=status,
            name=name,
            model_id=model_id,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            run_id=run_id,
            user_id=user_id,
            model_ids=model_ids,
            dataset_ids=dataset_ids,
            dataset_version_ids=dataset_version_ids,
        )

        return self._eval.list(payload)


class _Eval:
    def __init__(self, http: httpx.Client):
        self._http = http

    def create(self, payload: CreateEvalReq) -> int:
        resp = self._http.post(f"{_BASE}/run/", json=payload.model_dump())
        wrapper = APIWrapper[CreateEvalResp].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data.eval_run.id

    def list(self, payload: ListEvalReq) -> ListEvalResp:
        # Build query parameters, excluding None values
        params = {}
        for field, value in payload.model_dump().items():
            if value is not None:
                params[field] = value

        resp = self._http.get(f"{_BASE}/run/", params=params)
        wrapper = APIWrapper[ListEvalResp].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data
