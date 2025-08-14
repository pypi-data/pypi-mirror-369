import numpy as np
from habana_frameworks.mediapipe.backend.utils import media_to_np_dtype
import media_pipe_types as mpt  # NOQA
import media_pipe_nodes as mpn


class Tensor:
    def __init__(self, tensor):
        self._tensor = tensor
        self.name = tensor.name
        self.shape = tensor.Mem.shape
        self.dtype = tensor.Mem.dType
        self.size = tensor.Mem.size

    @property
    def np_dtype(self):
        return media_to_np_dtype(self.dtype)

    @property
    def np_shape(self):
        return self.shape[::-1]

    def get_shape(self):
        return self.shape

    def get_dtype(self):
        return self.dtype

    def __del__(self):
        self._tensor.Free()
        del self._tensor


class CPUTensor(Tensor):
    def __init__(self, tensor):
        super().__init__(tensor)
        self.device = "cpu"

    def as_nparray(self):
        return np.array(self._tensor)


class HPUTensor(Tensor):
    def __init__(self, tensor):
        super().__init__(tensor)
        self.dev_addr = tensor.Mem.busAddr
        self.device = "hpu"

    def as_cpu(self):
        cputensor = mpn.TensorCPU(
            self.name + '_py', self.dtype, 1.0, 0.0, self.shape)
        cputensor.ToHost(self._tensor)
        tensor = CPUTensor(cputensor)
        return tensor

    def get_addr(self):
        return self.dev_addr


def TensorPacker(tensors):
    o = []
    for t in tensors:
        if (t.device == mpn.Device_t.DEVICE_CPU):
            o.append(CPUTensor(t))
        elif (t.device == mpn.Device_t.DEVICE_HPU):
            o.append(HPUTensor(t))
        else:
            raise ValueError("Invalid tensor type received")
    if (len(o) == 1):
        return o[0]
    return o
