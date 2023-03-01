FROM python:3.9-slim
RUN apt-get update && \
      apt-get -y install sudo
RUN useradd --create-home appuser
RUN mkdir /myapp && chown -R appuser /myapp
USER appuser
EXPOSE 8080
RUN sudo apt-get update
RUN sudo apt-get install --yes --no-install-recommends git
RUN pip install setuptools
WORKDIR /myapp
#COPY --chown=app:app app-files/ /app
COPY requirements.txt ./myapp
RUN pip install --no-cache-dir --upgrade -r ./myapp/requirements.txt
COPY . .
RUN chmod 777 ./myapp/input && chmod 777 ./myapp/output
ENV PYTHONPATH=$PWD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]