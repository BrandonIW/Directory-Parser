import re

def main():
    parser()


def parser():
    regex_dir = re.compile(r'Directory:\s(.*)', re.IGNORECASE)

    with open('../files/Test', 'r') as file:
        hostname = file.name.split('/')[2].split(".")[0]
        with open(f'..\output\Host - {hostname}.csv', 'w') as output:
            output.write(
                'Data Type Found, HostName, File Name, Directory Location, Date, Time, Type, Size, File Extension\n')

            for line in file:
                try:
                    directory = regex_dir.search(line).group(1)
                    directory = directory.replace(',',' ')
                    block_parser(hostname, file, output, directory)

                except AttributeError:
                    continue

# Date Format: 05/05/2022 (\d{2}\/\d{2}\/\d{4})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(.*)
# Date Format: 5/5/2022 (\d{1,2}\/\d{1,2}\/\d{4})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(.*)
# Date Format: 2022-05-05  (\d{4}-\d{2}-\d{2})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(.*)
# Date Format: 1/3/2022 (\d{1,2}\/\d{1,2}\/\d{4})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(.*)

def block_parser(hostname, file, output_file, directory):
    regex = re.compile(r'(\d{4}-\d{2}-\d{2})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(.*)')
    count = 0

    for line in file:
        match = regex.search(line)

        if match:
            date = match.group(1)
            time = match.group(2)
            type = "File"
            name, size, extension = parse_filename(match.group(3))
            if name in [".", ".."]:
                continue

            keywords_found = keyword_finder(line)
            writer(hostname, date, time, type, name, size, extension, directory, output_file, keywords_found)

        elif line == "\n":
            count += 1
            if count == 4:
                return

        else:
            continue


def parse_filename(str):
    regex = re.compile(r'([\d+,]+)\s(.*)$')
    match = regex.search(str)
    size = match.group(1)
    size = size.replace(",", "")
    name = match.group(2)
    extension = match.group(2).split(".")[-1]

    return name, size, extension


def writer(hostname, date, time, type, name, size, extension, directory, output_file, keywords):
    if not keywords:
        keywords = "No keywords found"
    output_file.write(f"{keywords}, {hostname}, {name}, {directory}, {date}, {time}, {type}, {size}, {extension}\n")
    return


def keyword_finder(line):
    keyword_list = ["finance", "marketing", "tax", "technology", "resume"]
    keywords_found = []

    for keyword in keyword_list:
        regex = re.escape(keyword)

        if re.search(regex, line, re.IGNORECASE):
            keywords_found.append(regex)

    return keywords_found


if __name__ == "__main__":
    main()
