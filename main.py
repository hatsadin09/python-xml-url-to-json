import re
import urllib
import xmltodict
import json
import sys
from urllib.parse import urlparse
import time
from pathlib import Path
# from argparse import ArgumentParser

# parser = ArgumentParser()
# parser.add_argument("-l", "-url", metavar="URL")
# args = vars(parser.parse_args())

Path("./xml_data").mkdir(parents=True, exist_ok=True)
Path("./json_data").mkdir(parents=True, exist_ok=True)

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def js_r(filename: str):
    with open(filename) as f_in:
        return json.load(f_in)


def genfilename(url: str):
    url = url.rstrip('/')
    url_parts = urlparse(url)
    domain = url_parts.netloc.split(".")[-2]
    name = url_parts.path.rpartition('/')[2].split(".")[0]
    return f"{domain}_{name}"


def write_xml(filename: str, data: bytes):
    try:
        with open(f"./xml_data/{filename}.xml", "wb") as f:
            f.write(data)
    except Exception as e:
        print("ERROR: (write_xml)\t", e)


def write_json(filename: str, data: dict):
    try:
        with open(f"./json_data/{filename}.json", 'w', encoding='utf8') as fp:
            json.dump(data, fp, ensure_ascii=False)
    except Exception as e:
        print("ERROR: (write_json)\t", e)


AGRV = sys.argv
CONFIG = js_r("config.json")

if __name__ == "__main__":
    for url in AGRV:
        if re.match(regex, url) is not None:

            filename = f"{int(time.time()*1000)}_{genfilename(url)}"

            try:
                print(f"fetching... {url}")
                file = urllib.request.urlopen(url)
                xml_data = file.read()
                file.close()
            except Exception as e:
                print("ERROR: (request)\t", e)
                break

            data = xml_data

            tuple_config_replace = CONFIG["replace"].items()
            tuple_config_replace = sorted(
                tuple_config_replace, key=lambda x: x[0], reverse=True)

            for k, v in tuple_config_replace:
                if str.encode(k) in data:
                    data = data.replace(str.encode(k), str.encode(v))
                    break

            try:
                print(f"converting...")
                data = xmltodict.parse(data)
            except Exception as e:
                print("ERROR: (xmltodict.parse)\t", e)
                break

            write_xml(filename, xml_data)
            write_json(filename, data)

            print(f"DONE {filename}")

        else:
            pass
