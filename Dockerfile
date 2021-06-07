FROM bitnami/kubectl:1.21


USER root
# install python
RUN apt-get update -y
RUN apt-get install python3 -y

# copy over python source files n stuff
ADD main.py /app/main.py

ENTRYPOINT ["python3", "/app/main.py"]