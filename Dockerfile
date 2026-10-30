FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates wget git vim nano less tzdata \
        procps iproute2 net-tools dnsutils bash-completion \
        unzip tar gzip xz-utils sudo python3 python3-pip \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# 安装脚本测试用的自检服务：8000 端口输出环境信息
RUN mkdir -p /data /opt/test
COPY serve.py /opt/test/serve.py

ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1

CMD ["python3", "/opt/test/serve.py"]
