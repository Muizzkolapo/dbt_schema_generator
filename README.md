# dbt Schema Generator

A command-line tool to generate schema.yml files for specified dbt models.

## Installation

Install the package using pip:

```
pip install dbt_schema_generator
```

# Usage

You can use the dbt_schema_generator command-line tool with the following options:

-m, --models: A comma-separated list of model names to include in the schema.yml file.
-p, --path: A path to include models in the schema.yml file.


Examples:

```
dbt_schema_generator -m model1,model2,model3
dbt_schema_generator --models model1,model2,model3
```

```
# Using this format, dbt_schema_generator would generate a schema.yml file for all models within your_folder
dbt_schema_generator -path models/your_folder
dbt_schema_generator --path models/your_folder
```
NOTE: When using path the format should always be models/ the folder unless you have changed the model-paths in your dbt_project.yml

**NOTE: When using the `--path` option, the format should always be `models/your_folder` unless you have changed the `model-paths` in your `dbt_project.yml`.**



## **!!!!IMPORTANT!!!!: Be very careful when using the --path method as this would overwrite any schema.yml currently within the folder**
