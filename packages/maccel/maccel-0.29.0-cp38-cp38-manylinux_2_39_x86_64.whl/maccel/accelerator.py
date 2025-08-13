from typing import List

import maccel.maccel as _cMaccel
from .type import CoreId

__version__: str = _cMaccel.__version__


##
# \addtogroup PythonAPI
# @{


class Accelerator:
    def __init__(self, dev_no: int = 0):
        self._accelerator = _cMaccel.Accelerator(dev_no)

    def get_available_cores(self) -> List[CoreId]:
        return [
            CoreId.from_cpp(core_id)
            for core_id in self._accelerator.get_available_cores()
        ]


##
# @}
