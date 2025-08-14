import numpy as np


class CPUTensor(object):
    """
    Class defining CPU tensor of mediapipe.

    """

    def __init__(self, tensor, arr, pm):
        """
        Constructor method.

        :params tensor: TensorNode type tensor(raw tensor).
        :params arr: numpy array to holding data element.
        """
        self.__tensor = tensor
        self.__arr = arr
        self.name = tensor.name
        self.shape = tensor.shape
        self.np_shape = tensor.np_shape
        self.dtype = tensor.dtype
        self.np_dtype = tensor.np_dtype
        self.size = tensor.size
        self.device = "cpu"

    def as_nparray(self):
        """
        Method to get np array from host tensor.

        :returns : host numpy array.
        """
        return self.__arr

    def get_shape(self):
        return self.shape

    def get_dtype(self):
        return self.dtype


class HPUTensor(object):
    """
    Class defining HPU tensor of mediapipe.

    """

    def __init__(self, tensor, dev_addr, pm):
        """
        Constructor method.

        :params tensor: TensorNode type tensor(raw tensor).
        :params dev_addr: device address holding data element.
        :params pm: backend pipe manager.
        """
        self.__pm = pm
        self.__tensor = tensor
        self.name = tensor.name
        self.shape = tensor.shape
        self.np_shape = tensor.np_shape
        self.dtype = tensor.dtype
        self.np_dtype = tensor.np_dtype
        self.size = tensor.size
        self.dev_addr = dev_addr
        self.device = "hpu"

    def as_cpu(self):
        """
        Method to fetch data from device to host.

        :returns : CPU tensors for host processing.
        """
        arr = np.zeros(self.np_shape,
                       self.np_dtype)
        self.__pm.as_cpu(self.dev_addr, arr)
        tensor = CPUTensor(self.__tensor, arr, self.__pm)
        return tensor

    def get_shape(self):
        return self.np_shape

    def get_dtype(self):
        return self.dtype

    def get_addr(self):
        return self.dev_addr

    def __del__(self):
        """
        Destructor method.

        """
        self.__pm.free_device_tensor(self.dev_addr)
