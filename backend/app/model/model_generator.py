from pathlib import Path

from datamodel_code_generator import generate, InputFileType, PythonVersion

generate(input_=Path('../openapi3_0.yaml'),
         input_file_type=InputFileType.OpenAPI,
         output=Path('trading_platform_model.py'),
         target_python_version=PythonVersion.PY_312,
         snake_case_field=True)

