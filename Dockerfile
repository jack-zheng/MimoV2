# Use an official Python runtime as a parent image
FROM python:3.6

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Set proxy server, replace host:/port with values for your servers
#ENV http_proxy http://proxy.XX.com:8080
#ENV https_proxy http://proxy.xx.com:8080

# Install any needed packages specified in requirements.txt
# Linux: RUN pip install -i http://pypi.douban.com/simple --trusted-host pypi.douban.com -r requirements.txt
RUN pip install -i http://pypi.douban.com/simple -r requirements.txt


# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "run.py"]
