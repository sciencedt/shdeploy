import argparse
from shdeploy.cfn_action import DeployAction


def main() -> int:
    # Create the parser
    sh_parser = argparse.ArgumentParser(description='Deploy The artifact on AWS')
    # Add the arguments
    sh_parser.add_argument('--build_path', metavar='--build_path', type=str, help='Path of the artifact')
    sh_parser.add_argument('--stage', metavar='--stage', type=str, help='Cf stack')
    # Execute the parse_args() method
    args = sh_parser.parse_args()
    build_path = args.build_path
    stage = args.stage
    deploy = DeployAction(build_path=build_path, stage=stage)
    deploy.run_cmd()
    return 0


if __name__ == '__main__':
    exit(main())
