import os
import re
import subprocess
import time

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get('INFLUXDB_TOKEN')
org = os.environ.get('INFLUXDB_ORG')
url = os.environ.get('INFLUXDB_URL')

hosts = os.environ.get('HOSTS_TO_PING').split(',')

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket = os.environ.get('INFLUXDB_BUCKET')

write_api = write_client.write_api(write_options=SYNCHRONOUS)

while True:
    for host in hosts:
        p = subprocess.Popen(['ping', '-q', '-c', '1', '-W', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        output = output.decode("utf-8")
        if p.returncode == 1 and '0 received' in output:
            latency = 0.0
        elif p.returncode == 0 and '1 received' in output:
            latency_pattern = r"rtt min\/avg\/max\/mdev = ([^\/]+)"
            latency = float(re.findall(latency_pattern, output).pop())
        else:
            print(p.returncode)
            print(output)
            raise NotImplementedError('Unknown state')
        print(f'{host} latency: {latency}')
        point = {'measurement': "ping", 'tags': {'host': host}, 'fields': {'latency': latency}}
        write_api.write(bucket=bucket, org=org, record=point)
        time.sleep(0.5)
