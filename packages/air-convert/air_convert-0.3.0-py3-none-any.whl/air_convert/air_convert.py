import os
import re
import shutil
import subprocess
import tempfile

from bs4 import BeautifulSoup, Comment, ProcessingInstruction


def html_to_airtags(html, air_prefix: bool = True) -> str:
    """Converts HTML to Air Tags."""
    result = _html_to_airtags(html, air_prefix).strip()
    if result.strip().startswith("'html'"):
        result = result.strip()[6:]
    return format_with_ruff(result)


def _html_to_airtags(html, air_prefix: bool = True) -> str:
    """Converts HTML to Air Tags.

    This function includes code modified and extended from FastHTML licensed under the Apache License 2.0:

    https://github.com/answerdotai/fasthtml

    Copyright [AnswerAI] [2024-2025]

    This function licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    """
    base_prefix = "air." if air_prefix else ""

    def parse(element, level=0, in_svg=False):
        if isinstance(element, str):
            return repr(element.strip()) if element.strip() else ""
        if isinstance(element, list):
            return "\n".join(parse(o, level, in_svg) for o in element)
        tag_name = element.name.capitalize().replace("-", "_")
        if tag_name == "[document]":
            return parse(list(element.children), level, in_svg)

        # Check if this is an SVG element or if we're inside an SVG
        is_svg = tag_name.lower() == "svg"
        current_in_svg = in_svg or is_svg
        prefix = f"{base_prefix}svg." if current_in_svg else base_prefix

        children = []
        for c in element.contents:
            if str(c).strip():
                if isinstance(c, str):
                    children.append(repr(c.strip()))
                else:
                    children.append(parse(c, level + 1, current_in_svg))
        attrs, exotic_attrs = [], {}
        for key, value in sorted(element.attrs.items(), key=lambda x: x[0] == "class"):
            if value is None or value is True:
                value = True  # handle boolean attributes
            elif isinstance(value, (tuple, list)):
                value = " ".join(value)
            key = migrate_html_key_to_air_tag(key)
            if re.match(r"^[A-Za-z_-][\w-]*$", key):
                attrs.append(f"{key.replace('-', '_')}={value!r}")
            else:
                exotic_attrs[key] = value
        if exotic_attrs:
            attrs.append(f"**{exotic_attrs!r}")
        spc = " "
        if not element.contents:
            onlychild = True
        elif len(element.contents) == 1 and isinstance(element.contents[0], str):
            onlychild = True
        else:
            onlychild = False
        j = ", " if onlychild else f",\n{spc}"
        inner = j.join(filter(None, children + attrs))
        if onlychild:
            return f"{prefix}{tag_name}({inner})"
        if not attrs:
            return f"{prefix}{tag_name}(\n{spc}{inner}\n{' ' * (level - 1) * 4})"
        inner_children = j.join(filter(None, children))
        inner_attrs = ", ".join(filter(None, attrs))
        return f"{prefix}{tag_name}(\n{spc}{inner_children}\n{' ' * (level - 1) * 4}, {inner_attrs})"

    # prep the html by removing comments and processing instructions (like the <?xml ...?> tag)
    soup = BeautifulSoup(html.strip(), features="xml")
    for bad_tag in soup.find_all(string=lambda text: isinstance(text, (Comment, ProcessingInstruction))):
        bad_tag.extract()

    # Convert the text
    parsed = parse(soup, 1, False)

    # Attempt to use ruff to reformat the string
    return parsed.strip()


def format_with_ruff(code: str) -> str:
    if not shutil.which("ruff"):
        return code
    formatted_code = code
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmp:
        tmp.write(code)
        tmp.flush()
        tmp_path = tmp.name

        try:
            # Run ruff to format the file
            try:
                subprocess.run(
                    ["ruff", "format", tmp_path],
                    check=True,
                    capture_output=True,
                    text=True,
                )

                # Read the formatted content
                with open(tmp_path) as f:
                    formatted_code = f.read()
            except subprocess.CalledProcessError as cpe:
                print("\nType of error:", type(cpe))
                print(cpe.args)

        finally:
            os.unlink(tmp_path)

    return formatted_code


def migrate_html_key_to_air_tag(key: str) -> str:
    """Clean up HTML attribute keys to match the standard W3C HTML spec.

    Args:
        key: An uncleaned HTML attribute key

    Returns:

        Cleaned HTML attribute key
    """
    # If a "_"-suffixed proxy for "class", "for", or "id" is used,
    # convert it to its normal HTML equivalent.
    key = {"class": "class_", "for": "for_", "as": "as_"}.get(key, key)
    # Remove leading underscores and replace underscores with dashes
    return key.lstrip("_").replace("_", "-")
