from habana_frameworks.mediapipe.operators.media_nodes import MediaReaderNode
from habana_frameworks.mediapipe.backend.utils import get_media_dtype
from habana_frameworks.mediapipe.backend.utils import get_str_dtype
import numpy as np
import copy
import inspect


class reader_cpu_ops_node(MediaReaderNode):
    """
    Class representing media random biased crop cpu node.

    """

    def __init__(self, name, guid, device, inputs, params, cparams, node_attr, fw_params):
        """
        Constructor method.

        :params name: node name.
        :params guid: guid of node.
        :params guid: device on which this node should execute.
        :params params: node specific params.
        :params cparams: backend params.
        :params node_attr: node output information
        """
        super().__init__(
            name, guid, device, inputs, params, cparams, node_attr, fw_params)

    def gen_output_info(self):
        """
        Method to generate output type information.

        :returns : output tensor information of type "opnode_tensor_info".
        """
        pass

    def __iter__(self):
        """
        Callable class method.

        :params img: image data
        :params lbl: label data
        """
        pass

    def __next__(self):
        """
        Callable class method.

        :params img: image data
        :params lbl: label data
        """
        pass

    def get_largest_file(self):
        """
        Method to get largest media in the dataset.

        returns: largest media element in the dataset.
        """
        pass

    def get_media_output_type(self):
        pass

    def __len__(self):
        """
        Method to get dataset length.

        returns: length of dataset in units of batch_size.
        """
        pass


class cpu_reader_node(reader_cpu_ops_node):
    def __init__(self, name, guid, device, inputs, params, cparams, node_attr, fw_params):
        """
        Constructor method.

        :params name: node name.
        :params guid: guid of node.
        :params guid: device on which this node should execute.
        :params params: node specific params.
        :params cparams: backend params.
        :params node_attr: node output information
        """
        super().__init__(name, guid, device, inputs,
                         params, cparams, node_attr, fw_params)
        self.params_orig = copy.deepcopy(params)
        self.dtype = get_str_dtype(node_attr[0]['outputType'])
        self.params_orig['dtype'] = self.dtype
        self.params_orig['unique_number'] = self.counter
        spec = inspect.getfullargspec(self.params['func'])
        if (len(spec.args) != 2):
            msg = "{} constructor must take two arguments".format(
                str(self.params['func']))
            raise RuntimeError(msg)
        self.func_obj = self.params['func'](self.params_orig)
        if (not isinstance(self.func_obj, MediaReaderNode)):
            print(isinstance(self.func_obj, MediaReaderNode))
            raise ValueError(
                "Tensor node function must be of type TensorFunctionNode")
        spec = inspect.getfullargspec(self.func_obj)
        if ((len(spec.args) - 1) != len(inputs)):
            msg = "{} callable entity must take {} arguments".format(
                str(self.params['func']), len(inputs) + 1)
            raise RuntimeError(msg)
        self.params.clear()
        self.params['dtype'] = get_media_dtype(self.params_orig['dtype'])
        self.params['shape'] = self.params_orig['shape']
        self.params['impl'] = self.params_orig['func']
        self.params['seed'] = self.params_orig['seed']
        self.impl = self.params['impl'](self.params_orig)

    def iter(self, inputs):
        np_inputs = []
        for i in inputs:
            np_inputs.append(np.array(i, copy=False))
        outputs = []
        np_outputs = self.impl(np_inputs)
        if (isinstance(np_outputs, tuple)):
            np_outputs = list(np_outputs)
        else:
            np_outputs = [np_outputs]
        return np_outputs

    def run(self, inputs):
        np_inputs = []
        for i in inputs:
            np_inputs.append(np.array(i, copy=False))
        outputs = []
        np_outputs = self.impl(np_inputs)
        if (isinstance(np_outputs, tuple)):
            np_outputs = list(np_outputs)
        else:
            np_outputs = [np_outputs]
        return np_outputs
