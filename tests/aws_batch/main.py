import argparse


def handler(event, _):
    print("got event: ", event)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--name", help="name of the job", type=str, default='default job')
    args = vars(parser.parse_args())
    print("Initial Arguments", args)
    event = dict(body=args)
    handler(event, {})

