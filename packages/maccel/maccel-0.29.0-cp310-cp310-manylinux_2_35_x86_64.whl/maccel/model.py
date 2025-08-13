from typing import List, Optional, Tuple, Union

import numpy as np

import maccel.maccel as _cMaccel
from .accelerator import Accelerator
from .future import *
from .model_variant_handle import *
from .type import *

_Shape = Tuple[int, ...]

__all__ = ["Model", "load"]


##
# \addtogroup PythonAPI
# @{


# input ndarray의 shape이 유효한 shape인지 판별한다.
def _is_valid_shape(input_shape: _Shape, shape: _Shape) -> bool:
    if (len(input_shape) < len(shape)) or (len(input_shape) > len(shape) + 1):
        return False
    # input을 batch일 경우도 고려하여 [h, w, c] 및 [batch, h, w, c] 모두 고려한다
    offset = 1 if len(input_shape) > len(shape) else 0
    for s1, s2 in zip(input_shape[offset:], shape):
        # Dimensions that allow variable lengths are represented by negative values.
        # A variable-length dimension only permits multiples of the original value.
        if s1 % s2 != 0 or (s2 > 0 and s1 != s2):
            return False
    return True


# input ndarray의 shape를 검사하여 HWC인지 CHW인지 판별한다.
def _is_shape_hwc(inputs: List[np.ndarray], shapes: List[_Shape]) -> Optional[bool]:
    if len(inputs) != len(shapes):
        return None

    is_hwc = True
    is_chw = True
    for arr, shape in zip(inputs, shapes):
        shape_hwc = (shape[0], shape[1], shape[2])
        shape_chw = (shape[2], shape[0], shape[1])
        is_hwc = is_hwc and _is_valid_shape(arr.shape, shape_hwc)
        is_chw = is_chw and _is_valid_shape(arr.shape, shape_chw)

    if not is_hwc and not is_chw:
        return None
    # If both `is_hwc` and `is_chw` are `True`, the memory format is assumed to be HWC.
    return is_hwc


def _find_matching_variant_idx_and_is_hwc(
    model, inputs: List[np.ndarray]
) -> Tuple[int, bool]:
    variant_idx = None
    is_hwc = None
    for i in range(model.get_num_model_variants()):
        is_hwc = _is_shape_hwc(
            inputs, model.get_model_variant_handle(i).get_model_input_shape()
        )
        if is_hwc is not None:
            variant_idx = i
            break

    if is_hwc is None:
        raise ValueError("Input shape is invalid.")
    assert variant_idx is not None
    return variant_idx, is_hwc


# shape에 맞게 numpy ndarray를 생성한다.
def _build_outputs(
    shapes: List[_Shape], is_hwc: bool, dtype: np.dtype
) -> List[np.ndarray]:
    outputs = []
    for shape in shapes:
        if is_hwc:
            shape = (shape[0], shape[1], shape[2])
        else:
            shape = (shape[2], shape[0], shape[1])
        outputs.append(np.empty(shape, dtype=dtype))
    return outputs


# output에 들어있는 numpy ndarray의 shape가 올바른지 검사한다.
def _check_output_shapes(
    outputs: List[np.ndarray], shapes: List[_Shape], is_hwc: bool, dtype: np.dtype
) -> None:
    if len(outputs) != len(shapes):
        raise ValueError("The number of outputs is different.")

    for output, shape in zip(outputs, shapes):
        if output.dtype != dtype:
            raise ValueError("Output dtype mismatch.")

        if is_hwc:
            shape = (shape[0], shape[1], shape[2])
        else:
            shape = (shape[2], shape[0], shape[1])
        if output.shape != shape:
            raise ValueError("Output shape mismatch.")


