import sys
from pathlib import Path
from subprocess import call
import os
from typing import Any
import json

PYTHON_MIN = os.environ["PYTHON_MIN"]
SP_DIR = Path(os.environ["SP_DIR"])

IS_ABI3 = bool(json.loads(os.environ["IS_ABI3"].lower()))
ABI3_EXT = "pyd" if os.name == "nt" else "abi3.so"


UNLINK_TESTS = [
    # needs fixtures from `jsonschema` submodule (#28)
    "crates/jsonschema-py/tests-py/test_annotation_suite.py",
]

NO_JS_TEST_PYO3 = ("import jsonschema_testsuite_pyo3", "# not packaged")

PATCH_TESTS = {
    # needs unpackaged jsonschema_testsuite_pyo3 (#67)
    "crates/jsonschema-py/tests-py/test_suite.py": [NO_JS_TEST_PYO3],
    "crates/jsonschema-py/tests-py/conftest.py": [NO_JS_TEST_PYO3]
}

SKIPS = [
    # not relevant
    "readme",
    # needs jsonschema_testsuite_pyo3 (#67)
    "codegen",
    "concurrent_mutation_does_not_crash",
]

PYTEST_ARGS = [
    "pytest",
    "-vv",
    "--tb=long",
    "--color=yes",
    "crates/jsonschema-py",
    "-k",
    f"""not ({" or ".join(SKIPS)})""",
]


def unlink_tests() -> int:
    for name in UNLINK_TESTS:
        Path(name).unlink()
    return 0


def patch_tests() -> int:
    for name, patterns in PATCH_TESTS.items():
        path = Path(name)
        text = path.read_text(encoding="utf-8")
        for find, replace in patterns:
            text = text.replace(find, replace)
        path.write_text(text, encoding="utf-8")
    return 0


def maybe_abi3audit() -> int:
    if not IS_ABI3:
        return 0

    return do(
        "abi3audit",
        "-s",
        "-v",
        "--assume-minimum-abi3",
        PYTHON_MIN,
        *SP_DIR.glob(f"jsonschema_rs/**/*.{ABI3_EXT}"),
    )


def do(*args: Any) -> int:
    str_args = list(map(str, args))
    print(">>>", *str_args, flush=True)
    return call(str_args)


if __name__ == "__main__":
    print(f"PYTHON_MIN: {PYTHON_MIN}  IS_ABI3: {IS_ABI3}  ABI3_EXT: {ABI3_EXT}")
    sys.exit(unlink_tests() or patch_tests() or do(*PYTEST_ARGS) or maybe_abi3audit())
