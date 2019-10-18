from configparser import ConfigParser
import logging, os, json

logger = logging.getLogger(__name__)

from tencentcloud.common import credential
from tencentcloud.common.profile import client_profile
from tencentcloud.common.profile import http_profile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的client models。
from tencentcloud.cvm.v20170312 import cvm_client, models
from tencentcloud.monitor.v20180724 import monitor_client, models as monitor_models

# from aiops_demo.settings import BASE_DIR

from QcloudApi.qcloudapi import QcloudApi


def get_config_secret():
    try:
        cfg = ConfigParser()
        secret_path = os.path.join('***', 'config/tencentcloud.ini')
        # secret_path = os.path.join(BASE_DIR, 'config/tencentcloud.ini')
        cfg.read(secret_path)
        secretId = cfg.get('tencentclound', 'secretId')
        secretKey = cfg.get('tencentclound', 'secretKey')
    except Exception as e:
        secretId = None
        secretKey = None
        logger.error(e)
        logger.error('there is error in getting config tentcentcloud.ini')
    return [secretId, secretKey]


class ClientTencentApi(object):
    """ client tencent api"""

    def __init__(self, region, page, Limit):
        self.region = region
        self.Offset = ((int(page) - 1) * Limit) if page else None
        self.Limit = Limit if Limit else None

        secretId, secretKey = get_config_secret()
        try:
            self.secretId = secretId
            self.secretKey = secretKey

            # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
            cred = credential.Credential(secretId=self.secretId,
                                         secretKey=self.secretKey)
            self.cred = cred

            # 实例化一个client选项，可选的，没有特殊需求可以跳过。
            hp = http_profile.HttpProfile()
            hp.reqMethod = "POST"
            cp = client_profile.ClientProfile()
            cp.signMethod = "TC3-HMAC-SHA256"
            cp.httpProfile = hp
            self.cp = cp
            self.client = cvm_client.CvmClient(self.cred, self.region, self.cp)
            self.monitor = monitor_client.MonitorClient(credential=self.cred, region=self.region)
        except TencentCloudSDKException as e:
            logger.error(e)
            logger.error('there is wrong in getting tencent api credential init')

    def get_describe_regions(self):
        """查询地域列表"""
        req = models.DescribeRegionsResponse()
        resp = self.client.DescribeRegions(req)
        data = json.loads(resp.to_json_string())
        data['results'] = data.pop('RegionSet')
        data['count'] = data.pop('TotalCount')
        return data

    def get_describe_zones(self):
        """查询可用区列表"""
        req = models.DescribeZonesResponse()
        resp = self.client.DescribeZones(req)
        data = json.loads(resp.to_json_string())
        data['results'] = data.pop('ZoneSet')
        data['count'] = data.pop('TotalCount')
        return data

    def get_describe_instances(self):
        """获取实例列表"""
        # req = models.DescribeInstancesResponse()
        req = models.DescribeInstancesRequest()
        params = {"Offset": self.Offset, "Limit": self.Limit}
        req.from_json_string(json.dumps(params))
        resp = self.client.DescribeInstances(req)
        data = json.loads(resp.to_json_string())
        data['results'] = data.pop('InstanceSet')
        data['count'] = data.pop('TotalCount')
        return data

    def get_monitor_data(self, Namespace, MetricName, InstanceId, StartTime, EndTime):
        """获取监控数据"""
        req = monitor_models.GetMonitorDataRequest()
        instance_list = []
        # for item in InstanceIds:
        instance_list.append({'Dimensions': [{'Name': 'InstanceId', 'Value': InstanceId}]})
        params = {"Namespace": Namespace, "MetricName": MetricName, "Instances": instance_list, "StartTime": StartTime,
                  "EndTime": EndTime}
        req.from_json_string(json.dumps(params))
        resp = self.monitor.GetMonitorData(req)
        data = json.loads(resp.to_json_string())
        return data


class AccountTencentApi(object):

    def __init__(self):
        # self.region = region

        # 设置需要加载的模块
        self.module = 'account'

        # 对应接口的接口名，请参考wiki文档上对应接口的接口名
        self.action = 'DescribeProject'

        secretId, secretKey = get_config_secret()

        # 云API的公共参数
        self.config = {
            # 'Region': self.region,
            'secretId': secretId,
            'secretKey': secretKey,
            'method': 'GET',
            'SignatureMethod': 'HmacSHA1',
            # 只有cvm需要填写version，其他产品不需要
            # 'Version': '2017-03-12'
        }

        # 接口参数，根据实际情况填写，支持json
        # 例如数组可以 "ArrayExample": ["1","2","3"]
        # 例如字典可以 "DictExample": {"key1": "value1", "key2": "values2"}
        self.action_params = {
            'allList': 1,
        }

    def get_project(self):
        try:
            service = QcloudApi(self.module, self.config)

            # 请求前可以通过下面几个方法重新设置请求的secretId/secretKey/Region/method/SignatureMethod参数
            # 重新设置请求的Region
            # service.setRegion('ap-shanghai')

            # 打印生成的请求URL，不发起请求
            print(service.generateUrl(self.action, self.action_params))
            # 调用接口，发起请求，并打印返回结果
            result = json.loads(service.call(self.action, self.action_params).decode())
            result['results'] = result.pop('data')
            return result
        except Exception as e:
            import traceback
            print('traceback.format_exc():\n%s' % traceback.format_exc())


if __name__ == '__main__':
    # 获取地域列表
    # api_instance = ClientTencentApi(region=None)
    # print(api_instance.get_describe_regions())

    # 获取区列表
    # api_instance = ClientTencentApi(region='ap-guangzhou')
    # print(api_instance.get_describe_zones())

    # 获取实例列表
    # api_instance =ClientTencentApi(region='ap-guangzhou', page=1)
    # print(api_instance.get_describe_instances())

    # 获取项目列表
    api_instance = AccountTencentApi(region='ap-guangzhou')
    api_instance.get_project()
