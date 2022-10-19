import re

"""
Parses files formatted as such:
Directory of W:\\New-Server

08/10/2014  11:58 AM    <DIR>          .
08/10/2014  11:58 AM    <DIR>          ..
08/10/2014  11:58 AM    <DIR>          54HF2
08/10/2014  11:56 AM    <DIR>          9.2.0.4
12/13/2009  04:41 PM             1,042 Capture-New.reg
12/13/2009  08:08 AM            68,199 IDMPrefs-new.fnp
12/13/2009  08:20 AM               912 ODBC-NEW.reg
08/10/2014  11:53 AM    <DIR>          Oracle9.2
12/18/2009  07:39 AM            30,720 Update procedure for new server.doc
02/23/2010  11:21 AM       114,015,626 Update procedure for new serverVer.1.2.doc
               5 File(s)    114,116,499 bytes
"""

def main():
    parser()


def parser():
    regex_dir = re.compile(r'Directory\sof\s(.*)', re.IGNORECASE)

    with open('../files/OGCAP-FILENET01-W.txt', 'r') as file:
        hostname = file.name.split('/')[2].split(".")[0]
        with open(f'..\output\{hostname}.csv', 'w') as output:
            output.write(
                'Data Type Found, HostName, File Name, Directory Location, Date, Time, Type, Size, File Extension\n')

            for line in file:
                try:
                    directory = regex_dir.search(line).group(1)
                    directory = directory.replace(',', ' ')
                    block_parser(hostname, file, output, directory)

                except AttributeError:
                    continue


def block_parser(hostname, file, output_file, directory):
    """
    # Date Format: 05/05/2022 ^(\d{2}\/\d{2}\/\d{4})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(<DIR>)?\s+(.*)
    # Date Format: 5/5/2022 ^(\d{1,2}\/\d{1,2}\/\d{4})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(<DIR>)?\s+(.*)
    # Date Format: 2022-05-05  ^(\d{4}-\d{2}-\d{2})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(<DIR>)?\s+(.*)
    # Date Format: 1/3/2022 ^(\d{1,2}\/\d{1,2}\/\d{4})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(<DIR>)?\s+(.*)
    """
    regex = re.compile(r'^(\d{2}\/\d{2}\/\d{4})\s{2,3}(\d{1,2}:\d{2}\s[AP]M)\s+(<DIR>)?\s+(.*)')
    regex_bytes = re.compile(r'bytes')

    for line in file:
        match = regex.search(line)

        if match:
            date = match.group(1)
            time = match.group(2)
            type = "File" if not match.group(3) else "Directory"
            name, size, extension = parse_filename(type, match.group(4))
            if name in [".", ".."]:
                continue

            keywords_found = keyword_finder(line)
            writer(hostname, date, time, type, name, size, extension, directory, output_file, keywords_found)

        elif regex_bytes.search(line):
            return

        else:
            continue


def parse_filename(type, str):
    if type == "Directory":
        return str, "N/A", "N/A"

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
