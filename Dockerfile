FROM python:3.9-slim
EXPOSE 8080
RUN apt-get update
RUN apt-get install --yes --no-install-recommends git
RUN pip install setuptools
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . .
RUN chmod 777 ./input && chmod 777 ./output
ENV PYTHONPATH=$PWD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]