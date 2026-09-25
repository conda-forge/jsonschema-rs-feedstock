import sys
from pathlib import Path
from subprocess import call
import os
from typing import Any
import json

PYTHON_MIN = os.environ["python_min"]
SRC_DIR = Path(os.environ["SRC_DIR"])
SP_DIR = Path(os.environ["SP_DIR"])
IS_ABI3 = json.loads(os.environ["is_abi3"])
ABI3_EXT = "pyd" if os.name == "nt" else "pyo3.so"


UNLINK_TESTS = [
    # needs fixtures from `jsonschema` submodule (#28)
    "crates/jsonschema-py/tests-py/test_annotation_suite.py",
]

COMMENT_TESTS = {
    # needs unpackaged jsonschema_testsuite_pyo3
    "crates/jsonschema-py/tests-py/test_suite.py": [
        ("import jsonschema_testsuite_pyo3", "#"),
    ]
}

SKIPS = [
    # not relevant
    "readme",
    # needs jsonschema_testsuite_pyo3
    "test_draft_codegen",
]

PYTEST_ARGS = [
    "pytest",
    "-vv",
    "--tb=long",
    "--color=yes",
    "crates/jsonschema-py",
    "-k"
    f"""not ({" or ".join(SKIPS)})""",
]


def unlink_tests() -> int:
    for name in UNLINK_TESTS:
        (SRC_DIR / name).unlink()
    return 0


def comment_tests() -> int:
    for name, patterns in COMMENT_TESTS.items():
        path = Path(SRC_DIR / name)
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
        *SP_DIR.glob(f"jsonschemea_rs/**/*.{ABI3_EXT}"),
    )


def do(*args: Any) -> int:
    str_args = list(map(str, args))
    print(">>>", *str_args)
    return call(str_args)


if __name__ == "__main__":
    sys.exit(unlink_tests() or comment_tests() or do(*PYTEST_ARGS) or maybe_abi3audit())
