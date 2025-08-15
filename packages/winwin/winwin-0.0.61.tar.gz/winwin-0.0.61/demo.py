from io import StringIO

import os
import tos

from dotenv import load_dotenv

load_dotenv(override=True)
print(os.environ)

# 从环境变量获取 AK 和 SK 信息。
ak = os.getenv('TOS_ACCESS_KEY')
sk = os.getenv('TOS_SECRET_KEY')
# your endpoint 和 your region 填写Bucket 所在区域对应的Endpoint。# 以华北2(北京)为例，your endpoint 填写 tos-cn-beijing.volces.com，your region 填写 cn-beijing。
endpoint =os.getenv("TOS_ENDPOINT")
region = os.getenv("TOS_REGION")
bucket_name = os.getenv("TOS_BUCKET")
# 对象名称，例如 example_dir 下的 example_object.txt 文件，则填写为 example_dir/example_object.txt
object_key = "test.txt"
content = StringIO('Hello TOS')

file = "demo.py"

print(ak, sk, endpoint, region)

try:
    client = tos.TosClientV2(ak, sk, endpoint, region)
    # 若在上传对象时设置文件存储类型（x-tos-storage-class）和访问权限 (x-tos-acl), 请在 put_object中设置相关参数
    # 用户在上传对象时，可以自定义元数据，以便对对象进行自定义管理
    # result = client.put_object(bucket_name, object_key, content=content, acl=tos.ACLType.ACL_Private, storage_class=tos.StorageClassType.Storage_Class_Standard, meta={'name': '张三', 'age': '20'})
    result = client.put_object_from_file(bucket_name, object_key, file)
    # HTTP状态码
    print('http status code:{}'.format(result.status_code))
    # 请求ID。请求ID是本次请求的唯一标识，建议在日志中添加此参数
    print('request_id: {}'.format(result.request_id))
    # hash_crc64_ecma 表示该对象的64位CRC值, 可用于验证上传对象的完整性
    print('crc64: {}'.format(result.hash_crc64_ecma))
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