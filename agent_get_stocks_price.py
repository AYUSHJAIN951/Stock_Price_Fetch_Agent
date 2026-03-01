import os
import ollama
import yaml
import argparse
import yfinance as yf
import time
import logging
from datetime import datetime
import random
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

print(OLLAMA_ENDPOINT)
print(OLLAMA_MODEL)

ollamaclient=ollama.Client(host=OLLAMA_ENDPOINT)

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser(
        usage=True,
        description="This is a stock price fetcher Agent",
        formatter_class=argparse.HelpFormatter,
        prefix_chars="-",
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler="error",
        add_help=True,
        allow_abbrev=True,
    )

    parser.add_argument(
        "--stock", type=str, help="Stock price to be fetched, fetched once only"
    )

    parser.add_argument(
        "-f",
        "--stocks-file",
        type=str,
        default="stocks.yaml",
        help="Path to the YAML file containing stock tickers (default: stocks.yaml)",
    )

    parser.add_argument(
        "-t",
        "--time-interval",
        type=int,
        default=-1,
        help="Time Interval between Iterations",
    )

    return parser.parse_args()


def get_stock_data(stock_name, **kwargs):
    """
    Fetches the current price for a specific stock ticker.
    :param stock_name: The ticker symbol (e.g., AAPL)
    """
    print(f"-> AI requested data for: {stock_name}")
    # Using real yfinance since you imported it, or keep your random logic:
    value = random.randint(100, 500) 
    return value

def run_stock_check(stock):
    # Correct message format: System prompt first, then User prompt
    msg = [
        {'role': 'system', 'content': 'You are a helpful assistant that uses tools accurately. Only provide arguments defined in the tool.'},
        {'role': 'user', 'content': f"What is the current price for {stock}?"}
    ]
    
    response = ollamaclient.chat(
        model=OLLAMA_MODEL,
        messages=msg,
        tools=[get_stock_data],
    )
    
    if response.message.tool_calls:
        for call in response.message.tool_calls:
            if call.function.name == 'get_stock_data':
                # The **call.function.arguments will now work because of **kwargs in the def
                price = get_stock_data(**call.function.arguments)
                
                log_entry = f"stock_name: {stock} | Price: {price}"
                logging.info(log_entry)
                print(f"Logged: {log_entry}")


def fetch_via_stock_file(path_stocks_file, Interval):
    try:
        with open(path_stocks_file, "r") as file:
            # safe_load converts YAML into a standard Python dictionary
            data = yaml.safe_load(file)

        # Accessing the data
        if Interval is None or Interval == -1:
            Interval = data["interval_minutes"]

    except FileNotFoundError:
        print(f"Error: The file {path_stocks_file} was not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")

    print("==============================================")
    print(Interval)
    print(data["stocks"])
    print("==============================================")

    counter = Interval
    while counter > 0:
        print(f"------------------ {counter} ------------------")
        for stock in data["stocks"]:
            run_stock_check(stock)
        counter -= 1
        if counter > 0:
            print(f"Waiting {Interval} minutes...")
            time.sleep(Interval * 60) # Convert minutes to seconds


def main():
    try:
        args = parse_args()
        print(args)

        if args.stock:
            print("Fetching data once")
            run_stock_check(args.stock)

        else:
            if args.stocks_file:
                stocks_file = args.stocks_file
                Interval = args.time_interval
                if Path(stocks_file).exists():
                    print(f"Checking {stocks_file}")
                    fetch_via_stock_file(path_stocks_file=stocks_file, Interval=Interval)
                else:
                    print(f"File does not exist: {stocks_file}")
    except KeyboardInterrupt as e:
        print("Exiting...")

if __name__ == "__main__":
    main()
