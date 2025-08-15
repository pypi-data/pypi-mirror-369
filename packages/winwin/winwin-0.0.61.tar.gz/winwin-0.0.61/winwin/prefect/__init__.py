from prefect import Flow, get_run_logger, runtime, task
from prefect import flow as prefect_flow
from prefect.client.schemas.objects import FlowRun
from prefect.flows import FlowDecorator
from prefect.states import State
from prefect.variables import Variable

from winwin.dingtalk import DingtalkBot
from winwin.prefect.odps import OdpsCredentials

from .aliyun import AliyunOss, AliyunOssCredentials
from .ssh import SshCredentials


def notify_dingding(dingtalk_endpoint: str):
    def send_notify_dingding(flow: Flow, flow_run: FlowRun, state: State):
        get_run_logger().error(
            f"发送钉钉通知: 流程 {flow.name} 状态为 {state.name}"
            f": {runtime.flow_run.get_flow_run_ui_url()}"
        )
        DingtalkBot(dingtalk_endpoint).send_markdown(
            "Prefect 任务执行错误",
            f"流程 {flow.name}-{flow_run.name} 状态为 {state.name} "
            f"错误消息:\n\n"
            f"[流程页面]({runtime.flow_run.get_flow_run_ui_url()})\n\n"
            f"流程启动时间:{flow_run.expected_start_time:%Y-%m-%d %H:%M:%S}\n\n",
        )

    return send_notify_dingding


def flow(*args, **kwargs):
    # 定义默认参数
    default_kwargs = {
        "log_prints": True,
        "persist_result": True,
        "result_storage": "aliyun-oss/aliyun-oss-dev",
    }
    # 添加钉钉通知
    dingtalk_endpoint = Variable.get("dingtalk_endpoint", None)
    if dingtalk_endpoint:
        for hook in ["on_failure", "on_crashed"]:
            if hook not in kwargs:
                kwargs[hook] = [notify_dingding(dingtalk_endpoint)]
            else:
                kwargs[hook].append(notify_dingding(dingtalk_endpoint))
    final_args = {**default_kwargs, **kwargs}
    return prefect_flow(*args, **final_args)


flow: FlowDecorator

__all__ = [
    "AliyunOss",
    "AliyunOssCredentials",
    "OdpsCredentials",
    "SshCredentials",
    "flow",
    "task",
]
