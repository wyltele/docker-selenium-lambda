FROM umihico/aws-lambda-selenium-python:latest
RUN pip install requests
COPY renew_book.py ./
COPY lambda_function.py ./
CMD [ "lambda_function.lambda_handler" ]
