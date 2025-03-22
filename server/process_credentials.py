import json
import sys

def process_firebase_credentials(json_file_path):
    """
    Reads a Firebase credentials JSON file, escapes newline characters,
    and prints the JSON string for use in a .env file.
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        json_string = json.dumps(data)
        escaped_json_string = json_string.replace('\\n', '\\\\n')

        print(f"FIREBASE_CREDENTIALS={escaped_json_string}")

    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_credentials.py YOUR_FIREBASE_CREDENTIALS_FILE.json")
    else:
        json_file_path = sys.argv[1]
        process_firebase_credentials(json_file_path)