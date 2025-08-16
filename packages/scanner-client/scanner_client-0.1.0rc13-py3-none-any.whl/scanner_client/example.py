#!/usr/bin/env python3

import asyncio
import os
import time

from .scanner import Scanner, AsyncScanner


def query_example():
    # Create Scanner client
    scanner = Scanner(
        api_url=os.environ["SCANNER_API_URL"],
        api_key=os.environ["SCANNER_API_KEY"],
    )

    # Run non-blocking query
    response = scanner.query.start_query_and_return_results(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    )
    print(response.results)

    # Run blocking query
    response = scanner.query.blocking_query(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    )
    print(response.results)


async def async_query_example():
    # Create AsyncScanner client
    scanner = AsyncScanner(
        api_url=os.environ["SCANNER_API_URL"],
        api_key=os.environ["SCANNER_API_KEY"],
    )

    # Run non-blocking query
    response = await scanner.query.start_query_and_return_results(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    )
    print(response.results)

    # Run blocking query
    response = await scanner.query.blocking_query(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    )
    print(response.results)


def main():
    #query_example()
    asyncio.run(async_query_example())
