import os


def handler(event, _):
    print("got event: ", event)


if __name__ == '__main__':
    print("Aws Batch Started")
    table_name = os.environ['table_name']
    bucket_name = os.environ['bucket_name']
    key = os.environ['key']
    print("Aws Batch Started")
    print(table_name, bucket_name, key)
    print("Printing Payload", os.environ['payload'])
