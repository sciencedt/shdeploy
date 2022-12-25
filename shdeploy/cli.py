""" cli entrypoint """
import argparse
from shdeploy.cfn_action import DeployAction


def str2bool(v):
    """ str to bool convert function """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main() -> int:
    # Create the parser
    sh_parser = argparse.ArgumentParser(description='Deploy The artifact on AWS')
    # Add the arguments
    sh_parser.add_argument('--build_path', metavar='--build_path', type=str, help='Path of the artifact')
    sh_parser.add_argument('--skip_build', metavar='--skip_build', type=str2bool, help='Whether to skip building image', default=False)
    sh_parser.add_argument('--account_id', metavar='--account_id', type=str, help='AWS Account id')
    sh_parser.add_argument('--region_name', metavar='--region_name', type=str, help='AWS region name')
    # Execute the parse_args() method
    args = sh_parser.parse_args()
    build_path = args.build_path
    skip_build = args.skip_build
    account_id = args.account_id  # to override default value
    region_name = args.region_name  # to override env value
    deploy = DeployAction(build_path=build_path, skip_build=skip_build)
    deploy.run_cmd()
    return 0


if __name__ == '__main__':
    exit(main())
