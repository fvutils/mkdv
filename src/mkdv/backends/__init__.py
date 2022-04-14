from mkdv.backends.backend_local import BackendLocal
from mkdv.backends.backend_slurm import BackendSlurm
from mkdv.backends.backend_lsf import BackendLsf

_backends = {
    "local" : BackendLocal(),
    "lsf" : BackendLsf(),
    "slurm" : BackendSlurm()
    }

def backend(key):
    return _backends[key]

def backends():
    return _backends.keys()

    