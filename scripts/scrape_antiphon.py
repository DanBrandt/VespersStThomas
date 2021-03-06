#!/bin/python3

import requests
import re
import argparse
from more_itertools import split_after


def download_gabc(chant_id):
    url = f"https://gregobase.selapa.net/download.php?id={chant_id}&format=gabc"
    response = requests.get(url)
    response.raise_for_status()
    if response.status_code != 200:
        raise Exception(f"HTTP request for GABC file returned unexpected status: {response.status_code}")
    return response.text.splitlines()

def split_header_and_content(gabc_lines):
    [header, content] = list(split_after(gabc_lines, lambda x: x == "%%"))
    return header, content


def make_header(old_header, chant_id, tone):
    return ( [f"% https://gregobase.selapa.net/chant.php?id={chant_id}"]
                + old_header[:-1]
                + [f"annotation:{tone};", "%%"] )

def escape_unicode_chars(content):
    return list([escape_unicode_chars_str(s) for s in content])

def escape_unicode_chars_str(s):
    if "oe" in s:
        print("Text contains sequence OE, can't tell if it should be joined")
    return ( s.replace("ae", "\u00e6")
                .replace("Ae", "\u00c6")
                .replace("AE", "\u00c6")
                .replace("\u0153", "<sp>oe</sp>")
                .replace("\u01fd", "<sp>'ae</sp>'")
                .replace("aé", "<sp>'ae</sp>'")
                .replace("\u2020", "+") )

INTONATION_REGEX_STR = r"\([cf]b?\d\).{2,}\*"
INTONATION_REGEX = re.compile(INTONATION_REGEX_STR)

def make_intonation_gabc(content):
    match = re.match(INTONATION_REGEX, content[0])
    if not match:
        raise Exception(f"Can't find intonation of antiphon: {content[0]}")
    return [match.group() + "*(::)", "%%TODO psalm verse"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("chant_id")
    parser.add_argument("tone")
    parser.add_argument("output_name")
    parser.add_argument("-s", "--semidouble", action="store_true")
    args = parser.parse_args()

    gabc_lines = download_gabc(args.chant_id)
    header, content = split_header_and_content(gabc_lines)
    new_header = make_header(header, args.chant_id, args.tone)
    new_content = escape_unicode_chars(content)

    if args.semidouble:
        output_name = f"{args.output_name}-antiphon.gabc"
    else:
        output_name = f"{args.output_name}.gabc"

    with open(output_name, "w") as antiphon_out:
        antiphon_out.write("\n".join(new_header))
        antiphon_out.write("\n")
        antiphon_out.write("\n".join(new_content))

    if not args.semidouble:
        return

    intonation_content = make_intonation_gabc(new_content)
    with open(f"{args.output_name}-intonation.gabc", "w") as intonation_out:
        intonation_out.write("\n".join(new_header))
        intonation_out.write("\n")
        intonation_out.write("\n".join(intonation_content))

if __name__ == "__main__":
    main()
