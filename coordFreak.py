import requests
import re
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--limits", nargs="*", type=int, help="Comma separated "
                    "list of limitations to query from the part 90 limitations. If not specified, all frequencies"
                    "will be returned. Example: -l 17,10,58")
parser.add_argument("-i", "--itinerant", action="store_true", help="Query for itinerant frequencies only.")
parser.add_argument("-c", "--coordinators", nargs="*", help="Comma separated list"
                    "list of frequency coordinators. Valid choices are:"
                    "\r\n\tIP: Petroleum\r\n\tIW: Power\r\n\tLR: Railroad\r\n\tLA: Automobile Emergency\r\n"
                    "-c IP")
headers = {"User-Agent": "coordFreak/0.0.1"}
fcc_url = ("https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-47?chapter=I&subchapter=D&part=90"
           "&subpart=C&section=90.35")
req = requests.get(fcc_url, headers=headers)
soup = BeautifulSoup(req.content, "html.parser")
numbers = re.compile(r'^\s\([0-9]+\)')
combined_filter = re.compile(r'^\s\([0-9]+\)\s')
index_filter = re.compile(r'[\s()]')
table = soup.find("table", class_="gpo_table")
table_header = table.find("thead").find_all("th")
rows = table.find_all("tr")
limitations = soup.find("div", id="p-90.35(c)").find_all("div",
                                                         {"id": re.compile(r'p-90\.35\(c\)\([0-9]+\)')})
limits_filter = re.compile(r'\s|\.')
num_limitations = None
coordinators_filter = re.compile(r'\s')
coordinators = soup.find("div", id="p-90.35(b)(2)(iv)").find("div", class_ = "extract")
coordinators = coordinators.find_all("p", class_ = "flush-paragraph-1")
ditto_filter = re.compile(r'[.]*do')
parsed_args = parser.parse_args()


def parse_coordinators(coorders):
    c_dict = {}
    for c in coorders:
        c_split = c.text.split(sep="—")
        c_dict[c_split[0]] = c_split[1].rstrip("\n")
    return c_dict


def parse_limitations(limits):
    parsed_limits = {}
    for l in limits:
        limit_index = re.search(numbers, l.text)
        if limit_index:
            limit_index_clean = re.sub(index_filter, '', limit_index.group())
            limit_clean = re.sub(combined_filter, '', l.text)
            parsed_limits[int(limit_index_clean)] = limit_clean
    return parsed_limits


def parse_frequencies(freq_table):
    mhz = False
    freq_rows = []
    for f in freq_table:
        row = []
        for td in f.find_all("td"):
            match td.text:
                case str(s) if "Kilohertz" in s:
                    mhz = False
                    continue
                case str(s) if "Megahertz" in s:
                    mhz = True
                    continue
            row.append(td.text)
        row.append(mhz)
        freq_rows.append(row)
    return freq_rows


def hydrate_table(tbl, limits, coorders):
    freqs = []
    radio = None
    for r in tbl:
        row = {}
        for column in r:
            pos = r.index(column)
            match pos:
                case 0:
                    row["frequency"] = column
                case 1:
                    if re.match(ditto_filter, column):
                        row["class"] = radio
                    else:
                        radio = column
                        row["class"] = radio
                case 2:
                    limits_dict = {}
                    column = re.sub(limits_filter, "", column)
                    for limit in column.split(sep=","):
                        if limit:
                            limits_dict[int(limit)] = limits.get(int(limit))
                    row["limitations"] = limits_dict
                case 3:
                    coordinators_dict = {}
                    column = re.sub(limits_filter, "", column)
                    print("col: {}".format(column))
                    if column:
                        for coord in column.split(sep=','):
                            coordinators_dict[coord] = coorders.get(coord)
                            print("Coord: {}".format(coord))
                    row["coordinators"] = coordinators_dict
                    print("coord list: {}".format(coordinators_dict))
                case 4:
                    row["mhz"] = column
        freqs.append(row)
    return freqs


def main():
    parsed_limits = parse_limitations(limitations)
    parsed_coordinators = parse_coordinators(coordinators)
    parsed_frequencies = parse_frequencies(rows[2:])
    full_table = hydrate_table(parsed_frequencies, parsed_limits, parsed_coordinators)
    limits = parsed_args.limits
    itinerant = parsed_args.itinerant
    print(parsed_coordinators)
    for row in full_table:
        limits_dict = row.get("limitations")
        coordinators_dict = row.get("coordinators")
        for 
        #print(coordinators_list)


    # for row in full_table:
    #     l_dict = row.get("limitations")
    #     if l_dict:
    #         if (l_dict.get(17) or l_dict.get(10) or l_dict.get(58)) and not row.get("coordinators"):
    #             print("IT Freq: {}".format(row.get("frequency")))


if __name__ == "__main__":
    main()
