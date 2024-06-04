# Used for my grafana instance (to get latency of my services)

Still in early development, but it's working for me.

I'm going to make it more generic and add more features.

## Docker installation

First, you need to build the image. I'm going to make an automated build later.

```bash
git clone https://github.com/Farmeurimmo/GrafanaMonitoring.git && cd GrafanaMonitoring && sh build.sh
```

Then, you need to choose the method, for example if you don't have an influxdb instance with grafana, use the 
**All-in-one** method.
If you already have an influxdb instance, use the **Just the monitor** method.

### All-in-one

Here is my `docker-compose.yml` file for my monitoring stack.
I'm using cloudflare tunnel to expose my services via the __cloudflared__ network.
Please change the `INFLUXDB_TOKEN` and `GF_SECURITY_ADMIN_PASSWORD` environment variables.

You will need to set up influxdb and create a bucket with an api token (for INFLUXDB_TOKEN env var).

```yaml
version: '3.8'
services:
  influxdb:
    image: influxdb
    container_name: influxdb
    volumes:
      - /srv/db/influx:/var/lib/influxdb2:rw
    networks:
      - monitoring
      - cloudflared
  grafana:
    image: grafana/grafana
    container_name: grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=CHANGEME
    volumes:
      - /srv/grafana:/var/lib/grafana
    restart: unless-stopped
    networks:
      - cloudflared
      - monitoring
    dns:
      - 1.1.1.1
      - 172.17.0.1
  grafana_monitoring:
    image: grafana-monitoring
    container_name: grafana-monitoring
    environment:
      INFLUXDB_TOKEN: ${INFLUXDB_TOKEN}
      INFLUXDB_BUCKET: monitoring
      INFLUXDB_URL: "https://influxdb.farmeurimmo.fr"
      INFLUXDB_ORG: Farmeurimmo
      HOSTS_TO_PING: 1.1.1.1,8.8.8.8
      HOSTNAME: "hostname"
      INTERVAL: 2
    volumes:
      - /srv/grafana:/var/lib/grafana
    restart: unless-stopped
    network_mode: "host"
    dns:
      - 1.1.1.1
      - 172.17.0.1
networks:
  cloudflared:
    external: true
  monitoring:
    name: "monitoring"
```

### Just the monitor

```yaml
version: '3.8'
services:
  grafana_monitoring:
    image: grafana-monitoring
    container_name: grafana-monitoring
    environment:
      INFLUXDB_TOKEN: ${INFLUXDB_TOKEN}
      INFLUXDB_BUCKET: monitoring
      INFLUXDB_URL: "https://influxdb.farmeurimmo.fr"
      INFLUXDB_ORG: Farmeurimmo
      HOSTS_TO_PING: 1.1.1.1,8.8.8.8
      HOSTNAME: "hostname"
      INTERVAL: 2
    volumes:
      - /srv/grafana:/var/lib/grafana
    restart: unless-stopped
    network_mode: "host"
    dns:
      - 1.1.1.1 # Cloudflare
      - 172.17.0.1 # Docker because I use tailscale
```