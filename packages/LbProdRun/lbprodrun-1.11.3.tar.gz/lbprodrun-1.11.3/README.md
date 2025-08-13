# LbProdRun

LbProdRun provides a stable interface that can be used by LHCbDIRAC for configuring and launching LHCb's various software applications.
In order to generate simulated data and reproduce legacy reprocessing it is necessary for LHCbDIRAC to be able to configure applications dating back to 2011.
Previously this was handled by the [`ProdConf`](https://gitlab.cern.ch/lhcb-datapkg/ProdConf/) data package however changes to the Run 3 software stack caused `ProdConf` is not longer generic enough.
Instead `LbProdRun` provides a CLI application (`lb-prod-run`) which is passed a single JSON file as it's argument.
This file contains all of the required information to run an LHCb application and hides the details of configuring the application away from LHCbDIRAC.

## Usage

```bash
$ lb-prod-run prodspec_DaVinci_00145918_00000004_1.json
# Check the configuration is valid and print the command that would be ran
$ lb-prod-run prodspec_DaVinci_00145918_00000004_1.json --dry-run --verbose
```

## Version 1 schema

The most minimal configuration file that can be passed to version 1 of the schema is:

```json
{"spec_version": 1,
 "application": {"name": "DaVinci", "version": "v45r8"},
 "options": {"files": ["$APPCONFIGOPTS/my-options-file.py"]},
 "output": {"prefix": "00145918_00000004_1", "types": ["d02hhll.strip.mdst"]}}
```

When parsing this is padded with the default values:

```json
{"application": {"binary_tag": "best",
                 "data_pkgs": [],
                 "event_timeout": null,
                 "name": "DaVinci",
                 "number_of_processors": 1,
                 "version": "v45r8"},
 "db_tags": {"conddb_tag": null, "dddb_tag": null, "dq_tag": null},
 "input": {"files": null,
           "first_event_number": null,
           "n_of_events": -1,
           "run_number": null,
           "tck": null,
           "xml_file_catalog": null,
           "xml_summary_file": null},
 "options": {"files": ["$APPCONFIGOPTS/my-options-file.py"],
             "format": null,
             "gaudi_extra_options": null,
             "processing_pass": null},
 "output": {"histogram_file": null,
            "prefix": "00145918_00000004_1",
            "types": ["d02hhll.strip.mdst"]}}
```
