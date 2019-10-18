import asyncio
import datetime
import prometheus_client
from prometheus_client import Gauge
from flask import Response, Flask
import util_base

app = Flask(__name__)

guage_instance = Gauge("QCE_CVM", "monitor data of cvm, ", ['privateIpAddresses', 'zone', 'MetricName'])


@app.route("/metrics")
def r_value():
    EndTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    StartTime = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    tasks = []
    ips, region, Namespace, MetricNames = util_base.get_yaml_data()
    instanceId_ip_list = util_base.select_operator(ips)
    for each_instanceId_ip in instanceId_ip_list:
        for MetricName in MetricNames:
            kwargs = {"instanceId_ip": each_instanceId_ip, 'guage_instance': guage_instance, 'MetricName': MetricName,
                      'region': region, 'Namespace': Namespace, 'StartTime': StartTime, 'EndTime': EndTime}
            tasks.append(util_base.get_data(**kwargs))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    finally:
        loop.close()
    return Response(prometheus_client.generate_latest(guage_instance), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
