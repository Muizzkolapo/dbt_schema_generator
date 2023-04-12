import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Set, List, Tuple


def get_dbt_project_status() -> Tuple[str, str]:
    """
    This function uses the dbt debug command and returns the status of the dbt project and its location.
    
    :return: A tuple with the first element being either 'passed' the current directory has dbt_project.yml, 
            'failed' or 'unknown', and the second element being the path to the dbt project.
    """
    try:
        result = subprocess.run(['dbt', 'debug'], capture_output=True, text=True)
        output = result.stdout
        if 'ERROR not found' in output:
            print("fatal: \n  Not a dbt project (or any of the parent directories). Missing dbt_project.yml file. \n   Please go to the right directory and retry.")
            return ('failed 💩', None)
        elif 'All checks passed' in output:
            lines = output.split("\n")
            for line in lines:
                if "Using dbt_project.yml file at" in line:
                    path = line.split("dbt_project.yml file at")[1].strip()
                    path = os.path.dirname(path)
                    if os.path.exists(path):
                        return ('passed', path)
            return ('passed', None)
        else:
            return ('unknown', None)
    except Exception as e:
        print(f"An error occurred: {e}")
        return ('unknown', None)

def find_manifest_file(path: str) -> str:
    """Finds the manifest.json file in the given path."""
    for root, _, files in os.walk(path):
        for file in files:
            if file == "manifest.json":
                return os.path.join(root, file)
    return None

def load_manifest(file_path: str) -> Dict:
    """Loads the manifest JSON file."""
    with open(file_path, 'r') as f:
        manifest_data = json.load(f)
    return manifest_data

def get_models(manifest_data: Dict, model_names: Set[str]) -> Dict:
    """Extracts the specified models from the manifest data."""
    models = {}
    for node_key, node_value in manifest_data['nodes'].items():
        if node_value['resource_type'] == 'model' and node_value['name'] in model_names:
            models[node_key] = node_value
    return models

def get_path_models(manifest_data: Dict, path_name: str) -> Dict:
    """Extracts the specified models from the manifest data."""
    models = {}
    for node_key, node_value in manifest_data['nodes'].items():
        original_file_path = os.path.relpath(node_value['original_file_path'])
        if original_file_path.startswith(path_name) and node_value['resource_type'] == 'model':
            models[node_key] = node_value
    return models


def create_schema(models: Dict) -> str:
    """Creates the schema YAML content from the models."""
    schema = "version: 2\nmodels:\n"
    for model in models.values():
        model_dict = {
            'name': model['name'],
            'description': '',
            'columns': []
        }
        for column_name, column_value in model['columns'].items():
            column_dict = {
                'name': column_name,
                'description': '',
            }
            model_dict['columns'].append(column_dict)

        model_lines = f"  - name: {model_dict['name']}\n    description: '{model_dict['description']}'\n    columns:\n"
        column_lines = "\n".join([f"      - name: {col['name']}\n        description: '{col['description']}'\n" for col in model_dict['columns']])
        schema += f"{model_lines}{column_lines}\n"
    return schema

def save_schema(schema: str, output_file: str) -> None:
    """Saves the schema YAML content to the output file."""
    with open(output_file, 'w') as f:
        f.write(schema)

def main() -> None:
    parser = argparse.ArgumentParser(description='Generate schema.yml file for specified dbt models.')
    parser.add_argument('-m', '--models', type=str, required=False,
                        help='Comma-separated list of model names to include in the schema.yml file.')
    parser.add_argument('-p', '--path', type=str, required=False,
                        help='Path to include models in the schema.yml file.')

    args = parser.parse_args()
    specified_models = set(args.models.split(',')) if args.models else None
    specified_path = args.path

    if specified_path and not specified_path.endswith(os.path.sep):
        specified_path += os.path.sep

    status, project_path = get_dbt_project_status()
    if status == 'passed' and project_path:
        manifest_file = find_manifest_file(project_path)
        if manifest_file:
            manifest_data = load_manifest(manifest_file)

            if specified_models:
                models = get_models(manifest_data, specified_models)
            elif specified_path:
                models = get_path_models(manifest_data, specified_path)
            else:
                print("Please specify either the --models or --path flag.")
                return

            if specified_models:
                for model_name in specified_models:
                    model = {key: value for key, value in models.items() if value['name'] == model_name}
                    schema = create_schema(model)
                    model_directory = os.path.dirname(model[next(iter(model))]['original_file_path'])
                    output_file = os.path.join(project_path, model_directory, f"{model_name}.yml")
                    save_schema(schema, output_file)
            else:
                for model in models.values():
                    single_model = {key: value for key, value in models.items() if value['name'] == model['name']}
                    schema = create_schema(single_model)
                    model_directory = os.path.dirname(model['original_file_path'])
                    output_file = os.path.join(project_path, model_directory, f"{model['name']}.yml")
                    save_schema(schema, output_file)
        else:
            print("manifest.json file not found.")
    else:
        print(f"dbt project status: {status}")

if __name__ == "__main__":
    main()