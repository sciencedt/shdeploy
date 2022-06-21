import argparse
import os


def main() -> int:
    print("Working")
    # Create the parser
    sh_parser = argparse.ArgumentParser(description='Deploy The artifact on AWS')
    # Add the arguments
    sh_parser.add_argument('artifact', metavar='artifact', type=str, help='Path of the artifact')
    sh_parser.add_argument('template', metavar='template', type=str, help='Path of the artifact')
    # Execute the parse_args() method
    args = sh_parser.parse_args()
    artifact = args.artifact
    template = args.template
    print("Under Development !!")
    """
    parameter_dict = dict()  # TODO will be loaded from parameter files
    parameter_overrides = " ".join([f"{k}={v}" for k, v in parameter_dict.items()])
    os.system(f"aws cloudformation deploy --template {template} --stack-name my-new-stack --parameter-overrides {parameter_overrides}")
    """
    return 0


if __name__ == '__main__':
    exit(main())
