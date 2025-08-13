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


RUN3_MOORE_CONFIG = {
    "spec_version": 1,
    "application": {
        "data_pkgs": ["SprucingConfig.v25r5"],
        "name": "Franklin",
        "number_of_processors": 1,
        "version": "v1r9999",
        "event_timeout": None,
    },
    "options": {
        "entrypoint": "SprucingConfig.Spruce25.Sprucing_production_physics_pp_Collision25c0:turbospruce",
        "extra_options": {
            "input_process": "Hlt2",
            "write_options_to_fsr": True,
            "process": "TurboSpruce",
            "input_type": "RAW",
            "input_raw_format": 0.5,
            "data_type": "Upgrade",
            "simulation": False,
            "geometry_version": "run3/2025-v00.01",
            "conditions_version": "master",
            "output_type": "ROOT",
        },
        "extra_args": [],
    },
    "db_tags": {},
    "input": {
        "files": ["./320171_00080000_0002.raw"],
        "first_event_number": 0,
        "tck": "",
        "xml_file_catalog": "pool_xml_catalog.xml",
        "xml_summary_file": "summaryMoore_00289988_00000004_1.xml",
        "n_of_events": -1,
        "run_number": "320171",
    },
    "output": {
        "prefix": "00289988_00000004_1",
        "types": [
            "b2cc.dst",
            "b2oc.dst",
            "b2oclow.dst",
            "bandq.dst",
            "bandqlow.dst",
            "bnoc.dst",
            "bnoclow.dst",
            "charmcpv.dst",
            "charmlow.dst",
            "charmrare.dst",
            "charmspectr.dst",
            "ift.dst",
            "iftlow.dst",
            "qee.dst",
            "qeelow.dst",
            "rd.dst",
            "rdlow.dst",
            "trackeff.dst",
        ],
    },
}

RUN2_DAVINCI_CONFIG = {
    "application": {
        "binary_tag": "x86_64_v2-el9-gcc13-opt",
        "data_pkgs": ["AnalysisProductions.v1r3239"],
        "event_timeout": None,
        "name": "Franklin",
        "nightly": None,
        "number_of_processors": 1,
        "version": "v1r37",
    },
    "db_tags": {"conddb_tag": None, "dddb_tag": None, "dq_tag": None},
    "input": {
        "files": [
            "LFN:/lhcb/LHCb/Collision18/CHARMCOMPLETEEVENT.DST/00209985/0002/00209985_00020264_1.charmcompleteevent.dst"
        ],
        "first_event_number": 0,
        "n_of_events": -1,
        "run_number": None,
        "tck": "",
        "xml_file_catalog": "pool_xml_catalog.xml",
        "xml_summary_file": "summaryFranklin_00012345_00006789_1.xml",
    },
    "options": {
        "command": ["gaudirun.py", "-T"],
        "files": [
            "$ANALYSIS_PRODUCTIONS_DYNAMIC/yingl_slbaryon/2018_MagUp_collision_Xib2Xic3pi_autoconf.py",
            "$ANALYSIS_PRODUCTIONS_BASE/yingl_slbaryon/DV_Xi3pi_Xib.py",
        ],
        "format": "WGProd",
        "gaudi_extra_options": None,
        "processing_pass": None,
    },
    "output": {
        "compression": None,
        "histogram_file": None,
        "prefix": "00012345_00006789_1",
        "types": ["xic3pi.root"],
    },
    "spec_version": 1,
}


def test_franklin_run3_moore(tmp_path, monkeypatch):
    tmp_path = tmp_path / "prod_spec.json"
    tmp_path.write_text(json.dumps(RUN3_MOORE_CONFIG))
    result = runner.invoke(app, [str(tmp_path), "--verbose", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Franklin/v1r9999" in result.output
    assert (
        "SprucingConfig.Spruce25.Sprucing_production_physics_pp_Collision25c0:turbospruce"
        in result.output
    )
    assert "ProdConf" not in result.output


def test_franklin_run2_davinci(tmp_path, monkeypatch):
    tmp_path = tmp_path / "prod_spec.json"
    tmp_path.write_text(json.dumps(RUN2_DAVINCI_CONFIG))
    result = runner.invoke(app, [str(tmp_path), "--verbose", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Franklin/v1r37" in result.output
    assert "gaudirun.py -T" in result.output
    assert "ProdConf" in result.output
