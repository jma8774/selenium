# Parse command line arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--dev", action="store_true", help="Run in dev mode")
parser.add_argument("--url", help="URL to process")
args = parser.parse_args()