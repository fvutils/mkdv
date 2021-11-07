
- Documented schema
- Support testsuite-driven generation step
  - either per-setup or per-run
  - relies on generator plug-ins to do the heavy lifting
  - for makefile-based projects, must have access to select Make variables
  - in many cases, safe to assume the implementation will be Python

- Formalize support for run-vars and setup-vars
- Formalize support for default and override variables
- Formalize support for single-file specification of test groups
- Ensure future ability to support cross-job dependencies
  - At the user level, mostly comes from wishing to parallelize 
    sub-macro hardening
- Formalize support for job-collection 'styles', job 'runner'
  - Example: Googletest
  - User specifies location of executable (pre-built)
  - Plug-in queries 
  - Available jobs are queried by calling a command filtering 
  - Belongs under "job-group"
  - Specific tag configuring job type
  - Command-based approach to querying available jobs fits under this scheme
  
  
  - Job-runner 'class' is used for three purposes
  -> Provide available sub-jobs (optional)
    - Responsible for returning job specs 
    - Responsible for validating job context settings. 
  -> Run a specific job
    - Invoked by the job-runner wrapper
    - Provided with general and specific job parameters
  -> Run setup- and run- generation steps
    - Needed because these often depend on settings configured
      by the user-provided run-configuration file
      
Python run-configuration file
  - Sets control variables. For simplicity, can be same as makefile variables
  - Invokes mkdv common entrypoint
  
CMake run-configuration file
  - Think we can make work, provided the runner 
  
Note: jobs/job-group may be all we need
job-group:
    runner:
        ....
    ...
    jobs:
        - 
        - 
        - 
        job-group:
           ...
           jobs:
               -
               -
               -

Need to run setup for each collection of jobs with a distinct combination
of runner/params. 
  
jobs:
    job-group:
      runner:
        # Note: runner plug-in states whether it supports test discovery
        id: googletest
        params:
          test-executable: ${BUILD_DIR}/tests/test_libvsc
      jobs:
          
        

- Formalize support for execution back-ends
  - Local
- 
