
# Top-level sections

## Jobs
Specifies a list of jobs and/or job sets. Job-sets are specified in 
separate files.

```
jobs:
  - a
    - path: subdir/jobs.yaml
```

Job names inside `subdir/jobs.yaml` will be prefixed with `a`.

```
jobs
  - b
    - command: |
      echo "jobs" > mkdv.yaml
    - path: mkdv.yaml
```
    

Job-sets may be generated. Job-set generation is considered a build
step, since it may be time-consuming. This limits the ability of 
the user to list the generated jobs, but is a very powerful capability.

jobs