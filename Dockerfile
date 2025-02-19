FROM python:3.9-slim 

ENV TZ=Asia/Shanghai

RUN set -ex \
  && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  && pip install fastapi httpx requests uvicorn bs4 

COPY . /opt
WORKDIR /opt

CMD ["python", "main.py"]
