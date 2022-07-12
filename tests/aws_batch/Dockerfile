FROM python:3.8

ENV source_path /opt/program/source
RUN mkdir -p ${source_path}



#Set up source
COPY ./  ${source_path}
# RUN pip install -r ${source_path}/requirements.txt -t ${source_path}
# RUN pip install  awscli --upgrade

#Set up working directory
WORKDIR ${source_path}

#Default arguments to run test
CMD ["python", "main.py"]