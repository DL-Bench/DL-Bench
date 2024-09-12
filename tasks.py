import os
import re
import json
from collections import defaultdict
def list_files(directory):
    # List all files and directories in the specified directory
    files = os.listdir(directory)
    # Filter out directories, keep only files
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    return files
def list_files(directory):
    # List all files and directories in the specified directory
    files = os.listdir(directory)
    # Filter out directories, keep only files
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    return files

# Define the keywords associated with each DL component
dl_components = {
    'Preprocessing': ['normalize', 'scale', 'augment', 'preprocess', 'resize', 'encode', 'transform'],
    'Model Generation': ['model', 'architecture', 'train', 'compile', 'build', 'setup', 'initialize'],
    'Training': ['train', 'fit', 'epoch', 'batch', 'optimize', 'backpropagation'],
    'Evaluation': [ 'evaluate', 'validate', 'metrics', 'performance', 'loss', 'accuracy'],
    'Post-processing': ['threshold', 'postprocess', 'output', 'predict', 'classify', 'detection', 'segmentation'],
    'Utilities': ['load', 'save', 'read', 'write', 'utility', 'helper', 'tools']
}

# Directory where your test files are located
dl_test_statistics = defaultdict(int)

# Process each entry in the data list

files = list_files("crawl_tests")
for file in files:
    if "function_call" in file:
        with open(f"crawl_tests/{file}", 'r') as file:
            for line in file:
                data = json.loads(line)
                function_name = list(data.keys())[0].lower()  # Get the function name and convert to lower case

                # Check for each component's keywords in the function name
                for component, keywords in dl_components.items():
                    if any(keyword in function_name for keyword in keywords):
                        dl_test_statistics[component] += 1
                        break  # Avoid counting a function under multiple components

# Print statistics
for component, count in dl_test_statistics.items():
    print(f"{component}: {count} times tested")
