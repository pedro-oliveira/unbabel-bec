FROM python:2

# install app dependencies
COPY batch/requirements.txt .
RUN pip install -r requirements.txt

# create the app directory and set working directory
WORKDIR /app

# copy project files into workdir
COPY batch/ .

CMD ["bash"]
