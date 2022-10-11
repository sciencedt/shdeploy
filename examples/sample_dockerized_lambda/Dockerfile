FROM public.ecr.aws/lambda/python:3.8

COPY examples/sample_dockerized_lambda/ ${LAMBDA_TASK_ROOT}/sample_dockerized_lambda
RUN pip install -r sample_dockerized_lambda/requirements.txt


# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "sample_dockerized_lambda.app.handler" ]