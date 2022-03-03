import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=3237)
args = parser.parse_args()
print(args.port)

    

