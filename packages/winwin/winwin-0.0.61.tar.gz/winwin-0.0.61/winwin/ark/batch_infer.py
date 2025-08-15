import os
import json
from datetime import datetime

import aiohttp
import backoff
import importlib
from . import utils
from pathlib import Path
from typing import Dict, Any

tos = importlib.import_module("tos")


class TosClient:
    # 文档链接：https://www.volcengine.com/docs/6349/92786
    def __init__(self):
        self.ak = os.environ.get("TOS_ACCESS_KEY") or os.environ.get("VOLC_ACCESSKEY")
        self.sk = os.environ.get("TOS_SECRET_KEY") or os.environ.get("VOLC_SECRETKEY")

        self.endpoint = os.environ.get("TOS_ENDPOINT") or "tos-cn-beijing.volces.com"
        self.region = os.environ.get("TOS_REGION") or "cn-beijing"
        print(f"ak: {self.ak}, sk:{self.sk}, endpoint:{self.endpoint}, region:{self.region}")
        self.client = tos.TosClientV2(self.ak, self.sk, self.endpoint, self.region)

    def create_bucket(self, bucket_name):
        try:
            self.client.create_bucket(bucket_name, acl=tos.ACLType.ACL_Public_Read_Write)
        except tos.exceptions.TosClientError as e:
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
        except tos.exceptions.TosServerError as e:
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
            print('error with ec: {}'.format(e.ec))
            print('error with request url: {}'.format(e.request_url))
        except Exception as e:
            print('fail with unknown error: {}'.format(e))

    def put_object(self, bucket_name, object_key, data):
        try:
            # 通过字符串方式添加 Object
            res = self.client.put_object(bucket_name, object_key, content=data)
        except tos.exceptions.TosClientError as e:
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
        except tos.exceptions.TosServerError as e:
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
            print('error with ec: {}'.format(e.ec))
            print('error with request url: {}'.format(e.request_url))
        except Exception as e:
            print('fail with unknown error: {}'.format(e))

    def put_object_from_file(self, bucket_name, object_key, file_path):
        try:
            # 通过字符串方式添加 Object
            res = self.client.put_object_from_file(bucket_name, object_key, file_path)
        except tos.exceptions.TosClientError as e:
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
        except tos.exceptions.TosServerError as e:
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
            print('error with ec: {}'.format(e.ec))
            print('error with request url: {}'.format(e.request_url))
        except Exception as e:
            print('fail with unknown error: {}'.format(e))

    def get_object(self, bucket_name, object_name):
        try:
            # 从TOS bucket中下载对象到内存中
            object_stream = self.client.get_object(bucket_name, object_name)
            # object_stream 为迭代器可迭代读取数据
            # for content in object_stream:
            #     print(content)
            # 您也可调用 read()方法一次在内存中获取完整的数据
            print(object_stream.read())
        except tos.exceptions.TosClientError as e:
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
        except tos.exceptions.TosServerError as e:
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
            print('error with ec: {}'.format(e.ec))
            print('error with request url: {}'.format(e.request_url))
        except Exception as e:
            print('fail with unknown error: {}'.format(e))

    def close_client(self):
        try:
            # 执行相关操作后，将不再使用的TosClient关闭
            self.client.close()
        except tos.exceptions.TosClientError as e:
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
        except tos.exceptions.TosServerError as e:
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
            print('error with ec: {}'.format(e.ec))
            print('error with request url: {}'.format(e.request_url))
        except Exception as e:
            print('fail with unknown error: {}'.format(e))


