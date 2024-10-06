FROM umihico/aws-lambda-selenium-python:latest

COPY renew_book.py ./
COPY lambda_function.py ./
CMD [ "lambda_function.lambda_handler" ]
