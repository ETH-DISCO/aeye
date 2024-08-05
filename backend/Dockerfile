FROM python:3.10

# Set the working directory
WORKDIR /code

# Copy requirements.txt to the working directory
COPY ./requirements.txt requirements.txt

# Run pip install to install all dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy start.sh to the working directory
COPY ./start.sh start.sh

# Set execution permission for start.sh
RUN chmod +x ./start.sh

CMD ["bash", "-c", "./start.sh"]