class BatchInferenceClient:
    def __init__(self):
        """
        初始化BatchInferenceClient类的实例。
        该方法设置了一些默认属性，如重试次数、超时时间、访问密钥（AK/SK）、账号ID、API版本、服务域名、区域和基础参数。
        访问密钥（AK/SK）从环境变量中获取，以提高安全性。
        基础参数包括API版本和账号ID，这些参数在每次请求中都会用到。
        """
        # 设置重试次数为3次
        self._retry = 3
        # 设置请求超时时间为60秒
        self._timeout = aiohttp.ClientTimeout(60)
        # Access Key访问火山云资源的秘钥，可从访问控制-API访问密钥获取获取
        self.ak = os.environ["VOLC_ACCESSKEY"]
        self.sk = os.environ["VOLC_SECRETKEY"]
        # 设置模型名称
        self.model = os.getenv("MODEL_NAME", "doubao-pro-32k")
        # 设置模型版本
        self.model_version = os.getenv("MODEL_VERSION", "241215")
        # 需要替换为您的账号id，可从火山引擎官网点击账号头像，弹出框中找到，复制“账号ID”后的一串数字
        self.account_id = os.environ["VOLC_ACCOUNT_ID"]
        # 设置API版本
        self.version = os.getenv("VOLC_BI_API_VERSION", "2024-01-01")
        # 设置服务域名
        self.domain = os.getenv("VOLC_BI_API_DOMAIN", "open.volcengineapi.com")
        # 设置区域
        self.region = os.getenv("VOLC_BI_API_REGION", "cn-beijing")
        # 设置服务名称
        self.service = os.getenv("VOLC_BI_API_SERVICE", "ark")
        # 设置基础参数，包括API版本和账号ID
        self.base_param = {"Version": self.version, "X-Account-Id": self.account_id}

    async def _call(self, url, headers, req: Dict[str, Any]):
        """
        异步调用指定URL的HTTP POST请求，并处理请求的重试逻辑。
        :param url: 请求的目标URL。
        :param headers: 请求的HTTP头部信息。
        :param req: 请求的JSON格式数据。
        :return: 响应的JSON数据。
        :raises Exception: 如果请求失败或解析响应失败，抛出异常。
        """

        @backoff.on_exception(
            backoff.expo, Exception, factor=0.1, max_value=5, max_tries=self._retry
        )
        async def _retry_call(body):
            """
            内部函数，用于发送HTTP POST请求，并处理请求的重试逻辑。
            :param body: 请求的JSON格式数据。
            :return: 响应的JSON数据。
            :raises Exception: 如果请求失败或解析响应失败，抛出异常。
            """
            async with aiohttp.request(
                    method="POST",
                    url=url,
                    json=body,
                    headers=headers,
                    timeout=self._timeout,
            ) as response:
                try:
                    return await response.json()
                except Exception as e:
                    raise e

        try:
            return await _retry_call(req)
        except Exception as e:
            raise e

    async def create_batch_inference_job(
            self, input_object_key, output_object_key: str, job_name: str = "BI",
            project_name: str = "default"
    ):
        """
        异步创建批量推理任务。
        :param bucket_name: 存储桶名称。
        :param input_object_key: 输入文件的对象键。
        :param output_object_key: 输出文件的对象键。
        :param job_name: 任务名称。默认：BI
        :param project_name: 项目名称。默认：default
        :return: 响应的JSON数据。
        :raises Exception: 如果请求失败或解析响应失败，抛出异常。
        """
        action = "CreateBatchInferenceJob"
        canonicalQueryString = "Action={}&Version={}&X-Account-Id={}".format(
            action, self.version, self.account_id
        )
        url = "https://" + self.domain + "/?" + canonicalQueryString
        extra_param = {
            "Action": action,
            "ProjectName": project_name,
            "Name": job_name or "BI",
            "ModelReference": {
                "FoundationModel": {"Name": self.model, "ModelVersion": self.model_version},
            },
            "InputFileTosLocation": {
                "BucketName": os.environ["TOS_BUCKET"],
                "ObjectKey": input_object_key,
            },
            "OutputDirTosLocation": {
                "BucketName": os.environ["TOS_BUCKET"],
                "ObjectKey": output_object_key or os.getenv("VOLC_BI_OUTPUT"),
            },
            "CompletionWindow": "3d",
        }
        param = self.base_param | extra_param
        print(f"param: {param}")
        payloadSign = utils.get_hmac_encode16(json.dumps(param))
        headers = utils.get_hashmac_headers(
            self.domain,
            self.region,
            self.service,
            canonicalQueryString,
            "POST",
            "/",
            "application/json; charset=utf-8",
            payloadSign,
            self.ak,
            self.sk,
        )
        return await self._call(url, headers, param)

    async def list_batch_inference_jobs(self, job_ids: list[str] = None, phases=None):
        """
        异步列出批量推理任务。
        :param job_ids: 指定ID查询
        :param phases: 任务阶段列表，默认为空列表。
        :return: 响应的JSON数据。
        :raises Exception: 如果请求失败或解析响应失败，抛出异常。
        """
        # 如果phases为None，则初始化为空列表
        if phases is None:
            phases = []

        # 设置操作名称为ListBatchInferenceJobs
        action = "ListBatchInferenceJobs"
        # 构建规范查询字符串，包含操作名称、API版本和账号ID
        canonicalQueryString = "Action={}&Version={}&X-Account-Id={}".format(
            action, self.version, self.account_id
        )
        # 构建请求URL
        url = "https://" + self.domain + "/?" + canonicalQueryString
        # 构建额外参数，包括操作名称、项目名称和过滤器
        extra_param = {
            "Action": action,
            "ProjectName": "default",
            "Filter": {"Phases": phases, "Ids": job_ids},
        }
        # 合并基础参数和额外参数
        param = self.base_param | extra_param

        # 计算请求体的签名
        payloadSign = utils.get_hmac_encode16(json.dumps(param))
        # 获取请求头，包含签名信息
        headers = utils.get_hashmac_headers(
            self.domain,
            self.region,
            self.service,
            canonicalQueryString,
            "POST",
            "/",
            "application/json; charset=utf-8",
            payloadSign,
            self.ak,
            self.sk,
        )
        # 调用_call方法发送请求并返回响应
        return await self._call(url, headers, param)


tos_client = TosClient()
batch_infer_client = BatchInferenceClient()


async def create_batch_inference_job(input: str, output_dir: str = None, job_name: str = None,
                                     project_name: str = "default"):
    bucket_name = os.getenv("TOS_BUCKET")
    # 时间戳
    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
    tos_output = str(Path(os.getenv("VOLC_BI_INPUT", "batch_inference/input")) / f"{dt}.jsonl")
    tos_client.put_object_from_file(bucket_name, tos_output, file_path=input)
    response = await batch_infer_client.create_batch_inference_job(tos_output, output_dir, job_name, project_name)
    return tos_output, response


async def list_batch_inference_jobs(batch_job_ids: list[str] = None):
    response = await batch_infer_client.list_batch_inference_jobs(batch_job_ids)
    return response
