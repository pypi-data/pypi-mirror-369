#!/usr/bin/env python3
"""
JSON to YAML Converter
Reads JSON API response files from sample_data
folder and converts them to YAML format
Enhanced to merge all fields from all records
"""
import logging
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union
from collections import defaultdict

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_title_from_key(key: str) -> str:
    """Generate human-readable title from JSON key"""
    # Handle snake_case and camelCase
    if "_" in key:
        # snake_case
        words = key.split("_")
    else:
        # camelCase or PascalCase
        import re

        words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", key)

    # Capitalize first letter of each word
    title = " ".join(word.capitalize() for word in words)

    # Handle common abbreviations
    abbreviations = {
        "Id": "ID",
        "Url": "URL",
        "Api": "API",
        "Http": "HTTP",
        "Json": "JSON",
        "Xml": "XML",
        "Uuid": "UUID",
        "Utc": "UTC",
        "Gmt": "GMT",
    }

    for abbr, replacement in abbreviations.items():
        title = title.replace(abbr, replacement)

    return title


def is_epoch_millis_timestamp(data):
    """Check if data is an epoch milliseconds timestamp (string or int)"""
    try:
        if isinstance(data, str):
            # Check if string contains only digits
            if not data.isdigit():
                return False
            timestamp = int(data)
        elif isinstance(data, int):
            timestamp = data
        else:
            return False

        # Epoch millis should be 13 digits (roughly between 1970-2050)
        # Valid range: 1000000000000 (2001) to 2147483647000 (2038)
        if (
                len(str(timestamp)) == 13
                and 1000000000000 <= timestamp <= 2147483647000
        ):
            # Try to convert to datetime to validate
            datetime.fromtimestamp(timestamp / 1000)
            return True
        return False
    except (ValueError, OSError, OverflowError):
        return False


def is_datetime_string(value: str) -> bool:
    """Check if a string appears to be a date-time value"""
    if not isinstance(value, str):
        return False

    # Common date-time patterns
    datetime_patterns = [
        # ISO 8601 formats
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?",
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}",
        r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}"
    ]
    return any(re.match(pattern, value) for pattern in datetime_patterns)


def is_ip_address(value: str) -> bool:
    """Check if a string is an IP address (IPv4 or IPv6)"""
    if not isinstance(value, str) or not value:
        return False

    # IPv4 pattern - more precise
    ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

    # Check IPv4 first
    if re.match(ipv4_pattern, value):
        return True
    return False


def is_mac_address(value: str) -> bool:
    """Check if a string is a MAC address"""
    if not isinstance(value, str):
        return False

    # MAC address patterns (with : or -)
    mac_patterns = [
        r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",  # AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF
        r"^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$"  # AAAA.BBBB.CCCC
    ]

    return any(re.match(pattern, value) for pattern in mac_patterns)


def is_uuid(value: str) -> bool:
    """Check if a string is a UUID"""
    if not isinstance(value, str):
        return False

    # UUID pattern (8-4-4-4-12)
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"

    return re.match(uuid_pattern, value) is not None


def is_domain_name(value: str) -> bool:
    """Check if a string is a domain name"""
    if not isinstance(value, str):
        return False

    # Domain name pattern
    domain_pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"

    # Should contain at least one dot and be between 1-253 characters
    return (
            re.match(domain_pattern, value) and
            '.' in value and
            len(value) <= 253 and
            len(value) >= 4  # Minimum: a.co
    )


def is_url(value: str) -> bool:
    """Check if a string is a URL (more specific than URI)"""
    if not isinstance(value, str):
        return False

    # URL patterns - web URLs specifically
    url_patterns = [
        r"^https?://[^\s/$.?#].[^\s]*$",  # HTTP/HTTPS
        r"^ftp://[^\s/$.?#].[^\s]*$",  # FTP
    ]

    return any(re.match(pattern, value, re.IGNORECASE) for pattern in url_patterns)


