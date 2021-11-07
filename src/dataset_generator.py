import argparse
from web_scraper.collector import WebCollector


def parse_args():
    """Parse the arguments."""
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--web_endpoint', type=str, help="Web site to perform the scraping", required=True)
    parser.add_argument('--output_csv_file', type=str, help="Path to the output csv file", required=False)
    parser.add_argument('--show_graphs', help="This flag will generate graphs using the dataset collected", required=False, action='store_true')
    parser.add_argument('--driver_path', type=str, help="Custom path to the selenium firefox driver", required=False)

    args = parser.parse_args()
    if not any((vars(args)).values()):
        parser.error('No arguments provided. add arguments using --argName or check --help options')

    return args


if __name__ == "__main__":
    args = parse_args()
    collector = WebCollector(args.web_endpoint, args.output_csv_file, args.show_graphs)
    collector.start()