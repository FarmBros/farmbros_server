#!/usr/bin/env python3
"""
Convert cropV2.js to cropV2.json
This script uses Node.js to properly parse the JavaScript and convert to JSON
"""
import json
import subprocess
import sys

def convert_js_to_json():
    """Convert the JavaScript crops file to JSON using Node.js"""

    # Create a temporary Node.js script to parse the JS and output JSON
    node_script = """
    const fs = require('fs');

    // Read the JS file
    const jsContent = fs.readFileSync('assets/cropV2.js', 'utf8');

    // Remove the const declaration and export statement
    let dataStr = jsContent
        .replace(/^const crops = /, '')
        .replace(/;?\\s*export default crops;?\\s*$/, '')
        .trim();

    // Use eval to parse the JavaScript array (safe because we control the source)
    const crops = eval('(' + dataStr + ')');

    // Convert to JSON and output
    console.log(JSON.stringify(crops, null, 2));
    """

    try:
        # Write the Node.js script to a temporary file
        with open('/tmp/convert_crops.js', 'w') as f:
            f.write(node_script)

        # Run the Node.js script
        result = subprocess.run(
            ['node', '/tmp/convert_crops.js'],
            capture_output=True,
            text=True,
            check=True,
            cwd='/mnt/Kali/projects/farmbros_server'
        )

        # Parse the JSON output
        crops_data = json.loads(result.stdout)

        # Write to JSON file
        output_path = 'assets/cropV2.json'
        with open(output_path, 'w') as f:
            json.dump(crops_data, f, indent=2)

        print(f"✓ Successfully converted {len(crops_data)} crops to {output_path}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Error running Node.js: {e.stderr}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = convert_js_to_json()
    sys.exit(0 if success else 1)
