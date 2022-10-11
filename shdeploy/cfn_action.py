import boto3
import os

from botocore.exceptions import ClientError


class DeployAction:

    def __init__(self, build_path, stage):
        self.cf_client = boto3.client("cloudformation")
        self.ecr_client = boto3.client("ecr")
        self.parameters = []
        self.build_config = {}
        self.tags = []
        self._repository_name = "aws_batch"
        self._account_id = ""
        self._region_name = "us-east-1"
        self._build_path = build_path
        self._stage = stage
        self._template_path = os.path.join(self._build_path, 'cfn/template.json')
        self._cfg_path = os.path.join(self._build_path, "cfn/cfn.config")
        self._stack_name = None
        self._docker_path = os.path.join(self._build_path, 'Dockerfile')

    def _read_configuration(self):
        with open(self._cfg_path) as file:
            props = dict(line.strip().split('=', 1) for line in file)
        for k, v in props.items():
            param_type, name = k.split(".")
            if param_type == "parameter":
                self.parameters.append(
                    {'ParameterKey': name, 'ParameterValue': v, 'UsePreviousValue': False, 'ResolvedValue': v})
            if param_type == "build":
                self.build_config[name] = v
        self._stack_name = f"{self.build_config.get('StageName')}-{self._stage}"

    def create_stack(self):
        return self.cf_client.create_stack(StackName=self._stack_name,
                                           TemplateBody=self._parse_template(),
                                           Parameters=self.parameters, Capabilities=['CAPABILITY_NAMED_IAM'])

    def update_stack(self):
        return self.cf_client.update_stack(StackName=self._stack_name,
                                           Parameters=self.parameters,
                                           TemplateBody=self._parse_template(),
                                           Capabilities=['CAPABILITY_NAMED_IAM'])

    def delete_stack(self):
        pass

    def build_image(self):
        os.system(
            f"aws ecr get-login-password --region {self._region_name} | docker login --username AWS --password-stdin {self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com")
        os.system(f"docker build -t {self._repository_name} .")
        os.system(
            f"docker buildx build --platform linux/amd64 -f {self._docker_path} -t {self._repository_name} . --no-cache")
        os.system(
            f"docker tag {self._repository_name}:latest {self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com/{self._repository_name}:latest")
        os.system(
            f"docker push {self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com/{self._repository_name}:latest")

    def get_image_path(self):
        print(f"getting image digest")
        resp = self.ecr_client.describe_images(repositoryName='aws_batch', imageIds=[{'imageTag': 'latest'}])
        image_digest = resp.get("imageDetails")[0].get("imageDigest")
        ecr_path = f"{self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com/{self._repository_name}@{image_digest}"
        self.parameters.append({'ParameterKey': 'ImageUri', 'ParameterValue': ecr_path, 'UsePreviousValue': False,
                                'ResolvedValue': ecr_path})

    def _parse_template(self):
        print(f"Parsing template")
        with open(self._template_path) as template_file_obj:
            template_data = template_file_obj.read()
        self.cf_client.validate_template(TemplateBody=template_data)
        return template_data

    def run_cmd(self):
        try:
            self._read_configuration()
            self.build_image()
            self.get_image_path()
            self.create_stack()
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'AlreadyExistsException':
                print("Stack already exists: Updating")
                self.update_stack()
            else:
                print("Unexpected error: %s" % exc)
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'ValidationError':
                print("Hello")
