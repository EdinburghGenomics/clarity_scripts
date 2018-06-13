Changelog for clarity_scripts
=============================

0.9 (unreleased)
----------------

- Nothing changed yet.


0.8 (2018-06-13)
----------------

 - `apply_freezer_location.py`: is for updating Freezer/Shelf UDFs for samples 
 - update `email_receive_sample.py` to support user prepared libraries 
 - `next_step_assignment_user_prepared_plate_receipt.py` assigns the Next Step for user prepared libraries
 - `assign_workflow_user_library.py` assigns artifacts that pass through the step to qPCR step and updates required UDF "SSQC Result" to "Passed".
 - `check_container_name.py` checks that the container names have the correct naming convention.
 - update `assign_workflow_receive_sample.py` to assign samples to User Prepared Library receipt based on UDF
 - `generate_hamilton_input_UPL.py`: create hamilton input for the UPL batching step
 - Multiple bug fixes.


0.7 (2018-05-01)
----------------

- `populate_review_step`: Change the criteria for reviewing run elements so that it is more in line with SOP.
- `assign_sample_review`: New script that assign sample after review
- `check_step_UDFs`: New script that check if UDFs are present and exist with errors if not.
- `email_data_release_facility_manager`: sent data release step notification to facility manager.
- `next_step_assignment_quantstudio_data_import`: assign next step after Quantstudio import
- `convert_and_dispatch_genotypes`: 
  - support for new format.
  - match all samples in the step with sample in the genotyping.
  - adds new UDFs in submitted sample and output artifacts.

 
0.6.2 (2018-03-26)
------------------

- Updated EGCG-Core to 0.8.1
- PEP8 refactor
- New scripts: `next_step_assignment`, `remove_from_freezer`


0.6.1 (2018-02-02)
------------------

- New email notification for Data release, Sample receipt, FluidX receipt


0.6 (2017-10-23)
----------------

- Populate steps with review metrics from the Reporting App database for samples and run elements
- Generate email requesting data release


0.5 (2017-08-30)
----------------

- Added assign_container_name


0.4.1 (2017-07-14)
------------------

- Made Spectramax able to tolerate incomplete plates


0.4 (2017-06-27)
----------------

- Moved automatic file closing to StepEPP superclass
- Added temporary copy of pyclarity_lims.lims.Lims.get_file_contents to StepEPP
- Added assign_workflow_receive_sample, assign_workflow_user_library, spectramax

0.3 (2017-06-09)
----------------

- Import of scripts from production server (cleanup and migration to python3)
- added and tested assign_workflow_preseqlab.py and assign_workflow_seqlab_quantstudio.py

0.2 (2017-04-27)
----------------
 - add accufill check in convert_and_dispatch_genotypes
 - Support for installing via setup.py

0.1.1
------