def is_uri(value: str) -> bool:
    """Check if a string is a URI (broader than URL)"""
    if not isinstance(value, str):
        return False

    # URI pattern - starts with scheme followed by ://
    uri_patterns = [
        r"^[a-zA-Z][a-zA-Z0-9+.-]*://[^\s]*$",  # Generic scheme
        r"^mailto:[^\s@]+@[^\s@]+\.[^\s@]+$",  # Email
        r"^file://[^\s]*$",  # File
        r"^urn:[a-zA-Z0-9][a-zA-Z0-9-]{0,31}:[^\s]+$"  # URN
    ]

    return any(re.match(pattern, value, re.IGNORECASE) for pattern in uri_patterns)


def is_password(value: str) -> bool:
    """Check if a string appears to be a password (heuristic based)"""
    if not isinstance(value, str):
        return False

    # Password heuristics - common field names that likely contain passwords
    # This is heuristic since we can't definitively identify password content
    return (
            len(value) >= 8 and  # Minimum password length
            any(c.isupper() for c in value) and  # Has uppercase
            any(c.islower() for c in value) and  # Has lowercase
            any(c.isdigit() for c in value) and  # Has digits
            any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in value)  # Has special chars
    ) or (
        # Or looks like a hash (hex string of certain length)
            len(value) in [32, 40, 64, 128] and all(c in '0123456789abcdefABCDEF' for c in value)
    )


def get_type_from_value(value: Any) -> str:
    """Map Python types to schema types"""
    if isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        return "string"
    # elif value is None:
    #     return "string"
    else:
        return "string"


def merge_all_records(data: List[Dict]) -> Dict[str, Any]:
    """Merge all records to include all possible fields"""
    if not data:
        return {}

    # If data is not a list, make it one
    if not isinstance(data, list):
        return data

    merged = {}

    def deep_merge(target: Dict, source: Dict) -> Dict:
        """Deep merge two dictionaries"""
        for key, value in source.items():
            if key in target:
                if isinstance(target[key], dict) and isinstance(value, dict):
                    target[key] = deep_merge(target[key], value)
                elif isinstance(target[key], list) and isinstance(value, list):
                    # For arrays, merge unique items
                    existing_items = target[key]
                    for item in value:
                        if item not in existing_items:
                            existing_items.append(item)
                # If types differ, keep the first encountered type
            else:
                target[key] = value
        return target

    # Merge all records
    for record in data:
        if isinstance(record, dict):
            merged = deep_merge(merged, record)

    return merged


def collect_all_field_types(data: List[Dict]) -> Dict[str, Dict[str, Any]]:
    """Collect all possible field types from all records"""
    field_info = defaultdict(lambda: {
        'types': set(),
        'sample_values': [],
        'is_array': False,
        'nested_fields': defaultdict(dict)
    })

    def analyze_value(key_path: str, value: Any, parent_info: Dict):
        """Recursively analyze values and collect type information"""
        if isinstance(value, dict):
            parent_info[key_path]['types'].add('object')
            for sub_key, sub_value in value.items():
                sub_path = f"{key_path}.{sub_key}" if key_path else sub_key
                analyze_value(sub_path, sub_value, parent_info)
        elif isinstance(value, list):
            parent_info[key_path]['types'].add('array')
            parent_info[key_path]['is_array'] = True
            if value:  # If array is not empty
                for item in value:
                    analyze_value(f"{key_path}[item]", item, parent_info)
        else:
            value_type = get_type_from_value(value)
            parent_info[key_path]['types'].add(value_type)
            if len(parent_info[key_path]['sample_values']) < 3:
                parent_info[key_path]['sample_values'].append(value)

    # If data is not a list, make it one
    if not isinstance(data, list):
        data = [data] if data else []

    # Analyze all records
    for record in data:
        if isinstance(record, dict):
            for key, value in record.items():
                analyze_value(key, value, field_info)

    return field_info


