Changelog for clarity_scripts
=============================

0.17 (unreleased)
-----------------

- Nothing changed yet.


0.16 (2019-11-05)
-----------------

- Bug fixes in generate_hamilton_input_make_cst.py and populate_batch_id.py 


0.15 (2019-10-01)
-----------------

- New script for generating Human Tissue Storage Reports
  - Details on samples recorded in the LIMS as being currently stored in the lab
  - New config: human_tissue.recipients


0.14 (2019-09-13)
-----------------

- Remove tracking letter from customer manifest

0.13 (2019-07-26)
-----------------

- Updating EGCG-Core to v0.11.1
- New pooling and CST workflow scripts:
  - autoplacement_8_well.py
  - check_index_compatibility.py
  - check_plates_libraries_indexes.py
  - generate_hamilton_input_make_cst.py
  - generate_hamilton_input_make_pdp.py
  - generate_hamilton_input_make_pdp_mix.py
  - populate_batch_id.py
  - populate_pool_batch_and_pools.py
  - transfer_udf_input_output.py
  


0.12.3 (2019-07-10)
-------------------

- 'gender' API key renamed to 'sex'


0.12.2 (2019-05-30)
-------------------

- copy_samples.py: “Comments” step UDF in “Remove from processing” step now populated with description “Repeat samples requested.”


0.12.1 (2019-05-09)
-------------------

- `common.py` - Bugfix to allow naming of SGP tube racks


0.12 (2019-05-09)
-----------------

New scripts:
- `copy_samples.py` : Create new samples from the ones in the step
- `generate_hamilton_input_qpcr_dilution.py`: Generate Hamilton input file for the the QPCR dilution 
- `next_step_assignment_spectramax.py`: Set next step after spectramax step
Other changes:
- `next_step_assignment_sample_receipt.py`: Change Step UDF name
- `common.py`: Add finish_step function to safely finish an "in progress" step


0.11.2 (2019-04-11)
-------------------

- `assign_workflow_post_receive_sample.py`: routing FluidX tubes to FluidX receipt/transfer workflow
- `create_samples.py`: fixing container name regexes
- `create_sample_tracking_letter.py`: removing single input container constraint
- `generate_hamilton_input_UPL.py`: fixing blank lines in output file
- `generate_manifest.py`: fixing UDF parsing - reverting refactor
- `parse_fluidx_scan.py`: adding container name check
-milton_input_make_cst.py fixing StepEPP max_nb_input_container_typea 


0.11.1 (2019-04-02)
-------------------

- Fix for unexpected NotImplementedError in spectramax.py
- Configurable workflow stage names for assigning samples to PCR-free/Nano/KAPA/Quant
- Fixed KAPA workflow stage name
- Fixed autoplacement input columns
- Binary file support
- Customer manifest email template
- New scripts:
    - assign_workflow_post_receive_sample.py
    - create_sample_tracking_letter.py
    - create_samples.py
    - email_container_dispatched.py
    - email_container_ready_for_dispatch.py
    - email_manifest_tracking_letter_customer.py
    - email_sample_review.py
    - generate_sample_manifest.py
    - next_step_assignment_sample_receipt.py
    - next_step_assignment_udf.py
    - parse_fluidx_scan.py
    - parse_manifest.py
    - project_udfs_to_step_udfs.py
    - step_udf_completion_check.py


0.11 (2019-03-25)
-----------------

- EPP common: Generic Autoplacement class 
- `autoplacement_96_well.py`: place all input from up to 27 input plate to 1 output plate. (input plate are ordered by name)
- `generate_hamilton_input_quant_studio.py` : create one to three hamilon input files from up to load sample from up to 27 input plates
- `normalisation.py`: look up the udf from artifact or sample when normalising concentration


0.10 (2019-03-15)
-----------------

- EPP common: 
   - New validation framework that check step parameters before the `_run` function is used.
   - generic GenerateHamiltonInputEPP and ParseSpectramaxEPP class
- Test common: new class to generate Fake entities within a step or a process.
- KAPA library prep support scripts that helps:
   - with autoplacement in plates (`autoplacement_24_imp_gx`, `autoplacement_24_in_96`, `autoplacement_qpcr_384`)
   - Hamilton worklist generation (`generate_hamilton_input_cfp`, `generate_hamilton_input_imp_ssqc`, `generate_hamilton_input_ntp`, `generate_hamilton_input_qpcr_1to24`, `generate_hamilton_input_seq_quant_plate`, `generate_hamilton_input_uct`)
   - next step assignment (`next_step_assignment_gx`, `next_step_assignment_imp_ssqc`, `next_step_assignment_kapa_qc`, `next_step_assignment_kapa_qpcr`, `next_step_assignment_seq_pico`
   - out of workflow routing (`assign_workflow_kapa_qc`, `assign_workflow_preseqlab`, `assign_workflow_seqlab_quantstudio`)
   - `normalisation`: used to calculate volume of sample and buffer
   - `qc_check`: generic script to check specific UDF values
   - `check_container_name`: Ensure the name of container follows a specific format
- Spectramax parsing: `spectramax_sample_quant` `spectramax_seq_plate_quant` both parse spectramax output file at different time 


0.9.1 (2018-11-13)
------------------

- Enabled multiple projects for sample disposal emails


0.9 (2018-10-04)
----------------

- PEP8 refactor
- Boilerplate reduction
  - EPPs are now initialised without arguments, rather than step_uri, username, password, log_file
  - For adding extra arguments, EPPs can define the method `add_args(argparser)`
- Adding `email_sample_disposal_notification.py`
- Adding `email_sample_disposal_review.py`
- Fixing mean coverage query in `populate_review_step.py`
- Expanding valid container names in `prepare_discard_plate.py`
- Rewriting `remove_from_freezer.py`


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
