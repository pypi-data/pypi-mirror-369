from habana_frameworks.mediapipe.backend.nodes import opnode_tensor_info
from habana_frameworks.mediapipe.operators.media_nodes import MediaReaderNode
from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.media_types import readerOutType as ro

import numpy as np
from queue import Queue


class read_media_from_ext(MediaReaderNode):
    """
    Class defining read video from directory node.

    """

    def __init__(self, name, guid, device, inputs, params, cparams, node_attr, fw_params):
        """
        Constructor method.

        :params name: node name.
        :params guid: guid of node.
        :params device: device on which this node should execute.
        :params params: node specific params.
        :params cparams: backend params.
        :params node_attr: node output information
        """
        super().__init__(
            name, guid, device, inputs, params, cparams, node_attr, fw_params)

        assert fw_params.queue_depth == 0, "expect 0 queue depth for ext reader"
        self.num_batches_slice = 0
        self.first_file = ""
        self.ext_queue = params['ext_queue']
        self.batch_size = fw_params.batch_size

        print("media reader: batch size: {} queue: {}".format(
            self.batch_size, self.ext_queue))

        assert isinstance(self.ext_queue, Queue), "ext_queue not set"

    def gen_output_info(self):
        """
        Method to generate output type information.

        :returns : output tensor information of type "opnode_tensor_info".
        """

        out_info = []
        o = opnode_tensor_info(dt.NDT,
                               np.array([self.batch_size],
                                        dtype=np.uint32),
                               "")
        out_info.append(o)

        return out_info

    def get_largest_file(self):
        """
        Method to get largest media in the dataset.

        :returns : largest media element in the dataset.
        """
        return self.first_file  # ToDo

    def get_media_output_type(self):
        """
        Method to specify type of media output produced by the reader.

        returns: type of media output which is produced by this reader.
        """
        return ro.FILE_LIST

    def __len__(self):
        """
        Method to get dataset length.

        returns: length of dataset in units of batch_size.
        """
        return self.num_batches_slice  # ToDo

    def __iter__(self):
        """
        Method to initialize iterator.

        """
        return self

    def __next__(self):
        """
        Method to get one batch of dataset ouput from iterator.

        """
        vid_name_list = self.ext_queue.get()
        assert len(
            vid_name_list) == self.batch_size, "wrong number of media files received"

        start = 0
        end = self.batch_size
        vid_list = vid_name_list[start:end]

        return [vid_list]
