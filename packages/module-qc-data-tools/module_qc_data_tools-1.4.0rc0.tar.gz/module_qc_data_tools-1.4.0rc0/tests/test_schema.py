from __future__ import annotations

import json

import jsonschema
import pytest

import module_qc_data_tools as mqdt


@pytest.fixture(scope="session")
def schema():
    return json.loads((mqdt.utils.datapath / "schema_measurement.json").read_text())


@pytest.mark.parametrize(
    ("measurement"),
    [
        "FLATNESS",
        "GLUE_MODULE_FLEX_ATTACH",
        "MASS_MEASUREMENT",
        "PARYLENE",
        "TRIPLET_METROLOGY",
        "WIREBONDING",
        "WIREBOND_PULL_TEST",
        "DE_MASKING_TEST",
    ],
)
def test_measurement(measurement, schema, datadir):
    output = json.loads(datadir.joinpath(f"{measurement}.json").read_text())
    jsonschema.validate(output, schema)
