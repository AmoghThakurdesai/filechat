FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 && apt-get install -y python3-pip

RUN pip3 install farm-haystack
RUN pip3 install farm-haystack[inference]

WORKDIR /app
COPY raghaystack.py .
COPY CS_Books .




CMD ["python3","/app/raghaystack.py"]
