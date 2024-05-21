FROM python:3-slim-buster
ENV PYTHONUNBUFFERED 1
ENV INFLUXDB_TOKEN=your_token
ENV INFLUXDB_BUCKET=monitoring
ENV INFLUXDB_URL="https://influxdb.farmeurimmo.fr"
ENV INFLUXDB_ORG="Farmeurimmo"
ENV HOSTS_TO_PING=1.1.1.1,8.8.8.8
RUN apt update && apt install -y iputils-ping
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
WORKDIR /app
COPY main.py /app
CMD ["python", "main.py"]