class Model:
    def __init__(self, path: str, model_config: Optional[ModelConfig] = None):
        if model_config is None:
            self._model = _cMaccel.Model(path)
        else:
            self._model = _cMaccel.Model(path, model_config._model_config)

        # 기존 BufferInfo 대신에 ModelShape를 사용한다.
        # Model {input,output} shape는 batch를 포함한 4D이다.
        self._input_shape = self.get_model_input_shape()
        self._output_shape = self.get_model_output_shape()

    def launch(self, acc: Accelerator) -> None:
        self._model.launch(acc._accelerator)
        self._acc = acc

    def dispose(self) -> None:
        self._model.dispose()
        self._acc = None

    def is_target(self, core_id: CoreId) -> bool:
        return self._model.is_target(core_id._core_id)

    def get_core_mode(self) -> CoreMode:
        return CoreMode(self._model.get_core_mode())

    def get_target_cores(self) -> List[CoreId]:
        return [CoreId.from_cpp(target) for target in self._model.target_cores]

    # Deprecated
    @property
    def target_cores(self) -> List[CoreId]:
        return [CoreId.from_cpp(target) for target in self._model.target_cores]

    # 1. infer(in:List[numpy]) -> List[numpy]   (float / int)
    # 2. infer(in:numpy)       -> List[numpy]   (float / int)
    # 3. infer(in:List[numpy], out:List[numpy]) (float / int)
    # 4. infer(in:List[numpy], out:List[])      (float / int)
    # 5. infer(in:numpy, out:List[numpy])       (float / int)
    # 6. infer(in:numpy, out:List[])            (float / int)
    def infer(
        self,
        inputs: Union[np.ndarray, List[np.ndarray]],
        outputs: Optional[List[np.ndarray]] = None,
        cache_size: int = 0,
    ) -> Optional[List[np.ndarray]]:
        if not isinstance(inputs, list):
            inputs = [inputs]

        variant_idx, is_hwc = _find_matching_variant_idx_and_is_hwc(self, inputs)
        inputs = [np.ascontiguousarray(i) for i in inputs]

        if outputs is None:
            # No Output Parameter
            infer_func = self._model.infer if is_hwc else self._model.infer_chw
            return [np.asarray(o) for o in infer_func(inputs, cache_size)]

        else:
            if outputs:
                _check_output_shapes(
                    outputs,
                    self.get_model_variant_handle(variant_idx).get_model_output_shape(),
                    is_hwc,
                    inputs[0].dtype,
                )
                for oi in range(len(outputs)):
                    outputs[oi] = np.ascontiguousarray(outputs[oi])
            else:
                outputs[:] = _build_outputs(
                    self.get_model_variant_handle(variant_idx).get_model_output_shape(),
                    is_hwc,
                    inputs[0].dtype,
                )

            if is_hwc:
                self._model.infer(inputs, outputs, cache_size)
            else:
                self._model.infer_chw(inputs, outputs, cache_size)

    def infer_to_float(
        self,
        inputs: Union[
            np.ndarray,
            List[np.ndarray],
        ],
        cache_size: int = 0,
    ) -> List[np.ndarray]:
        if not isinstance(inputs, list):
            inputs = [inputs]

        _, is_hwc = _find_matching_variant_idx_and_is_hwc(self, inputs)
        inputs = [np.ascontiguousarray(i) for i in inputs]

        if is_hwc:
            outputs = self._model.infer_to_float(inputs, cache_size)
        else:
            outputs = self._model.infer_chw_to_float(inputs, cache_size)

        return [np.asarray(o) for o in outputs]

    # For backward compatibility.
    infer_chw = infer
    infer_chw_to_float = infer_to_float

    def infer_buffer(
        self,
        inputs: List[Buffer],
        outputs: List[Buffer],
        shape: List[List[int]] = [],
        cache_size: int = 0,
    ) -> None:
        self._model.infer_buffer(
            [i._buffer for i in inputs], [o._buffer for o in outputs], shape, cache_size
        )

    def infer_speedrun(self) -> None:
        self._model.infer_speedrun()

    def infer_async(
        self,
        inputs: Union[np.ndarray, List[np.ndarray]],
    ) -> Future:
        if not isinstance(inputs, list):
            inputs = [inputs]
        _, is_hwc = _find_matching_variant_idx_and_is_hwc(self, inputs)
        inputs = [np.ascontiguousarray(i) for i in inputs]
        infer_async_func = (
            self._model.infer_async if is_hwc else self._model.infer_async_chw
        )
        return Future.from_cpp(infer_async_func(inputs), inputs)

    def reposition_inputs(
        self,
        inputs: List[np.ndarray],
        input_bufs: List[Buffer],
        seqlens: List[List[int]] = [],
    ) -> None:
        inputs = [np.ascontiguousarray(i) for i in inputs]
        self._model.reposition_inputs(
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
        self._model.reposition_outputs(
            [buf._buffer for buf in output_bufs], outputs, seqlens
        )

    def get_num_model_variants(self) -> int:
        return self._model.get_num_model_variants()

    def get_model_variant_handle(self, variant_idx) -> ModelVariantHandle:
        return ModelVariantHandle.from_cpp(
            self._model.get_model_variant_handle(variant_idx)
        )

    def get_model_input_shape(self) -> List[_Shape]:
        return self._model.get_model_input_shape()

    def get_model_output_shape(self) -> List[_Shape]:
        return self._model.get_model_output_shape()

    def get_input_scale(self) -> List[Scale]:
        return [Scale.from_cpp(s) for s in self._model.get_input_scale()]

    def get_output_scale(self) -> List[Scale]:
        return [Scale.from_cpp(s) for s in self._model.get_output_scale()]

    def get_input_buffer_info(self) -> List[BufferInfo]:
        return [BufferInfo.from_cpp(bi) for bi in self._model.get_input_buffer_info()]

    def get_output_buffer_info(self) -> List[BufferInfo]:
        return [BufferInfo.from_cpp(bi) for bi in self._model.get_output_buffer_info()]

    def acquire_input_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        return [Buffer(b) for b in self._model.acquire_input_buffer(seqlens)]

    def acquire_output_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        return [Buffer(b) for b in self._model.acquire_output_buffer(seqlens)]

    def release_buffer(self, buffer: List[Buffer]) -> None:
        self._model.release_buffer([b._buffer for b in buffer])

    def get_identifier(self) -> int:
        return self._model.get_identifier()

    def get_model_path(self) -> str:
        return self._model.get_model_path()

    def get_cache_infos(self) -> List[CacheInfo]:
        return [CacheInfo.from_cpp(c) for c in self._model.get_cache_infos()]

    def get_schedule_policy(self) -> SchedulePolicy:
        return SchedulePolicy(self._model.get_schedule_policy())

    def get_latency_set_policy(self) -> LatencySetPolicy:
        return LatencySetPolicy(self._model.get_latency_set_policy())

    def get_maintenance_policy(self) -> MaintenancePolicy:
        return MaintenancePolicy(self._model.get_maintenance_policy())

    def get_latency_consumed(self) -> int:
        return self._model.get_latency_consumed()

    def get_latency_finished(self) -> int:
        return self._model.get_latency_finished()

    def reset_cache_memory(self) -> None:
        self._model.reset_cache_memory()

    def dump_cache_memory(self) -> List[bytes]:
        bufs = self._model.dump_cache_memory()
        return [np.asarray(buf, np.int8).tobytes() for buf in bufs]

    def load_cache_memory(self, bufs: List[bytes]) -> None:
        self._model.load_cache_memory(
            [np.frombuffer(buf, dtype=np.int8) for buf in bufs]
        )

    def dump_cache_memory_to(self, cache_dir: str) -> None:
        self._model.dump_cache_memory(cache_dir)

    def load_cache_memory_from(self, cache_dir: str) -> None:
        self._model.load_cache_memory(cache_dir)

    def filter_cache_tail(
        self, cache_size: int, tail_size: int, mask: List[bool]
    ) -> int:
        return self._model.filter_cache_tail(cache_size, tail_size, mask)

    def move_cache_tail(self, num_head: int, num_tail: int, cache_size: int) -> int:
        return self._model.move_cache_tail(num_head, num_tail, cache_size)


def load(path: str, model_config: Optional[ModelConfig] = None) -> Model:
    acc = Accelerator()
    model = Model(path, model_config)
    model.launch(acc)
    return model


##
# @}
