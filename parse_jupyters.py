import requests
import nbformat
from io import BytesIO
import json
import os
from json_saver import save_dict_to_jsonl
import time
import requests
from io import BytesIO
import nbformat


def check_file_existence(file_path):
    return os.path.isfile(file_path)

def check_folder_existence(folder_path):
    return os.path.exists(folder_path)


def fetch_notebooks(owner, repo, token, path=""):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        contents = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve contents from {api_url}: {e}")
        return -1  # Return an empty list on failure

    notebooks = []

    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('.ipynb'):
            try:
                download_url = item['download_url']
                notebook_response = requests.get(download_url)
                notebook_response.raise_for_status()
                notebook_file = BytesIO(notebook_response.content)
                nb = nbformat.read(notebook_file, as_version=4)
                notebooks.append((item['path'], nb))
            except requests.exceptions.RequestException as e:
                print(f"Failed to download notebook {download_url}: {e}")
        elif item['type'] == 'dir':
            # Ensure the path used for recursive call is correctly formed
            new_path = f"{path}/{item['name']}".strip("/")
            sub_notebooks = fetch_notebooks(owner, repo, token, new_path)
            notebooks.extend(sub_notebooks)  # Ensure recursion results are added
    return notebooks


def parse_notebooks(notebooks):
    results = {}

    for path, nb in notebooks:
        entries = [] 
        current_markdown = None  
        code_cells = []  
        flag = False
        first_code = False
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                if current_markdown is not None:
                    if first_code:
                        flag = True
                    if flag:
                        current_markdown = "start"
                    entries.append({"prompt": current_markdown, "ground_truth": code_cells})
                
                current_markdown = cell.source
                code_cells = []  
            elif cell.cell_type == 'code':
                if not flag:
                    first_code = True
                code_cells.append(cell.source)

        if current_markdown is not None:
            entries.append({"prompt": current_markdown, "ground_truth": code_cells})
        else:
            if not flag:
                entries.append({"prompt": current_markdown, "ground_truth": code_cells})

        results[path] = entries  # Store all entries under the notebook path key
    return results


token = ''   # GitHub personal access token
file_path = "repos_jupyter.jsonl"

with open(file_path, 'r') as json_file:
    json_list = list(json_file)
base_path = "./jupyter"
for json_str in json_list:
    result = json.loads(json_str) 
    path = result["url"].replace("https://github.com/", "")
    print(path)
    if check_folder_existence(f"{base_path}/{path.replace('/','_')}"):
        continue
    try:
        notebooks = fetch_notebooks(path.split("/")[0], path.split("/")[1], token=token)
        time.sleep(1)
        if notebooks == -1:
            break
        parsed_notebooks = parse_notebooks(notebooks)
        
        if not os.path.exists(base_path +f"/{path.replace('/', '_')}"):
            os.mkdir(f"{base_path}/{path.replace('/','_')}")
        
        for notebook_path, content in parsed_notebooks.items():
            print(notebook_path)
            datas = content
            for data in datas:
                save_dict_to_jsonl(data, f"{base_path}/{path.replace('/','_')}/{notebook_path.replace('/','_')}.jsonl")
            print(f"Notebook: {notebook_path}")
        
    except Exception as e:
        print("error", path, e)
