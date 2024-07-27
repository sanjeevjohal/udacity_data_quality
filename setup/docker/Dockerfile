# Base image
FROM apache/airflow:2.4.3-python3.10

USER root
# Install vim and other tools (split to isolate issues)
RUN apt-get update
#RUN apt-get install vim -y # this is not working for docker remote interpreter
#RUN apt-get upgrade -y # this is not working for docker remote interpreter
RUN apt-get install -y apt-utils build-essential unzip gcc default-mysql-server default-libmysqlclient-dev

USER airflow
# Install python dependencies
ADD ./config/requirements.txt .
RUN pip install -r requirements.txt

# Add bash profile
ADD config/.bashrc /home/airflow/.bashrc
