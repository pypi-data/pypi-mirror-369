# !/usr/bin/env python
# -*-coding:utf-8 -*-
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CreateEvalReq(BaseModel):
    """创建评测任务"""
    dataset_id: int = Field(description="数据集ID")
    dataset_version_id: int = Field(description="数据集版本ID")
    prediction_artifact_path: str = Field(description="推理产物的路径")
    evaled_artifact_path: str = Field(description="评测结果产物的路径")
    run_id: str = Field(description="运行ID")
    user_id: int = Field(0, description="用户ID")
    report: Dict = Field(default_factory=dict, description="评测报告")


class EvalRun(BaseModel):
    """评测任务的运行实体"""
    id: int = Field(description="评测的运行ID")
    name: str = Field(description="评测名称")
    description: str = Field(description="评测描述")
    user_id: int = Field(description="用户ID")
    model_id: int = Field(description="模型ID")
    model_name: str = Field(description="模型名称")
    dataset_id: int = Field(description="数据集ID")
    dataset_version_id: int = Field(description="数据集版本ID")
    dataset_name: str = Field(description="数据集名称")
    status: str = Field(description="状态")
    prediction_artifact_path: str = Field(description="推理产物路径")
    evaled_artifact_path: str = Field(description="评测结果产物路径")
    run_id: str = Field(description="运行ID")
    dataset_summary: Dict = Field(default_factory=dict, description="数据集摘要")
    metrics_summary: Dict = Field(default_factory=dict, description="指标摘要")
    viz_summary: Dict = Field(default_factory=dict, description="可视化摘要")
    eval_config: Optional[Dict] = Field(default=None, description="评测配置")
    created_at: int = Field(description="创建时间")
    updated_at: int = Field(description="更新时间")


class CreateEvalResp(BaseModel):
    """创建评测任务的返回结果"""
    eval_run: EvalRun = Field(alias="eval_run", description="评测运行信息")


class ListEvalReq(BaseModel):
    """列出评测任务请求"""
    page_size: int = Field(20, description="页面大小")
    page_num: int = Field(1, description="页码")
    status: Optional[str] = Field(None, description="状态过滤")
    name: Optional[str] = Field(None, description="名称过滤")
    model_id: Optional[int] = Field(None, description="模型ID过滤")
    dataset_id: Optional[int] = Field(None, description="数据集ID过滤")
    dataset_version_id: Optional[int] = Field(None, description="数据集版本ID过滤")
    run_id: Optional[str] = Field(None, description="运行ID过滤")
    user_id: Optional[int] = Field(None, description="用户ID过滤")
    model_ids: Optional[str] = Field(None, description="模型ID列表过滤")
    dataset_ids: Optional[str] = Field(None, description="数据集ID列表过滤")
    dataset_version_ids: Optional[str] = Field(None, description="数据集版本ID列表过滤")


class ListEvalResp(BaseModel):
    """列出评测任务响应"""
    total: int = Field(description="总数")
    page_size: int = Field(description="页面大小")
    page_num: int = Field(description="页码")
    data: List[EvalRun] = Field(description="评测运行列表")