def read_json_file(file_path: Path) -> List[Dict[Any, Any]]:
    """Read and parse JSON file - return all records"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            logger.info(f"✅ Successfully read JSON file: {file_path.name}")
            # Return all records instead of limiting to 10
            return data if isinstance(data, list) else [data] if data else []
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing JSON in {file_path.name}: {e}")
        return []
    except FileNotFoundError:
        logger.error(f"❌ File not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"❌ Error reading {file_path.name}: {e}")
        return []


class JSONToYAMLConverter:
    """AI Agent for converting JSON API responses to YAML format"""

    def __init__(self, sample_data_folder: str = "build/output"):
        self.sample_data_folder = Path(sample_data_folder)
        self.output_folder = self.sample_data_folder / "yaml_output"
        if not self.output_folder.exists():
            self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.sample_data_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)

    def convert_to_yaml(self, data: List[Dict[Any, Any]], output_path: Path) -> bool:
        """Convert JSON data to YAML schema format and save"""
        try:
            # Generate schema from all JSON records
            schema = self.generate_schema_from_all_records(data)

            # Configure YAML output format
            yaml_content = yaml.dump(
                schema,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
                sort_keys=True,
            )

            with open(output_path, "w", encoding="utf-8") as file:
                file.write(yaml_content)

            logger.info(f"✅ Successfully converted to YAML schema: {output_path.name}")
            return True

        except Exception as e:
            logger.info(f"❌ Error converting to YAML: {e}")
            return False

    def process_single_file(self, json_file: str) -> bool:
        """Process a single JSON file"""
        json_path = self.sample_data_folder / json_file

        if not json_path.exists():
            logger.info(f"❌ JSON file not found: {json_path}")
            return False

        # Read JSON data - now returns all records
        json_data = read_json_file(json_path)
        if not json_data:
            return False

        # Create output YAML file path
        yaml_filename = json_path.stem + ".yaml"
        yaml_path = self.output_folder / yaml_filename

        # Convert and save
        return self.convert_to_yaml(json_data, yaml_path)

    def process_all_json_files(self) -> List[str]:
        """Process all JSON files in the sample_data folder"""
        json_files = list(self.sample_data_folder.glob("*.json"))

        if not json_files:
            logger.debug(f"❌ No JSON files found in {self.sample_data_folder}")
            return []

        logger.debug(f"🔍 Found {len(json_files)} JSON file(s) to process")

        processed_files = []

        for json_file in json_files:
            logger.info(f"\n📄 Processing: {json_file.name}")

            # Read JSON data - now returns all records
            json_data = read_json_file(json_file)
            if not json_data:
                continue

            logger.info(f"   📊 Processing {len(json_data)} record(s)")

            # Create output YAML file path
            yaml_filename = json_file.stem + ".yaml"
            yaml_path = self.output_folder / yaml_filename

            # Convert and save
            if self.convert_to_yaml(json_data, yaml_path):
                processed_files.append(yaml_filename)

        return processed_files

    def generate_schema_from_all_records(self, data: List[Dict[Any, Any]]) -> Dict[str, Any]:
        """Generate comprehensive schema from all JSON records"""
        if not data:
            return {"properties": {}}

        # Merge all records to get comprehensive field coverage
        merged_data = merge_all_records(data)

        # Generate schema from merged data
        return self.generate_schema_from_json(merged_data)

    def generate_schema_from_json(
            self, data: Any, parent_key: str = ""
    ) -> Dict[str, Any]:
        """Generate schema properties from JSON data"""
        if isinstance(data, dict):
            properties = {}

            for key, value in data.items():
                # Generate title from key
                title = generate_title_from_key(key)

                if isinstance(value, dict):
                    # Nested object
                    properties[key] = {
                        "type": "object",
                        "title": title,
                        "properties": self.generate_schema_from_json(value, key),
                    }
                elif isinstance(value, list):
                    # Array
                    if value:
                        # Determine array item type from first element
                        first_item = value[0]
                        if isinstance(first_item, dict):
                            # For object arrays, merge all items to get all possible fields
                            merged_item = {}
                            for item in value:
                                if isinstance(item, dict):
                                    merged_item = {**merged_item, **item}

                            properties[key] = {
                                "type": "array",
                                "title": title,
                                "items": {
                                    "type": "object",
                                    "properties": self.generate_schema_from_json(
                                        merged_item, key
                                    ),
                                },
                            }
                        else:
                            properties[key] = {
                                "type": "array",
                                "title": title,
                                "items": {"type": get_type_from_value(first_item)},
                            }
                    else:
                        properties[key] = {
                            "type": "array",
                            "title": title,
                            "items": {"type": "string"},
                        }
                else:
                    # Primitive type
                    property_def = {}

                    if get_type_from_value(value) == "boolean":
                        property_def["type"] = "boolean"
                        property_def["title"] = f"{title}?"
                    else:
                        property_def["type"] = get_type_from_value(value)
                        property_def["title"] = title

                    # Check for special formats (order matters - most specific first)
                    if isinstance(value, str):
                        if is_datetime_string(value):
                            property_def["format"] = "date-time"
                        elif is_epoch_millis_timestamp(value):
                            property_def["format"] = "epoch-millis"
                        elif is_uuid(value):
                            property_def["format"] = "uuid"
                        elif is_ip_address(value):
                            property_def["format"] = "ip-addr"
                        elif is_mac_address(value):
                            property_def["format"] = "mac-addr"
                        elif is_url(value):
                            property_def["format"] = "url"
                        elif is_uri(value):
                            property_def["format"] = "uri"
                        elif is_domain_name(value):
                            property_def["format"] = "domain-name"
                        elif is_password(value):
                            property_def["format"] = "password"
                    elif isinstance(value, int) and is_epoch_millis_timestamp(value):
                        property_def["format"] = "epoch-millis"

                    properties[key] = property_def

            return {"properties": properties} if parent_key == "" else properties
        else:
            # If root is not an object, wrap it
            root_property = {"type": get_type_from_value(data), "title": "Value"}

            # Check for special formats (order matters - most specific first)
            if isinstance(data, str):
                if is_datetime_string(data):
                    root_property["format"] = "date-time"
                elif is_epoch_millis_timestamp(data):
                    root_property["format"] = "epoch-millis"
                elif is_uuid(data):
                    root_property["format"] = "uuid"
                elif is_ip_address(data):
                    root_property["format"] = "ip-addr"
                elif is_mac_address(data):
                    root_property["format"] = "mac-addr"
                elif is_url(data):
                    root_property["format"] = "url"
                elif is_uri(data):
                    root_property["format"] = "uri"
                elif is_domain_name(data):
                    root_property["format"] = "domain-name"
                elif is_password(data):
                    root_property["format"] = "password"
            elif isinstance(data, int) and is_epoch_millis_timestamp(data):
                root_property["format"] = "epoch-millis"

            return {"properties": {"value": root_property}}


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description="JSON to YAML Converter")
    parser.add_argument(
        "--folder",
        default="build/output",
        help="Folder containing JSON files (default: build/output)",
    )

    args = parser.parse_args()

    # Initialize converter
    converter = JSONToYAMLConverter(args.folder)

    logger.info("JSON to YAML Converter (Enhanced)")
    logger.info("=" * 40)
    logger.info(
        "\n📁 Processing all JSON files in '%s' folder...", converter.sample_data_folder
    )
    processed_files = converter.process_all_json_files()

    if processed_files:
        logger.info("\n✅ Successfully converted %d file(s):", len(processed_files))
        for file in processed_files:
            logger.info("   - %s", file)
        logger.info(f"\n📂 Output files saved in: {converter.output_folder}")
        logger.info("📝 All fields from all records have been merged into the schema")
    else:
        logger.error("\n❌ No files were processed successfully")


if __name__ == "__main__":
    main()