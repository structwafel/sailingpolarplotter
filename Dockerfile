FROM python:3.11-alpine

WORKDIR /code


RUN apk update && apk add --no-cache gcc musl-dev linux-headers
RUN apk add --no-cache python3
RUN python3 -m ensurepip

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app
COPY ./static /code/static
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]