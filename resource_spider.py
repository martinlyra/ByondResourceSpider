import os
import re as regex


line_comment_regex_expression = regex.compile(r'^\s*\/\/')


def construct_regex(extensions):
    return regex.compile(rf"'([a-zA-Z0-9\\\/\-\_\.\#\&]*)\.({str.join('|', extensions)})'")


def construct_filename_regex(extensions):
    return regex.compile(rf'\.({str.join("|", extensions)})$')


def collect_candidate_files(directory, extensions):
    if not isinstance(extensions, list):
        extensions = [extensions]
    expression = construct_filename_regex(extensions)

    def is_a_match(file):
        return regex.search(expression, file) is not None

    candidates = dict()
    for path, subdirectories, files in os.walk(directory):
        for file in files:
            if is_a_match(file):
                full_path = os.path.join(path, file)
                full_path = os.path.normpath(full_path)
                candidates[len(candidates) + 1] = full_path.lower()
    return candidates


def apply_regex_to_file(file, expression, ignore_comments=True):
    def is_a_line_comment(line):
        return line_comment_regex_expression.match(line)

    results = list()

    is_comment_block = False
    for line in open(file, 'r', encoding='latin-1'):
        if ignore_comments:
            if str.find(line, '/*') >= 0:
                is_comment_block = True
            if str.find(line, '*/') >= 0:
                is_comment_block = False
            if is_comment_block or is_a_line_comment(line):
                continue

        matches = regex.findall(expression, line)
        if len(matches) > 0:
            for match in matches:
                results.append(os.path.normpath(str.join('.', match)).lower())
    return results


def analyze(targets):
    expr = construct_regex(targets)

    source_code_files = collect_candidate_files('./', 'dm')
    resource_files = collect_candidate_files('./', targets)

    count = 0
    resources_used = {
        icon: 0
        for icon in resource_files.values()
    }
    resources_non_existing = dict()
    for code_file in source_code_files.values():
        matches = apply_regex_to_file(code_file, expr)
        for match in matches:
            if match not in resources_used:
                if match not in resources_non_existing:
                    resources_non_existing[match] = 0
                resources_non_existing[match] += 1
            else:
                resources_used[match] += 1
            count += 1

    non_used_icons = list(filter(
        lambda x: x[1] == 0,
        resources_used.items()
    ))

    print("Processed!")
    print(f"\t{len(resource_files)} found resource files")
    print(f"\t{count} matched usages in {len(source_code_files)} code files")
    print("")

    if len(resources_non_existing):
        print(f"Missing resource files ({len(resources_non_existing)} entries):")
        for (key, value) in resources_non_existing.items():
            print(f"\t{key}: {value} references")
        print('End of missing resources list\n')
    else:
        print("No missing resources found!")

    if len(non_used_icons):
        print(f"Unused resource files ({len(non_used_icons)} entries):")
        for (key, value) in non_used_icons:
            print(f"\t{key}")
        print('End of unused resources list\n')
    else:
        print("No unused resources found!")

    print("Done!")


if __name__ == "__main__":
    analyze(['dmi', 'ogg'])
