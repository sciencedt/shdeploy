import argparse
import os
import sys

# Create the parser
sh_parser = argparse.ArgumentParser(description='Deploy The artifact on AWS')

# Add the arguments
sh_parser.add_argument('artifact', metavar='artifact', type=str, help='Name of the artifact')

# Execute the parse_args() method
args = sh_parser.parse_args()

artifact = args.artifact

print(f"name of the artifact is :{artifact}")
