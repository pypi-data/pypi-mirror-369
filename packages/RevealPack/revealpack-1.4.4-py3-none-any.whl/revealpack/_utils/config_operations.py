import json
import logging
import sys
import os


def read_config(target_dir):
    """Read the config.json file from the target directory and return the configuration."""
    config_path = os.path.join(target_dir, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logging.error(f"config.json not found in {target_dir}.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Error decoding config.json.")
        sys.exit(1)


def initialize_logging(config, log_level=None):
    """Initialize logging based on the config.json settings."""
    if log_level:
        log_level = log_level.upper()
    else:
        log_level = config.get("logging", "info").upper()
    
    # Get the numeric log level, defaulting to INFO if invalid
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger to ensure the level is set
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # If no handlers exist, create a basic one
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        # Update existing handlers to respect the new level
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level)


def write_config(target_dir, property_name, property_value, force=False):
    """Modify a property in the config.json file and save the changes."""
    config_path = os.path.join(target_dir, "config.json")

    try:
        # Read the existing configuration
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Split the property_name into parts to handle nested properties
        keys = property_name.split(".")
        last_key = keys.pop()

        # Navigate to the correct part of the configuration
        sub_config = config
        for key in keys:
            if key in sub_config:
                sub_config = sub_config[key]
            else:
                if force:
                    sub_config[key] = {}
                    sub_config = sub_config[key]
                else:
                    logging.error(f"Property {property_name} not found in config.json.")
                    sys.exit(1)

        if last_key in sub_config:
            existing_value = sub_config[last_key]
            if isinstance(existing_value, type(property_value)) or force:
                sub_config[last_key] = property_value
            else:
                logging.error(f"Type mismatch: {last_key} expects {type(existing_value).__name__}, got {type(property_value).__name__}")
                sys.exit(1)
        else:
            if force:
                sub_config[last_key] = property_value
            else:
                logging.error(f"Property {property_name} not found in config.json.")
                sys.exit(1)

        # Write the updated configuration back to the file
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        logging.info(f"Property {property_name} updated successfully.")

    except FileNotFoundError:
        logging.error(f"config.json not found in {target_dir}.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Error decoding config.json.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred while updating config.json: {e}")
        sys.exit(1)
