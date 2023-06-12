import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--url', help='URL Endpoint')
parser.add_argument('--count', help='Number of Books to Add')
args = parser.parse_args()

count = int(args.count)

while (count > 0):
    # Ask Input
    title = input("Title of the Book: ")
    author = input("Authors: ")
    description = input("Description: ")
    barcode_id = int(input("Barcode ID: "))

    # Pack it into a dictionary / json
    # payload = {}
    # payload = {
    #     "bookId": barcode_id,
    #     "title": title,
    #     "author": author,
    #     "description": description
    # }
    # print(payload)
    # Send the request
    res = requests.post(args.url, data={
        "bookId": barcode_id,
        "title": title,
        "author": author,
        "description": description
    })

    # Print the Response
    print(res.json())
    count = count - 1
