"""Functions for reading and writing input/output files."""
import csv
import os
from typing import Dict, List, Type

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from epeira.helpers.marking import is_subcomponent
from epeira.helpers.parsing import get_model_catalog_suffix, get_model_input_suffix


def write_input_file_from_catalogs(catalogs: List[Dict[str, List[Type[BaseModel]]]], filename: str) -> None:
    """Use one or more catalogs to prepare an input dictionary.

    Takes a list of dictionaries that each contain lists of models, which could be component,
    cost, or other mixin models. Catalog keys must follow the naming conventions in parsing.py.

    If there is only one entry in the list for a given model type, that will be used in the input
    dictionary. If not, the model will be listed as [TBD], to be filled out manually.
    All attributes of each model available will be listed if they do not already exist in the input
    file. If they are added, they will have value [TBD] and description "[TBD]".
    """
    # Load existing parameters if file exists
    existing_params = set()

    if os.path.exists(filename):
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            existing_params = {row['parameter'] for row in rows}
    else:
        rows = []


    # Process catalogs
    for catalog in catalogs:
        for key, model_list in catalog.items():
            if not key.endswith(get_model_catalog_suffix()):
                raise Exception(f"Model key {key} must follow the format "
                                f"in the parsing module and end with {get_model_catalog_suffix()}.")
            model_name = '[TBD]'
            if len(model_list) == 1:
                model_name = model_list[0].__name__
            newkey = key.removesuffix(get_model_catalog_suffix())+get_model_input_suffix()
            if newkey not in existing_params:
                rows.append({
                    'parameter':newkey,
                    'value': model_name,
                    'description':'[TBD]'
                })
            for model_cls in model_list:
                # Get field names from the Pydantic model
                for field_name, field in model_cls.model_fields.items():
                    if is_subcomponent(field):
                        continue
                    param_name = f"{field_name}"
                    if param_name not in existing_params:
                        if field.default is not PydanticUndefined:
                            value = str(field.default)
                        else:
                            value = '[TBD]'
                        rows.append({
                            'parameter': param_name,
                            'value': value,
                            'description': '[TBD]'
                        })
                        existing_params.add(param_name)

    # Write the updated rows back to file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        f.write("parameter,value,description\n")
        for row in rows:
            f.write(f'{row["parameter"]},{row["value"]},"{row["description"]}"\n')
