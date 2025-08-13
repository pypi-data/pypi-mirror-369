from typing import List, Optional

import numpy as np

import maccel.maccel as _cMaccel


##
# \addtogroup PythonAPI
# @{


class Future:
    def __init__(
        self,
        _future: _cMaccel.Future = None,
        _inputs: Optional[List[np.ndarray]] = None,
    ):
        self._future = _future if _future is not None else _cMaccel.Future()
        # self._inputs holds user inputs to prevent them from being garbage collected
        # before asynchronous inference is completed.
        self._inputs = _inputs

    @classmethod
    def from_cpp(cls, _future: _cMaccel.Future, _inputs: List[np.ndarray]):
        return cls(_future, _inputs)

    def wait_for(self, timeout_ms: int) -> bool:
        return self._future.wait_for(timeout_ms)

    def get(self) -> List[np.ndarray]:
        outputs = self._future.get()
        self._inputs = None
        return [np.asarray(o) for o in outputs]


##
# @}
