import os.path

from elemental_tools.pydantic import generate_pydantic_model_from_path

this_path = os.path.abspath(__file__)
internal_scripts = generate_pydantic_model_from_path(os.path.dirname(this_path))
