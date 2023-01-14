import re

"""
Parses the files formatted as such:
    Directory: C:\


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----       2021-12-20  10:04 AM             21 __output   

"""

def main():
    """ Build Generator Object. Open files. Loop through Generator until EOF and write to output file """
    directory = ""

    with open("../files/Done - File.txt", "r", encoding="UTF-8") as file:
        hostname = file.name.split('/')[2].split(".")[0]
        generator_obj = record_generator(file)

        with open(f'..\output\Host - {hostname}.csv', 'w') as output:
            output.write(
                'Data Type Found, HostName, File Name, Directory Location, Date, Time, Type, Size, File Extension\n')

            while True:
                try:
                    line = next(generator_obj)
                    if line[1]:
                        directory = line[0]
                        continue
                    line_formatter(line[0], output, directory, hostname, "file")

                except StopIteration:
                    quit(0)


def record_generator(fileobj):
    """
    Generator that pushes out a complete line of text from the input file. Will also account for lines
    that contain file names that are > 1 line and merge them into a single line. Uses date column to
    confirm if it's a line relating to a new file. Use regexs below to edit as needed depending on
    date format.

    05/05/2022 \d{2}\/\d{2}\/\d{4}
    5/5/2022 \d{1,2}\/\d{1,2}\/\d{4}
    2022-05-05  \d{4}-\d{2}-\d{2}
    """
    regex_date = re.compile(r'\d{4}-\d{2}-\d{2}')
    regex_append = re.compile(r'\s+\w+')
    regex_dir = re.compile(r'Directory:\s(.*)', re.IGNORECASE)
    regex_append_dir = re.compile(r'\s*\w+')

    record = ""
    directory = ""

    for line in fileobj:
        match_new_file = regex_date.search(line)
        match_append_name = regex_append.search(line)

        try:
            match_directory_name = regex_dir.search(line)
            if match_directory_name:
                directory = match_directory_name.group(1)
                directory = directory.replace(',', ' ')
                continue

            elif regex_append_dir.search(line) and directory:
                directory = f"{directory}\\{line}"
                yield directory, True
                directory = ""
                continue

            elif not regex_append_dir.search(line) and directory:
                yield directory, True
                directory = ""
                continue

        except AttributeError:
            pass

        if match_new_file and record:
            yield record, False
            record = f"{line}"

        elif record and line == "\n":
            yield record, False
            record = ""

        elif match_new_file:
            record = f"{line}"
            continue

        elif match_append_name and record:
            record = f"{record}{line}"
            continue

        else:
            continue


def line_formatter(line, output, directory, hostname, type):
    """ Formats the output from the generator to pull out columns for Excel """
    line = line.replace("\n", "").split()
    line = line[1:]
    line[1:3] = ["".join(line[1:3])]
    line[3:] = [" ".join(line[3:])]

    directory = directory.replace("\n", "")

    date, time, size, name, ext = line[0], line[1], line[2], line[3], line[3].split(".")[-1]
    keywords = keyword_finder(name)

    writer(hostname, date, time, type, name, size, ext, directory, output, keywords)


def keyword_finder(filename):
    """ Searches filename for keywords """
    keyword_list = ["INSERT KEYWORDS"
                    ]

    # Acronym Regex
    regex_SIN_ac = re.compile(r'\bSIN\b', re.IGNORECASE)
    regex_T4 = re.compile(r'\bT4\b', re.IGNORECASE)
    regex_T4A = re.compile(r'\bT4A\b', re.IGNORECASE)
    regex_ROE = re.compile(r'\bROE\b', re.IGNORECASE)
    regex_RE = re.compile(r'\bRE\b', re.IGNORECASE)
    regex_VEF = re.compile(r'\bVEF\b', re.IGNORECASE)
    regex_PAD = re.compile(r'\bPAD\b', re.IGNORECASE)
    regex_DIN = re.compile(r'\bDIN\b', re.IGNORECASE)
    regex_EFT = re.compile(r'\bEFT\b', re.IGNORECASE)
    regex_AMEX = re.compile(r'\bamex\b', re.IGNORECASE)

    regex_dictionary = {
        "ROE":regex_ROE,
        "DIN":regex_DIN,
        "SIN-Acronym":regex_SIN_ac,
        "T4":regex_T4,
        "T4A":regex_T4A,
        "Pre-Authorized Debit":regex_PAD,
        "Electronic Funds Transfer":regex_EFT,
        "AMEX":regex_AMEX,
        "Record of Employment":regex_RE,
        "Electronic Funds Transfer (French)":regex_VEF
    }

    keywords_found = ""

    for keyword in keyword_list:
        regex = re.escape(keyword)

        if re.search(regex, filename, re.IGNORECASE):
            keywords_found = f"{keywords_found} | {regex}"

    for name, regex in regex_dictionary.items():
        if regex.search(filename):
            keywords_found = f"{keywords_found} | {name}"

    return keywords_found


def writer(hostname, date, time, type, name, size, extension, directory, output_file, keywords):
    """ Writes to output file in csv format """
    extension_blacklist = ['dll', 'manifest', 'rtf', 'config', 'msi', 'cab', 'dmp', 'cur', 'cpl', 'cfg', 'bak', 'ini',
                           'tmp', 'sys', 'drv', 'ps1', 'psd1']
    directory_blacklist = "C:\\Windows\\"

    if (extension in extension_blacklist) or (directory_blacklist in directory):
        return

    if not keywords:
        #return
        keywords = "No keywords found"
    directory = directory.replace(',', ' ')
    name = name.replace(',', ' ')
    output_file.write(f"{keywords}, {hostname}, {name}, {directory}, {date}, {time}, {type}, {size}, {extension}\n")
    return


if __name__ == "__main__":
    main()
