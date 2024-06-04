import os
import re
import subprocess
import time

import influxdb_client
import psutil
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get('INFLUXDB_TOKEN')
org = os.environ.get('INFLUXDB_ORG')
url = os.environ.get('INFLUXDB_URL')
hostname = os.environ.get('VPS_NAME')

hosts = os.environ.get('HOSTS_TO_PING').split(',')

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket = os.environ.get('INFLUXDB_BUCKET')

write_api = write_client.write_api(write_options=SYNCHRONOUS)

start = 0
INTERVAL = float(os.environ.get('INTERVAL'))

last_network = 0
last_network_in = 0
last_network_out = 0

while True:
    if time.time() - start < INTERVAL:
        time.sleep(0.2)
        continue
    start = time.time()
    for host in hosts:
        p = subprocess.Popen(['ping', '-q', '-c', '1', '-W', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        output = output.decode("utf-8")
        if p.returncode == 1 and '0 received' in output:
            latency = 0.0
        elif p.returncode == 0 and '1 received' in output:
            latency = float(re.findall(r"rtt min/avg/max/mdev = ([^/]+)", output).pop())
        else:
            print(p.returncode)
            print(output)
            raise NotImplementedError('Unknown state')
        write_api.write(bucket=bucket, org=org,
                        record={'measurement': "ping", 'tags': {'host': host, 'machine': hostname}, 'fields': {'latency': latency}})

    net = psutil.net_io_counters()
    time_diff = time.time() - last_network
    network_in = (net.bytes_recv - last_network_in) * 8 / (1024 ** 2 * time_diff)
    network_out = -(net.bytes_sent - last_network_out) * 8 / (1024 ** 2 * time_diff)
    if network_in < 0:
        network_in *= -1
    if network_out > 0:
        network_out *= -1
    write_api.write(bucket=bucket, org=org, record={'measurement': "network", 'tags': {'host': 'localhost', 'machine': hostname},
                                                    'fields': {'in': round(network_in, 4),
                                                               'out': round(network_out, 4)}})
    last_network_in = net.bytes_recv
    last_network_out = net.bytes_sent
    last_network = time.time()
    time.sleep(INTERVAL - (time.time() - start))
