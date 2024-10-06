FROM umihico/aws-lambda-selenium-python:latest

COPY renew_book.py ./
COPY lambda_function ./
CMD [ "lambda_function.lambda_handler" ]
