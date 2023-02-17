FROM python:3.9
ENV PORT 8080
ENV HOST 0.0.0.0
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "./main.py" ]
# --------------------------------------------------------------------
FROM python:3.9-slim
EXPOSE 8080
RUN apt-get update
RUN apt-get install --yes --no-install-recommends git
RUN pip install setuptools
# RUN git clone https://github.com/sergiojulio/covid19-etl-docker.git
WORKDIR /covid19-etl-docker
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
RUN chmod 777 /covid19-etl-docker/input && chmod 777 /covid19-etl-docker/output
ENV PYTHONPATH=$PWD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]