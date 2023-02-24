#!/usr/bin/env python3
import json
import locale
import sys
import reports
import os
import emails


def load_data(filename):
    """Loads the contents of filename as a JSON file."""
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def format_car(car):
    """Given a car dictionary, returns a nicely formatted name."""
    return "{} {} ({})".format(car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
    """Analyzes the data, looking for maximums.
  Returns a list of lines that summarize the information.
  """
    max_revenue = {"revenue": 0}
    max_sales = {"total_sales": 0}
    sales_by_year = {}

    for item in data:

        item_price = locale.atof(item["price"].strip("$"))
        item_sales = item["total_sales"]
        item_revenue = item_sales * item_price
        if item_revenue > max_revenue["revenue"]:
            item["revenue"] = item_revenue
            max_revenue = item

        if item_sales > max_sales["total_sales"]:
            max_sales = item

        item_year = item["car"]["car_year"]
        sales_by_year[item_year] = sales_by_year.setdefault(item_year, 0) + item_sales

    # set most popular year and amount:
    most_popular_year = sorted(sales_by_year, key=sales_by_year.get, reverse=True)[0]
    most_popular_sales = sales_by_year[most_popular_year]
    summary = [
        "The {} generated the most revenue: ${}".format(
            format_car(max_revenue["car"]), max_revenue["revenue"]
        ),
        "The {} had the most sales: {}".format(
            format_car(max_sales["car"]), max_sales["total_sales"]
        ),
        "The most popular year was {} with {} sales.".format(
            most_popular_year, most_popular_sales
        ),
    ]

    return summary

def cars_dict_to_table(car_data):
    """Turns the data in car_data into a list of lists."""
    table_data = [["ID", "Car", "Price", "Total Sales"]]
    for item in car_data:
        table_data.append(
            [item["id"], format_car(item["car"]), item["price"], item["total_sales"]]
        )
    return table_data


def main(argv):
    """Process the JSON data and generate a full report out of it."""
    data = load_data("../car_sales.json")
    summary = process_data(data)

    # turn this into a PDF report
    report_file = "/tmp/cars.pdf"
    report_title = "Sales summary for last month"
    report_summary = "<br/>".join(summary) + "<br/>"
    report_table = cars_dict_to_table(data)
    reports.generate(report_file, report_title, report_summary, report_table)

    # send the PDF report as an email attachment
    sender = "automation@example.com"
    receiver = "{}@example.com".format(os.environ.get("USER"))
    subject = report_title
    body = "\n".join(summary)
    attachment = report_file
    message = emails.generate(sender, receiver, subject, body, attachment)
    emails.send(message)


if __name__ == "__main__":
    main(sys.argv)


