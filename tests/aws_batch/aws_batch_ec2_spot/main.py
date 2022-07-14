import os


def handler(event, _):
    print("got event: ", event)


if __name__ == '__main__':
    payload = os.getenv('payload', {})
    vpc = os.getenv('VPC', 'test')
    print("payload", payload)
    print("vpc", vpc)
    print("payload type", type(payload))

    event = dict(payload=payload, vpc=vpc)
    handler(event, {})

