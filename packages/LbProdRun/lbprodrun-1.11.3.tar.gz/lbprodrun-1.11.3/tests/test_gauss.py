###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json

from typer.testing import CliRunner

from LbProdRun.__main__ import app

runner = CliRunner()


RUN3_GAUSS_CONFIG = {
    "spec_version": 1,
    "application": {
        "data_pkgs": ["AppConfig.v3r450", "Gen/DecFiles.v30r119"],
        "name": "Gauss",
        "number_of_processors": 1,
        "version": "v49r25",
        "binary_tag": "x86_64-slc6-gcc48-opt",
        "event_timeout": None,
    },
    "options": {
        "files": [
            "$APPCONFIGOPTS/Gauss/Sim08-Beam4000GeV-mu100-2012-nu2.5.py",
            "$APPCONFIGOPTS/Gauss/DataType-2012.py",
            "$APPCONFIGOPTS/Gauss/RICHRandomHits.py",
            "$APPCONFIGOPTS/Gauss/NoPacking.py",
            "$DECFILESROOT/options/11434000.py",
            "$LBPYTHIA8ROOT/options/Pythia8.py",
            "$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py",
            "",
        ],
        "processing_pass": None,
    },
    "db_tags": {"dddb_tag": "dddb-20170721-2", "conddb_tag": "sim-20160321-2-vc-mu100"},
    "input": {
        "files": [],
        "first_event_number": 11230661,
        "tck": "",
        "xml_file_catalog": "pool_xml_catalog.xml",
        "xml_summary_file": "summaryGauss_00291403_00028946_1.xml",
        "n_of_events": 388,
        "run_number": 29169246,
    },
    "output": {"prefix": "00291403_00028946_1", "types": ["sim"]},
}


def test_franklin_run3_moore(tmp_path, monkeypatch):
    tmp_path = tmp_path / "prod_spec.json"
    tmp_path.write_text(json.dumps(RUN3_GAUSS_CONFIG))
    result = runner.invoke(app, [str(tmp_path), "--verbose", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Gauss/v49r25" in result.output
    assert "ProdConf" in result.output
