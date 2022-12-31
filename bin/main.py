import re


def main():
    parser()


def parser():
    """ Keeps a running dictionary w/ each key being equivalent to a depth value based on the number of '|||' strings.
    Moves through the file and continually updates each dictionary key value with the respective depth of a parsed
    directory. When a file is reached, a depth counter is taken based on the number of '|||' strings, e.g. 3, and
    the directory will be created from keys 0-2 for a file w/ depth counter of 3. If a file has a depth counter of 5
    the directory will be created from keys 0-4 etc. """

    directory_path = {
        0: "",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: "",
        8: "",
        9: "",
        10: ""
    }
    with open(f'..\output\Output.csv', 'w', encoding="UTF-8") as output:
        output.write('Keywords, File Name, Directory Location, File Extension\n')

        with open('../files/RS_POE_Revised.txt', 'r', encoding="UTF-8") as file:
            full_file = file.readlines()

            for line in full_file:
                line = line.replace("\n", "")  # Get rid of the \n

                line_info = check_file(line)
                file, depth = line_info[0], line_info[1]

                if not file:
                    directory_path[depth] = line.replace("|||", "").lstrip() + "\\"

                elif file:
                    formatted_line = line_formatter(line, directory_path, depth)
                    name, extension, path, keywords = formatted_line[0], formatted_line[1], \
                                                      formatted_line[2], formatted_line[3]
                    writer(name, extension, path, keywords, output)


def check_file(line):
    regex_ext = re.compile(r'\.\w{1,9}$')
    regex_depth = re.compile(r'(\|\|\|)')
    regex_line = re.compile(r'\s{4,}')

    file_match = regex_ext.search(line)
    depth_match = len(regex_depth.findall(line))

    anal = line.split("|||")[1:-1]
    anal2 = [True if not regex_line.fullmatch(x) else False for x in anal]

    if not all(anal2):
        depth_match += 1

    if file_match:
        return True, depth_match
    return False, depth_match


def line_formatter(line, directory_path, depth):
    line = line.replace("|||", "").lstrip()
    extension = line.split(".")[-1]
    directory = ""

    for num in range(depth):
        directory += directory_path[num]

    keywords = keyword_finder(line)
    return line, extension, directory, keywords


def keyword_finder(line):
    keyword_list = ["Finance", "Marketing", "Tax", "Resume", "Social Insurance Number", "Cheque",
                    "Record of Employment", "Direct Deposit", "Bank Account", "Bank Statement", "Passport", "Bank",
                    "Credit Card", "Visa", "Mastercard", "American Express", "AMEX", "Electronic Funds Transfer",
                    "Payroll", "Sales"]
    keywords_found = ""

    for keyword in keyword_list:
        regex = re.escape(keyword)

        if re.search(regex, line, re.IGNORECASE):
            keywords_found = f"{keywords_found} | {regex}"

    return keywords_found


def writer(name, extension, path, keywords, output_file):
    name = name.replace(",", " ")
    path = path.replace(",", " ")
    if not keywords:
        keywords = "No keywords found"
    output_file.write(f"{keywords}, {name}, {path}, {extension}\n")
    return


if __name__ == "__main__":
    main()
