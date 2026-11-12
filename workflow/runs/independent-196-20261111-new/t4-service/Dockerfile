FROM harbor.4pd.io/lab-platform/inf/python:3.9

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

# 离线安装 torch/torchvision (CPU) 及依赖（全部 vendor 在构建上下文）
COPY vendor/ /tmp/wheels/
RUN pip install --no-index --find-links=/tmp/wheels \
        "torch==2.6.0+cpu" "torchvision==0.21.0+cpu" \
    && pip cache purge \
    && rm -rf /tmp/wheels

COPY main.py start.sh /app/
COPY model/ /app/model/

RUN chmod +x /app/start.sh

EXPOSE 80
CMD ["/app/start.sh"]
