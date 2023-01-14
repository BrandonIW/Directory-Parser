import os
import re


def main():
    """ First open the file we will write results to. Then open the TA file of filenames we are searching for. For
    each filename, first replace the unnecessary \n, then read the raw PS Tree output into memory. Search for the exist-
    ance of the file. If it does exist, save the drive letter we found it in and return in a list. For each drive letter
    that contains the filename, create a generator of that PS Tree output, reading from the bottom up. For each line
    in the generator, check if the filename is present. If present, get directory and write."""
    count = 0

    with open(f'..\output\Outputfile.txt', 'w', encoding="UTF-8", errors="Ignore") as output:
        output.write('Detection Result, Filename, Directory Location\n')
        with open(f'..\\files\\TA Files.txt', 'r', encoding="UTF-8", errors="Ignore") as TA_Filenames:
            f_file, g_file, j_file, e_file = read_pstree()

            for filename in TA_Filenames:
                filename = filename.replace("\n", "")
                roots_present = check_if_exists(filename, f_file, g_file, j_file, e_file)

                if not roots_present:
                    writer(filename, None, None, output)
                    count += 1
                    if count % 200 == 0:
                        print(count)
                    continue

                for vol in roots_present:
                    generator_object = reverse_readline(f"..\\files\\{vol}_Tree.txt")
                    for line in generator_object:
                        complete_name = line.split("¦")[-1].lstrip()
                        if filename == complete_name:
                            directory = get_dir(generator_object)
                            writer(filename, vol, directory, output)
                            break

                count += 1
                if count % 200 == 0:
                    print(f"Count is {count}/~50,000\n"
                          f"Most recent sample: {filename} ||| {vol}\\{directory}")


def check_if_exists(filename, f_file, g_file, j_file, e_file):
    vols = []

    if filename in j_file:
        vols.append("J")
    if filename in g_file:
        vols.append("G")
    if filename in f_file:
        vols.append("F")
    if filename in e_file:
        vols.append("E")

    return vols


def read_pstree():
    """ Open each of the 4 root PS Tree outputs and determine where, if anywhere, the file exists. Helps narrow down
    search and avoid unnecessary processing """

    with open("..\\files\\J_Tree.txt", 'r', encoding="ANSI", errors="Ignore") as file:
        j_file = file.read()

    with open("..\\files\\G_Tree.txt", 'r', encoding="ANSI", errors="Ignore") as file:
        g_file = file.read()

    with open("..\\files\\F_Tree.txt", 'r', encoding="ANSI", errors="Ignore") as file:
        f_file = file.read()

    with open("..\\files\\E_Tree.txt", 'r', encoding="ANSI", errors="Ignore") as file:
        e_file = file.read()

    return f_file, g_file, j_file, e_file


def calc_depth(line):
    """
    Gets the depth of a directory by taking in that directory's line in the txt file i.e. ¦       +---log and
    just finding the location of the + symbol. PS Tree standardizes the location in multiples of 4
    """
    return line.index("+") / 4


def get_dir(gen_obj):
    """
    Generates the directory path of a particular file. Reads the file backwards and looks at the depth relative to the
    file via the get_depth function
    """

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
        10: "",
        11: "",
        12: "",
        13: "",
        14: "",
        15: "",
        16: "",
        17: "",
        18: "",
        19: "",
        20: ""
    }
    full_dir = ""
    regex_parent_depth = re.compile(r'\+---')
    depth_parent = None

    # Iterate the generator object (reads backwards to facilitate searching). For each line, if it's a directory
    # (matches the +--- string indicative of a dir) then strip out the unnecessary characters and get the directory name
    # Calculate depth. If depth parent doesn't exist yet i.e. this is the first directory directly above the file, then
    # set the depth_parent value and populate dictionary. If this isn't the first directory above the file, BUT its
    # depth is one less than the directory prior, then we know we're one level deeper. Once we hit the root, break out
    for line in gen_obj:
        if regex_parent_depth.search(line):
            dir = line.split("+---")[-1]  # Match +¦\s up until the first -. Then lstrip -
            depth = calc_depth(line)
            if not depth_parent:
                depth_parent = calc_depth(line)
                directory_path[depth] = dir
            elif depth == (depth_parent - 1):
                directory_path[depth] = dir
                depth_parent = depth

            if depth_parent == 0:
                break

    for name in directory_path.values():
        if not name:
            break
        full_dir = full_dir + f"{name}\\"

    return full_dir


def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename, encoding="ANSI", errors="Ignore") as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment


def writer(filename, volume, directory, output_file):
    """ Write to CSV file """

    if filename and directory:
        output_file.write(f"TA Filename detected| {volume}\\{directory}\\{filename}\n")
    else:
        output_file.write(f"No detection| {filename}\n")
    return


if __name__ == "__main__":
    main()
