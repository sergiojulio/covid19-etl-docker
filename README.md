# covid19-etl-docker
Este repositorio contiene los archivos necesarios para la creación de una
aplicación contenerizada (Docker) que es ejecutada en Google Cloud Platform (GCP) mediante el servicio 
Cloud Run y Cloud Scheduler. La ejecución de la aplicación clona el 
[repositorio Covid19 ETL](https://github.com/sergiojulio/covid19-etl), luego ejecuta
su funcion *principal* generando una serie de archivos de salida. En el segundo paso, se clona 
el [repositorio Covid19 Chile](https://github.com/sergiojulio/covid19-chile), 
los archivos generados en la ejecución pasada son copiados
en el repositorio Covid19 Chile y luego se realiza un push con los cambios generados. El objetivo 
del proyecto es la automatización del proceso que se realizaba de forma manual.

![Alt text](https://github.com/sergiojulio/doc-covid19-chile-pipeline/blob/master/covid_19_chile_etl_architecture.png?raw=true "architecture diagram")