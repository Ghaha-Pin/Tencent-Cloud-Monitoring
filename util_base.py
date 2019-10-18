import MySQLdb
import util_tencentcloud
import yaml


def select_operator(ips):
    fetch_data = []
    conn = MySQLdb.connect(host='host', port=3306, user='***', passwd='****', db='****')
    format_strings = ','.join(['%s'] * len(ips))
    cursor = conn.cursor()
    sql = 'select  cci.instanceId, cci.privateIpAddresses->>"$[0]" as privateIpAddresses from cmdb_cloud_instance cci where cci.privateIpAddresses->>"$[0]" in (%s)' % format_strings
    cursor.execute(sql, tuple(ips))
    cursor_data = cursor.fetchall()
    for item in cursor_data:
        fetch_data.append({'instanceId': item[0], 'privateIpAddresses': item[1]})
    return fetch_data


async def get_data(**kwargs):
    instanceId_ip = kwargs['instanceId_ip']
    guage_instance = kwargs['guage_instance']
    MetricName = kwargs['MetricName']
    region = kwargs['region']
    Namespace = kwargs['Namespace']
    StartTime = kwargs['StartTime']
    EndTime = kwargs['EndTime']
    api_instance = util_tencentcloud.ClientTencentApi(region=region, page=None, Limit=None)
    data = api_instance.get_monitor_data(Namespace=Namespace, MetricName=MetricName,
                                         InstanceId=instanceId_ip['instanceId'], StartTime=StartTime, EndTime=EndTime)
    label_value = data['DataPoints'][0]['Values'][-1]
    guage_instance.labels(privateIpAddresses=instanceId_ip['privateIpAddresses'], zone='ap-guangzhou',
                          MetricName=MetricName).set(label_value)

def get_yaml_data():
    yaml_file = 'cvm.yaml'
    yaml_data = yaml.load(open(yaml_file), Loader=yaml.FullLoader)
    privateIpAddresses = yaml_data['cvm']['ip']
    region = yaml_data['cvm']['region']
    Namespace = yaml_data['cvm']['Namespace']
    MetricNames = yaml_data['cvm']['MetricName']
    return [privateIpAddresses, region, Namespace, MetricNames]

