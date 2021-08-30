from mkdv.backends.backend_local import BackendLocal
from mkdv.backends.backend_slurm import BackendSlurm

_backends = {
    "local" : BackendLocal(),
    "slurm" : BackendSlurm()
    }

def backend(key):
    return _backends[key]

def backends():
    return _backends.keys()

    