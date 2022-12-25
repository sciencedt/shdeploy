""" stack deployment script """
# core imports
import os
import json
import logging

# third party import
import boto3
from botocore.exceptions import ClientError

# local

from shdeploy.constants import PackageConst

logging.basicConfig(level=logging.INFO)


class DeployAction:

    def __init__(self, build_path, skip_build):
        env = json.load(open('deploy.json'))
        self._logger = logging.getLogger(__name__)
        self.cf_client = boto3.client(PackageConst.CLOUDFORMATION)
        self.ecr_client = boto3.client(PackageConst.ECR)
        self.skip_build = skip_build
        self.parameters = []
        self.parameters.append(
            {'ParameterKey': "Stage", 'ParameterValue': env.get(PackageConst.STAGE), 'UsePreviousValue': False,
             'ResolvedValue': env.get(PackageConst.STAGE)})
        self.build_config = {}
        self.artifact = {}
        self.tags = []
        self._repository_name = None
        self._account_id = env.get(PackageConst.ACCOUNT_ID)
        self._region_name = env.get(PackageConst.REGION_NAME)
        self._build_path = build_path
        self._stage = env.get(PackageConst.STAGE)
        self._build = True
        self._template_path = os.path.join(self._build_path, 'cfn/template.json')
        self._cfg_path = os.path.join(self._build_path, "cfn/cfn.config")
        self._stack_name = None
        self._docker_path = None

    def _set_envs(self):
        docker_file = 'dockerfile.lambda'
        if self.artifact.get("DeploymentType") == "batch":
            docker_file = 'dockerfile.batch'
        if not self.artifact.get("DeploymentType"):
            self._build = False
        self._docker_path = os.path.join(self._build_path, docker_file)
        self._stack_name = f"{self.build_config.get('StageName')}-{self._stage}"

    def _read_configuration(self):
        with open(self._cfg_path) as file:
            props = dict(line.strip().split('=', 1) for line in file)
        for k, v in props.items():
            value = v
            param_type, name = k.split(".")
            if name == 'RepositoryName':
                self._repository_name = value
            if param_type == "parameter":
                if name in ("RepositoryName", "FunctionName"):
                    value = f"{value}-{self._stage}"
                self.parameters.append(
                    {'ParameterKey': name, 'ParameterValue': value, 'UsePreviousValue': False,
                     'ResolvedValue': value})
            if param_type == "build":
                self.build_config[name] = value
            if param_type == "artifact":
                self.artifact[name] = value
        self._set_envs()

    def create_stack(self):
        self._logger.info("$$> Stack create in progress")
        template = self._parse_template()
        cf_json = json.loads(template)
        keys = list(cf_json.get("Parameters", {}).keys())
        parameters = [param for param in self.parameters if param.get("ParameterKey") in keys]
        return self.cf_client.create_stack(StackName=self._stack_name,
                                           TemplateBody=template,
                                           Parameters=parameters,
                                           Capabilities=['CAPABILITY_NAMED_IAM'])

    def update_stack(self):
        self._logger.info("$$> Stack update in progress")
        template = self._parse_template()
        cf_json = json.loads(template)
        keys = list(cf_json.get("Parameters").keys())
        parameters = [param for param in self.parameters if param.get("ParameterKey") in keys]
        return self.cf_client.update_stack(StackName=self._stack_name,
                                           Parameters=parameters,
                                           TemplateBody=template,
                                           Capabilities=['CAPABILITY_NAMED_IAM'])

    def delete_stack(self):
        self._logger.info("$$> Stack delete in progress")
        pass

    def build_image(self):
        if not self._build:
            self._logger.info(f"$$> Didn't found build settings skipping build ")
            return
        self._logger.info(f"$$> Building the image from path {self._docker_path}")
        os.system(
            f"aws ecr get-login-password --region {self._region_name} | docker login --username AWS --password-stdin {self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com")
        os.system(f"docker build -t {self._repository_name}-{self._stage} .")
        os.system(
            f"docker buildx build --platform linux/amd64 -f {self._docker_path} -t {self._repository_name}-{self._stage} . --no-cache")
        os.system(
            f"docker tag {self._repository_name}-{self._stage}:latest {self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com/{self._repository_name}-{self._stage}:latest")
        os.system(
            f"docker push {self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com/{self._repository_name}-{self._stage}:latest")

    def get_image_path(self):
        if not self._build:
            return
        self._logger.info("$$>> Getting Image digest")
        resp = self.ecr_client.describe_images(
            repositoryName=f"{self._repository_name}-{self._stage}",
            imageIds=[{'imageTag': 'latest'}])
        image_digest = resp.get("imageDetails")[0].get("imageDigest")
        ecr_path = f"{self._account_id}.dkr.ecr.{self._region_name}.amazonaws.com/{self._repository_name}-{self._stage}@{image_digest}"
        self.parameters.append(
            {'ParameterKey': 'ImageUri', 'ParameterValue': ecr_path, 'UsePreviousValue': False,
             'ResolvedValue': ecr_path})

    def _parse_template(self):
        self._logger.info("$$> Parsing and validating templates")
        with open(self._template_path) as template_file_obj:
            template_data = template_file_obj.read()
        self.cf_client.validate_template(TemplateBody=template_data)
        return template_data

    def _handle_stack_change(self):
        try:
            self.create_stack()
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'AlreadyExistsException':
                self._logger.error("$$> Stack already exists: Updating")
                self.update_stack()
            else:
                self._logger.error(f"$$> Unexpected error: {exc}")
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'ValidationError':
                self._logger.error(f"$$> Validation Error")

    def run_cmd(self):
        try:
            self._read_configuration()
            if not self.skip_build:
                self.build_image()
            else:
                self._logger.info(f"$$> Skipping building image")
            self.get_image_path()
            self._handle_stack_change()
        except Exception as exc:
            self._logger.error(f"$$> Deploy Error: {exc}")
