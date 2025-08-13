from typing import List, Tuple

import maccel.maccel as _cMaccel
from .type import *

_Shape = Tuple[int, ...]

##
# \addtogroup PythonAPI
# @{


class ModelVariantHandle:
    def __init__(self, _model_variant_handle: _cMaccel.ModelVariantHandle):
        self._model_variant_handle = _model_variant_handle
        self._output_shape = self.get_model_output_shape()

    @classmethod
    def from_cpp(cls, _model_variant_handle: _cMaccel.ModelVariantHandle):
        return cls(_model_variant_handle)

    def get_model_input_shape(self) -> List[_Shape]:
        return self._model_variant_handle.get_model_input_shape()

    def get_model_output_shape(self) -> List[_Shape]:
        return self._model_variant_handle.get_model_output_shape()

    def get_input_buffer_info(self) -> List[BufferInfo]:
        return [
            BufferInfo.from_cpp(bi)
            for bi in self._model_variant_handle.get_input_buffer_info()
        ]

    def get_output_buffer_info(self) -> List[BufferInfo]:
        return [
            BufferInfo.from_cpp(bi)
            for bi in self._model_variant_handle.get_output_buffer_info()
        ]

    def get_input_scale(self) -> List[Scale]:
        return [Scale.from_cpp(s) for s in self._model_variant_handle.get_input_scale()]

    def get_output_scale(self) -> List[Scale]:
        return [
            Scale.from_cpp(s) for s in self._model_variant_handle.get_output_scale()
        ]

    def acquire_input_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        return [
            Buffer(b) for b in self._model_variant_handle.acquire_input_buffer(seqlens)
        ]

    def acquire_output_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        return [
            Buffer(b) for b in self._model_variant_handle.acquire_output_buffer(seqlens)
        ]

    def release_buffer(self, buffer: List[Buffer]) -> None:
        self._model_variant_handle.release_buffer([b._buffer for b in buffer])

    def reposition_inputs(
        self,
        inputs: List[np.ndarray],
        input_bufs: List[Buffer],
        seqlens: List[List[int]] = [],
    ) -> None:
        inputs = [np.ascontiguousarray(i) for i in inputs]
        self._model_variant_handle.reposition_inputs(
            inputs, [buf._buffer for buf in input_bufs], seqlens
        )

    def reposition_outputs(
        self,
        output_bufs: List[Buffer],
        outputs: List[np.ndarray],
        seqlens: List[List[int]] = [],
    ) -> None:
        if len(outputs) != len(self._output_shape):
            outputs.clear()
            for shape in self._output_shape:
                outputs.append(np.empty(shape=shape, dtype=np.float32))
        else:
            for oi in range(len(outputs)):
                outputs[oi] = np.ascontiguousarray(outputs[oi])
        self._model_variant_handle.reposition_outputs(
            [buf._buffer for buf in output_bufs], outputs, seqlens
        )


##
# @}
