from habana_frameworks.mediapipe.backend.operator_specs import schema
from habana_frameworks.mediapipe.operators.reader_nodes.coco_reader import coco_reader
from habana_frameworks.mediapipe.operators.reader_nodes.read_image_from_dir import read_image_from_dir
from habana_frameworks.mediapipe.operators.reader_nodes.read_video_from_dir import read_video_from_dir
from habana_frameworks.mediapipe.operators.reader_nodes.read_video_from_dir_gen import read_video_from_dir_gen
from habana_frameworks.mediapipe.operators.reader_nodes.read_media_from_ext import read_media_from_ext
from habana_frameworks.mediapipe.operators.reader_nodes.read_image_from_dir_buf import read_image_from_dir_buffer
from habana_frameworks.mediapipe.operators.reader_nodes.reader_nodes import media_ext_reader_op
from habana_frameworks.mediapipe.operators.reader_nodes.read_numpy_from_dir import read_numpy_from_dir
from habana_frameworks.mediapipe.operators.reader_nodes.reader_node_params import *
from habana_frameworks.mediapipe.operators.reader_nodes.reader_cpu_ops_node import reader_cpu_ops_node

import media_pipe_params as mpp  # NOQA
import media_pipe_nodes as mpn  # NOQA


# add operators to the list of supported ops
# schema.add_operator(oprator_name,guid, min_inputs,max_inputs,num_outputs,params_of_operator)

schema.add_operator_cpu("ReadVideoDatasetFromDir", None, 0, 0, generic_in0_keys,
                        3, read_video_from_dir_params, None, read_video_from_dir, dt.NDT)

schema.add_operator_cpu("ReadVideoDatasetFromDirGen", None, 0, 0, generic_in0_keys,
                        3, read_video_from_dir_gen_params, None, read_video_from_dir_gen, dt.NDT)

schema.add_operator_cpu("ReadMediaDatasetFromExt", None, 0, 0, generic_in0_keys,
                        1, read_media_from_ext_params, None, read_media_from_ext, dt.NDT)

schema.add_operator_cpu("ReadImageDatasetFromDirBuffer", None, 0, 0, generic_in0_keys,
                        2, read_image_from_dir_params, None, read_image_from_dir_buffer, dt.NDT)

schema.add_operator_cpu(
    "MediaExtReaderOp",
    "py_reader",
    0,
    0,
    generic_in0_keys,
    1,
    media_ext_reader_op_params,
    mpn.PyReaderParams_t,
    media_ext_reader_op,
    dt.NDT)

schema.add_operator_cpu(
    "ReadNumpyDatasetFromDir",
    "numpy_reader",
    0,
    0,
    generic_in0_keys,
    2,
    read_numpy_from_dir_params,
    mpn.NumpyReaderParams_t,
    read_numpy_from_dir,
    dt.NDT)

schema.add_operator_cpu(
    "ReadImageDatasetFromDir",
    "file_reader",
    0,
    0,
    generic_in0_keys,
    2,
    read_image_from_dir_params,
    mpn.FileReaderParams_t,
    read_image_from_dir,
    dt.NDT)

schema.add_operator_cpu("CocoReader", "coco_reader", 0, 0, generic_in0_keys, 7,
                        coco_reader_params, mpn.CocoParams_t, coco_reader, dt.NDT)
