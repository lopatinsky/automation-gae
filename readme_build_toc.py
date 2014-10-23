import re
import os.path


def is_header(line):
    return line[0] == "#" and line[1] != "!"


def make_link(level, text):
    header_id = "markdown-header-" + re.sub(r"\s+", "-", text.lower())
    prefix = "> " + "   * " * (level - 1)
    return "%s[%s](#%s)\n" % (prefix, text, header_id)


def main():
    readme_dir = os.path.dirname(__file__)
    readme_file = os.path.join(readme_dir, "README.md")
    readme = open(readme_file, "r+")
    lines = readme.readlines()

    i = 0
    for i, line in enumerate(lines):
        if is_header(line):
            break
    lines = lines[i:]

    headers = []
    for line in lines:
        if not is_header(line):
            continue
        header_level = 1
        while line[header_level] == "#":
            header_level += 1
        header_text = line[header_level:].strip()
        headers.append((header_level, header_text))

    toc_lines = ["> Table of contents\n",
                 ">\n"]
    for level, text in headers:
        toc_lines.append(make_link(level, text))
    toc_lines.append("")

    print "".join(toc_lines)

    lines[:0] = toc_lines
    readme.seek(0)
    readme.truncate()
    readme.writelines(lines)
    readme.close()

if __name__ == "__main__":
    main()
