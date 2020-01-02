FROM python:3.7

# install app dependencies
COPY streaming/requirements.txt .
RUN pip install -r requirements.txt

# create the app directory and set working directory
WORKDIR /app

# copy project files into workdir
COPY streaming/ .

CMD ["bash"]