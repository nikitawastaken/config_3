import argparse
import xml.etree.ElementTree as ET
import re
import sys


# Регулярное выражение для проверки имени
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_name(name):
    if not NAME_PATTERN.match(name):
        raise ValueError(f"Invalid name: '{name}'")


def parse_value(element):
    if len(element) > 0:  # Проверяем, есть ли вложенные элементы
        # Если вложенный элемент — это <dictionary>, обрабатываем его
        child = element[0]
        if child.tag == "dictionary":
            return parse_dictionary(child)
        else:
            raise ValueError(f"Unsupported nested element in entry: {ET.tostring(element, 'unicode')}")
    elif element.text and element.text.strip().isdigit():  # Проверяем, что текст — это число
        return int(element.text.strip())
    elif element.text and element.text.strip():  # Текстовое значение
        return element.text.strip()
    else:
        raise ValueError(f"Invalid value for element '{element.tag}'")


def parse_dictionary(element):
    dictionary = {}
    for entry in element:
        if entry.tag != "entry" or "name" not in entry.attrib:
            raise ValueError(f"Invalid dictionary entry: {ET.tostring(entry, 'unicode')}")
        name = entry.attrib["name"]
        validate_name(name)
        dictionary[name] = parse_value(entry)
    return dictionary


def parse_configuration(xml_root):
    """Парсинг корневого элемента <configuration>."""
    if xml_root.tag != "configuration":
        raise ValueError("Root element must be <configuration>")
    
    dictionary_element = xml_root.find("dictionary")
    if dictionary_element is None:
        raise ValueError("Missing required <dictionary> element in <configuration>")
    
    return parse_dictionary(dictionary_element)


def format_value(value):
    if isinstance(value, dict):
        formatted = "{\n"
        for k, v in value.items():
            formatted += f"    {k} = {format_value(v)};\n"
        formatted += "}"
        return formatted
    return str(value)


def write_output(data, output_path):
    with open(output_path, "w") as f:
        for key, value in data.items():
            f.write(f"{key} = {format_value(value)};\n")


def main():
    parser = argparse.ArgumentParser(description="XML to custom configuration language translator.")
    parser.add_argument("input", help="Path to the input XML file.")
    parser.add_argument("--output", required=True, help="Path to the output configuration file.")
    args = parser.parse_args()

    try:
        # Чтение и парсинг XML
        tree = ET.parse(args.input)
        root = tree.getroot()

        # Преобразование XML в объектную модель
        data = parse_configuration(root)

        # Запись результата
        write_output(data, args.output)
        print(f"Translation completed successfully. Output saved to {args.output}.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()