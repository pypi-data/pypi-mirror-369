# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import re

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        help="Base URL for OpenAI compatible API",
    )
    parser.addoption(
        "--api-key",
        action="store",
        help="API key to use for the provider",
    )
    parser.addoption(
        "--provider",
        action="store",
        help="Provider to use for testing",
    )
    parser.addoption(
        "--model",
        action="store",
        help="Model to use for testing",
    )


pytest_plugins = [
    "pytest_jsonreport",
    "llama_verifications.functional_tests.openai_api.fixtures.fixtures",
    "llama_verifications.functional_tests.openai_api.fixtures.load",
]


@pytest.hookimpl(optionalhook=True)
def pytest_json_runtest_metadata(item, call):
    """Add model and case_id to pytest-json report metadata."""
    metadata = {}
    nodeid = item.nodeid

    # 1. Extract model from callspec if available
    model = item.callspec.params.get("model") if hasattr(item, "callspec") else None
    if model:
        metadata["model"] = model
    else:
        # Fallback: Try parsing from nodeid (less reliable)
        match_model = re.search(r"\[(.*?)-", nodeid)
        if match_model:
            model = match_model.group(1)  # Store model even if found via fallback
            metadata["model"] = model
        else:
            print(f"Warning: Could not determine model for test {nodeid}")
            model = None  # Ensure model is None if not found

    # 2. Extract case_id using the known model string if possible
    if model:
        # Construct a regex pattern to find the case_id *after* the model name and a hyphen.
        # Escape the model name in case it contains regex special characters.
        pattern = re.escape(model) + r"-(.*?)\]$"
        match_case = re.search(pattern, nodeid)
        if match_case:
            case_id = match_case.group(1)
            metadata["case_id"] = case_id
        else:
            # Fallback if the pattern didn't match (e.g., nodeid format unexpected)
            # Try the old less specific regex as a last resort.
            match_case_fallback = re.search(r"-(.*?)\]$", nodeid)
            if match_case_fallback:
                case_id = match_case_fallback.group(1)
                metadata["case_id"] = case_id
                print(f"Warning: Used fallback regex to parse case_id from nodeid {nodeid}")
            else:
                print(f"Warning: Could not parse case_id from nodeid {nodeid} even with fallback.")
                if "case" in (item.callspec.params if hasattr(item, "callspec") else {}):
                    metadata["case_id"] = "parsing_failed"
    elif "case" in (item.callspec.params if hasattr(item, "callspec") else {}):
        # Cannot reliably parse case_id without model, but we know it's a case test.
        # Try the generic fallback regex.
        match_case_fallback = re.search(r"-(.*?)\]$", nodeid)
        if match_case_fallback:
            case_id = match_case_fallback.group(1)
            metadata["case_id"] = case_id
            print(f"Warning: Used fallback regex to parse case_id from nodeid {nodeid} (model unknown)")
        else:
            print(f"Warning: Could not parse case_id from nodeid {nodeid} (model unknown)")
            metadata["case_id"] = "parsing_failed_no_model"
    # else: Not a test with a model or case param we need to handle.

    return metadata


@pytest.fixture(autouse=True)
def skip_unless_selected_model(request):
    selected_model = request.config.getoption("--model")
    if not selected_model:
        return  # No filter, run all
    # Try to get the test's model param value
    model_param = None
    if hasattr(request.node, "callspec"):
        model_param = request.node.callspec.params.get("model", None)
    if model_param is not None and model_param != selected_model:
        pytest.skip(f"Skipping model {model_param} because --model={selected_model} was specified")
