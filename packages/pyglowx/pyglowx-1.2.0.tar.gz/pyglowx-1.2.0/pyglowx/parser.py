import re
from .ansi_codes_mapping import (
   ANSI_RESET,
   contains_foreground_color,
   contains_background_color,
   contains_style,
   get_foreground_color,
   get_background_color,
   get_style
)

class PyGlowxParser:
 @staticmethod
 def parse_recursively(input_str: str, start=0):
    output = []
    i = start

    rgb_pattern = re.compile(r"^rgb\((\d{1,3}),(\d{1,3}),(\d{1,3})\)$")
    hex_pattern = re.compile(r"^hex\(#([A-Fa-f0-9]{6})\)$")

    while i < len(input_str):
        if input_str.startswith("[/", i):
            end = input_str.find("]", i)
            if end == -1:
                break
            return "".join(output), end + 1

        if input_str[i] == '[':
            end = input_str.find("]", i)
            if end == -1:
                break

            tag_string = input_str[i + 1:end].strip()
            tags = tag_string.split()

            ansi = []

            for tag in tags:
                tag_lower = tag.lower()
                rgb_match = rgb_pattern.match(tag_lower)
                hex_match = hex_pattern.match(tag_lower)

                if rgb_match:
                    r, g, b = map(int, rgb_match.groups())
                    ansi.append(f"\u001b[38;2;{r};{g};{b}m")
                elif hex_match:
                    hex_code = hex_match.group(1)
                    r = int(hex_code[0:2], 16)
                    g = int(hex_code[2:4], 16)
                    b = int(hex_code[4:6], 16)
                    ansi.append(f"\u001b[38;2;{r};{g};{b}m")
                elif contains_foreground_color(tag):
                    ansi.append(get_foreground_color(tag))
                elif contains_background_color(tag):
                    ansi.append(get_background_color(tag))
                elif contains_style(tag):
                    ansi.append(get_style(tag))

            inner_result, next_index = PyGlowxParser.parse_recursively(input_str, end + 1)
            output.append("".join(ansi))
            output.append(inner_result)
            output.append(ANSI_RESET)
            i = next_index
        else:
            output.append(input_str[i])
            i += 1

    return "".join(output), i
