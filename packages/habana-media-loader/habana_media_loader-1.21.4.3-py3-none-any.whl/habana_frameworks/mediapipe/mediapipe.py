# main mediapipe file : master controller
from habana_frameworks.mediapipe.backend.utils import get_media_fw_type
from habana_frameworks.mediapipe.backend.utils import getDeviceIdFromDeviceName
# from habana_frameworks.mediapipe.backend.graph import graph_executor, graph_processor
from habana_frameworks.mediapipe.operators.media_nodes import media_layout as cl
from habana_frameworks.mediapipe.backend.iterator import HPUGenericIterator as iter
from habana_frameworks.mediapipe.media_types import layout as lt
from habana_frameworks.mediapipe.media_types import mediaDeviceType as mdt
from habana_frameworks.mediapipe.backend.proxy_impl import set_c_proxy
from habana_frameworks.mediapipe.backend.logger import printf
from habana_frameworks.mediapipe.backend.tracing import media_tracer, tracer
import media_pipe_types as mpt
import media_pipe_proxy as mppy  # NOQA
from abc import ABC, abstractmethod
import numpy as np
import time


class MediaPipe(ABC):
    """
    Abstract class representing media pipe.

    """
    framework_type = None
    framework_proxy = None

    @abstractmethod
    def __init__(self, device=None, prefetch_depth=2, batch_size=1, num_threads=1, pipe_name=None):
        """
        Constructor method.

        :params device: media device to run mediapipe on. <hpu/hpu:0>
        :params prefetch_depth: mediapipe prefetch count. <1/2/3>
        :params batch_size: mediapipe output batch size.
        :params channel: mediapipe output channel.
        :params height: mediapipe output height.
        :params width: mediapipe output width.
        :params pipe_name: mediapipe user defined name.
        :params layout: mediapipe output layout. <lt.NHWC/lt.WHCN>

        """
        self._pipeline_init = False
        self._gp = None
        self._gexe = None
        self._graph_compiled = False
        self._batch_size = batch_size
        self._queue_depth = prefetch_depth
        if not isinstance(num_threads, int):
            raise ValueError("num_threads must be integer")
        self._num_threads = num_threads
        self._device = device
        self._pipename = pipe_name
        if (device == mdt.CPU or device == mdt.MIXED):
            from habana_frameworks.mediapipe.backend.graph import graph_executor, graph_processor
            self.__graph_executor = graph_executor
            self.__graph_processor = graph_processor
            self._device_type, self._device_id = device, 0
            self.__execute = self.__run__
        elif (device == mdt.LEGACY):
            from habana_frameworks.mediapipe.backend.graph_legacy import graph_executor, graph_processor
            self.__graph_executor = graph_executor
            self.__graph_processor = graph_processor
            self._device_type, self._device_id = device, 0
            self.__execute = self.__run_legacy__
        else:
            print(" Warning!!!!!! : Unsupported device please use legacy/cpu/mixed")
            print("Falling back to legacy")
            device = "legacy"
            from habana_frameworks.mediapipe.backend.graph_legacy import graph_executor, graph_processor
            self.__graph_executor = graph_executor
            self.__graph_processor = graph_processor
            self._device_type, self._device_id = device, 0
            self.__execute = self.__run_legacy__

        self._fw_type = mppy.fwType.SYNAPSE_FW
        self._proxy = 0x0  # this must be 0 and not None
        self._python_proxy = None
        # INFO: as of now only 1 recipe is supported
        self._iter_repeat_count = 1
        self.__tracer = media_tracer()
        print("MediaPipe device {} device_type {} device_id {} pipe_name {}".format(
            device, self._device_type, self._device_id, pipe_name))
        printf("{}  created.".format(self._pipename))

    def close(self):
        """
        Destructor method.

        """
        if (self._gexe is not None):
            self._gexe.close()
            self._gexe = None
        if (self._gp is not None):
            self._gp.close()
            self._gp = None

    def __del__(self):
        """
        Destructor method.

        """
        self.close()

    @abstractmethod
    def definegraph(self):
        """
        Abstract method defining the media graph.
        Derived class defines the control flow of the media nodes in this method.

        """
        pass

    def setOutputShape(self, batch_size, channel, height, width, layout=lt.NHWC):
        """
        Setter method to set media pipe output shape.

        :params channel: mediapipe output channel.
        :params height: mediapipe output height.
        :params width: mediapipe output width.
        :params layout: mediapipe output layout. <lt.NHWC/lt.WHCN>
        """
        self._img_cwhb_ = np.array(
            [channel, width, height, batch_size], dtype=np.uint32)
        self._img_out_ = self._img_cwhb_[cl.idx[cl.enum[layout]]]

    def getDeviceId(self):
        """
        Getter method to get media pipe device id

        :returns : mediapipe device id.
        """
        return self._device_id

    def getBatchSize(self):
        """
        Getter method to get media pipe batch_size

        :returns : mediapipe batch_size.
        """
        return self._batch_size

    def build(self):
        """
        Method to build media pipe nodes and generate the recipe.

        """
        if (self._graph_compiled):
            # graph already built
            return
        self._graph_compiled = True
        # call user defined graph function
        output_tensors = self.definegraph()
        if isinstance(output_tensors, tuple):
            output_tensors = list(output_tensors)
        elif not isinstance(output_tensors, list):
            output_tensors = [output_tensors]
        self._gp = self.__graph_processor(
            self._device_type, output_tensors, self._fw_type, self._proxy)
        self._gp.create_opnodes(self._batch_size,
                                self._queue_depth,
                                self._num_threads)
        self._gp.segment_graph()
        self._gp.process_and_validate_graph(self._batch_size,
                                            self._queue_depth,
                                            self._num_threads)
        self._recipe_ = self._gp.compile()
        self._gp.process_recipe()

    def set_proxy(self, fw_type, proxy):
        """
        Setter method to set media proxy.

        :params fw_type: framework to be used by media. <SYNAPSE_FW/TF_FW/PYTHON_FW/PYT_FW>
        :params proxy : c++ proxy address.
        """
        if MediaPipe.framework_type is None:
            MediaPipe.framework_type = get_media_fw_type(fw_type)
            if not isinstance(MediaPipe.framework_type, mppy.fwType):
                raise RuntimeError(" Invalid proxy type.")
            self._fw_type = MediaPipe.framework_type
            MediaPipe.framework_proxy = proxy
            if (MediaPipe.framework_type == mppy.fwType.PYTHON_FW):
                MediaPipe.framework_c_proxy = set_c_proxy(
                    MediaPipe.framework_proxy)
                self._proxy = MediaPipe.framework_c_proxy
                self._python_proxy = MediaPipe.framework_proxy
            elif (MediaPipe.framework_type == mppy.fwType.PYTHON_PYT_FW):
                self._proxy = MediaPipe.framework_proxy[0]
                self._python_proxy = MediaPipe.framework_proxy[1]
            else:
                self._proxy = MediaPipe.framework_proxy
        else:
            fw_type = get_media_fw_type(fw_type)
            if fw_type != MediaPipe.framework_type:
                raise RuntimeError("A different framework already initialized")
            self._fw_type = MediaPipe.framework_type
            if (MediaPipe.framework_type == mppy.fwType.PYTHON_FW):
                self._proxy = MediaPipe.framework_c_proxy
                self._python_proxy = MediaPipe.framework_proxy
            elif (MediaPipe.framework_type == mppy.fwType.PYTHON_PYT_FW):
                self._proxy = MediaPipe.framework_proxy[0]
                self._python_proxy = MediaPipe.framework_proxy[1]
            else:
                self._proxy = MediaPipe.framework_proxy

    def set_repeat_count(self, count):
        """
        Setter method to set mediapipe iteration repeat count.

        :params count: number of time media pipe iteration to be repeated.
        """
        self._iter_repeat_count = count

    def iter_init(self):
        """
        Method to initialize mediapipe iterator.

        """
        t = tracer("iter_init")
        printf("{} iter init ".format(self._pipename))
        if (self._graph_compiled != True):
            raise RuntimeError("Pipe build() not called!!!!")
        if (self._pipeline_init == False):
            self._gexe = self.__graph_executor(self._gp,
                                               self._queue_depth,
                                               self._batch_size,
                                               self._fw_type,
                                               self._proxy,
                                               self._python_proxy)
            self._gexe.acquire_device(self._device_type)
            self._gexe.initialize_memory()
            self._gexe.start_worker()
            self._pipeline_init = True
        else:
            self._gexe.flush_pipeline()
        self._gexe.initialize_iter_pipeline(self._iter_repeat_count)

    def del_iter(self):
        """
        Method to close media iteration and release device.

        """
        if self._pipeline_init:
            t = tracer("del_iter")
            printf("{} iter del".format(self._pipename))
            self._gexe.flush_pipeline()
            self._gexe.stop_worker()
            self._gexe.free_memory()
            self._gexe.release_device()
            self._gexe.close()
            self._gexe = None
            self._pipeline_init = False

    def __run_legacy__(self):
        t = tracer("mediapipe_run_legacy")
        return self._gexe.run()

    def __run__(self):
        t = tracer("mediapipe_run_cpu")
        return self._gexe.get_output()

    def run(self):
        """
        Method to run mediapipe iterator over one batch of dataset.

        :returns : one batch of media graph processed output.
        :raises StopIteration: when complete dataset iteration and number repeat counnt is done.
        """
        return self.__execute()

    def as_iterator(self):
        """
        Method to get mediapipe iteratable object.

        :returns : mediapipe iteratable object.
        """
        if self._fw_type == mppy.fwType.SYNAPSE_FW:
            return iter(mediapipe=self)
        else:
            print("Pipe not iterable, use iterator")
            return None

    def get_batch_count(self):
        """
        Getter method to get media pipe number of batches in dataset.

        :returns : mediapipe number of batches presnet in dataset.
        """
        return self._gp.get_num_batches()

    def push_input(self, idx, np_array):
        self._gexe.push_input(idx, np_array)
