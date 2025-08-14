from pydantic.v1 import ValidationError
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_types import (
    JumpStartResourceType,
)
from sagemaker_jupyterlab_extension_common.jumpstart.request import NotebookRequest
import pytest


@pytest.mark.parametrize(
    "input_request",
    [
        {
            "key": "pmm-notebook/notebook.ipynb",
            "resource_type": "modelSdkNotebook",
            "model_id": "test-model-id",
            "endpoint_name": "test-endpoint-name",
            "inference_component": "test-inference-component",
            "hub_name": "test-hub-name",
        },
        {
            "key": "pmm-notebook/notebook.ipynb",
            "resource_type": "modelSdkNotebook",
            "model_id": "test-model-id",
            "endpoint_name": "test-endpoint-name",
            "inference_component": "test-inference-component",
        },
        {
            "key": "nova-notebooks/notebook.ipynb",
            "recipe_path": "/recipes/training/nova/recipe.yaml",
            "resource_type": "novaNotebook",
        },
    ],
)
def test_notebook_request_happy_case(input_request):
    NotebookRequest(**input_request)


def test_notebook_request_when_only_key_is_specified():
    request = {
        "key": "pmm-notebook/notebook.ipynb",
    }
    validated_input = NotebookRequest(**request)
    assert validated_input.resource_type == JumpStartResourceType.default


@pytest.mark.parametrize(
    "notebook_request,expected",
    [
        [
            {
                "key": "pmm-notebook/notebook.ipynb",
                "resource_type": "modelSdkNotebook",
            },
            "model_id is required when resource_type is modelSdkNotebook",
        ],
        [
            {
                "key": "pmm-notebook/notebook.ipynb",
                "resource_type": "inferNotebook",
            },
            "endpoint_name is required when resource_type is inferNotebook",
        ],
        [
            {
                "key": "pmm-notebook/notebook.ipynb",
                "resource_type": "invalidNotebook",
            },
            "value is not a valid enumeration member",
        ],
        [
            {
                "key": "pmm-notebook/notebook.ip",
            },
            "string does not match regex",
        ],
        [
            {
                "key": "pmm-notebook/notebook.ipynb",
                "endpoint_name": "1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
            },
            "ensure this value has at most 63 characters",
        ],
        [
            {
                "key": "pmm-notebook/notebook.ipynb",
                "endpoint_name": "1____1",
            },
            "string does not match regex",
        ],
        [
            {
                "key": "nova-notebooks/notebook.ipynb",
                "recipe_path": "a" * 257,
                "resource_type": "novaNotebook",
            },
            "ensure this value has at most 256 characters",
        ],
        [
            {
                "key": "nova-notebooks/notebook.ipynb",
                "recipe_path": "path with spaces/recipe.yaml",
                "resource_type": "novaNotebook",
            },
            "string does not match regex",
        ],
        [
            {
                "key": "nova-notebooks/notebook.ipynb",
                "recipe_path": "/another/recipe_01-test.json",
                "resource_type": "novaNotebook",
            },
            "does not conform to the expected recipe path format",
        ],
        [
            {
                "key": "nova-notebooks/notebook.ipynb",
                "recipe_path": "/recipes/fine-tuning/nova/../../../bib/ls",
                "resource_type": "novaNotebook",
            },
            "does not conform to the expected recipe path format",
        ],
        [
            {
                "key": "nova-notebooks/notebook.ipynb",
                "recipe_path": "/another/recipe_01-test.json",
                "resource_type": "novaNotebook",
            },
            "does not conform to the expected recipe path format",
        ],
        [
            {
                "key": "nova-notebooks/notebook.ipynb",
                "recipe_path": "recipe_name.py",
                "resource_type": "novaNotebook",
            },
            "does not conform to the expected recipe path format",
        ],
    ],
)
def test_notebook_request_failed_with_validation_error(notebook_request, expected):
    with pytest.raises(ValidationError, match=expected):
        NotebookRequest(**notebook_request)
