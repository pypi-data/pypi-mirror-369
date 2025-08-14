import os.path

import numpy as np


def get_eigency_eigen_dir():
    from importlib.resources import files

    return (files(__name__) / "eigen").__str__()


def get_includes(include_eigen=True):
    root = os.path.dirname(__file__)
    path = [root, np.get_include()]
    if include_eigen:
        __eigen_dir__ = get_eigency_eigen_dir()
        path.append(os.path.join(root, __eigen_dir__))
    return path
