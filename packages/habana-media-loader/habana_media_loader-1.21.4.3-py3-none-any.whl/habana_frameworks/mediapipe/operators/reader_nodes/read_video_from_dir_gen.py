from habana_frameworks.mediapipe.backend.nodes import opnode_tensor_info
from habana_frameworks.mediapipe.operators.media_nodes import MediaReaderNode
from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.media_types import readerOutType as ro
from habana_frameworks.mediapipe.media_types import clipSampler as cs
from habana_frameworks.mediapipe.operators.reader_nodes.read_image_from_dir import gen_class_list, gen_image_list, gen_label_list
from habana_frameworks.mediapipe.operators.reader_nodes.video_reader_utils import RandomSampler, UniformSampler, ContiguousSampler, get_num_frame
from media_pipe_randomizer import DatasetShuffler
from habana_frameworks.mediapipe.media_types import lastBatchStrategy as lbs
from media_pipe_nodes import LastBatchStrategy_t as lbs_t

import numpy as np
import time
from typing import List, Tuple
import warnings
import bisect

# If g_extra_frame_stride is True, last Frame in clip will require extra
# frames needed by stride as well
g_extra_frame_stride = True


def unfold_stride(idx_array: np.ndarray, size: int, step: int, dilation: int = 1) -> np.ndarray:
    """
    Returns all consecutive windows of `size` elements (F), with `step` between windows. The distance between each element
    in a window (stride) is given by `dilation`.
    """
    if idx_array.ndim != 1:
        raise ValueError(
            f"expected 1 dimension instead of {idx_array.ndim}")

    o_stride = idx_array.strides[0]
    numel = idx_array.size
    new_stride = (step * o_stride, dilation * o_stride)
    if g_extra_frame_stride:
        new_size = ((numel - (dilation * size)) // step + 1, size)
    else:
        new_size = ((numel - (dilation * (size - 1) + 1)) // step + 1, size)

    if new_size[0] < 1:
        new_size = (0, size)

    return np.lib.stride_tricks.as_strided(idx_array, new_size, new_stride, writeable=False)


def compute_clips_for_video_stride(
        num_frame_vid: np.uint32,
        clip_length: int,
        step: int,
        start_index: int,
        stride: int) -> np.ndarray:
    """
    Compute all consecutive sequences of clips of clip_length from num_frame_vid.
    """

    idxs_all = np.arange(start_index, num_frame_vid, dtype=np.int32)
    idxs = unfold_stride(idxs_all, clip_length, step, stride)
    if idxs.size == 0:
        warnings.warn(
            "video reader: There aren't enough frames in the current video to get a clip for the given clip length (frames_per_clip)."
            "The video (and potentially others) will be skipped.")
    return idxs


def get_clip_len(
        num_frame_vid: np.uint32,
        clip_length: int,
        step: int,
        start_index: int,
        stride: int) -> int:
    """
    Compute number of clips of clip_length from num_frame_vid.
    """
    numel = num_frame_vid - start_index
    dilation = stride
    size = clip_length

    if g_extra_frame_stride:
        new_size = (numel - (dilation * size)) // step + 1
    else:
        new_size = (numel - (dilation * (size - 1) + 1)) // step + 1
    if new_size < 1:
        new_size = 0
    new_size = int(new_size)

    if new_size == 0:
        warnings.warn(
            "video reader: There aren't enough frames in the current video to get a clip for the given clip length (frames_per_clip)."
            "The video (and potentially others) will be skipped.")
    return new_size


class VideoClipsStride:
    def __init__(
            self,
            frames: int,
            step: int,
            vid_list: np.ndarray,
            start_frame_index: int,
            stride: int) -> None:
        """
        Given a list of video files 'vid_list', compute all consecutive subvideos of size
        'frames_per_clip', where the distance between each subvideo in the
        same video is defined by `step_between_clips`.

        frames_per_clip: size of a clip in number of frames
        step_between_clips: step (in frames) between each clip
        start_frame_index: start frame index for clips
        stride: stride of clips
        """

        self.frames_per_clip = frames
        self.step_between_clips = step
        self.stride = stride
        self.start_frame_index = start_frame_index

        # start_time = time.time()
        print("compute num_frame, fps ...")
        num_frame, _avg_fps_ = get_num_frame(vid_list)

        # total_time = time.time() - start_time
        print("compute num_frame, fps Done")
        # print("compute num_frame, fps Done, time {}s".format(total_time))

        assert len(vid_list) == len(num_frame), "wrong num frame"

        self.vid_list_num_frame_np = np.array(num_frame, dtype=np.uint32)

        self.compute_clips_stride()
        # print("compute_clips Done")

    def compute_clips_stride(self):
        """
        Compute Reference Clip of max frames and list of clip lengths from self.vid_list_num_frame_np.

        """

        self.vid_clips_list = []
        max_frame = np.max(self.vid_list_num_frame_np)
        self.ref_vid_clip = compute_clips_for_video_stride(
            max_frame,
            self.frames_per_clip,
            self.step_between_clips,
            self.start_frame_index,
            self.stride)

        for num_frame_vid in self.vid_list_num_frame_np:
            # clips = compute_clips_for_video_stride(num_frame_vid, self.frames_per_clip, self.step_between_clips, self.start_frame_index, self.stride)
            # self.vid_clips_list.append(len(clips))
            clips_len = get_clip_len(num_frame_vid, self.frames_per_clip,
                                     self.step_between_clips, self.start_frame_index, self.stride)
            self.vid_clips_list.append(clips_len)

        clip_lengths = np.array(self.vid_clips_list, dtype=np.uint32)
        self.vid_clips_list_cumulative_sizes = clip_lengths.cumsum(0).tolist()

        # check Clip list is List[int]
        for clip in self.vid_clips_list:
            assert isinstance(clip, int), "expected int clip length"

    def get_video_clip_list(self) -> Tuple[np.ndarray, List[int]]:
        # return Reference Clip of max frames, list of clip lengths
        return self.ref_vid_clip, self.vid_clips_list

    def get_clip_location(self, idx: int) -> Tuple[int, int]:
        """
        Converts a flattened representation of the indices into a video_idx, clip_idx
        representation.
        """
        # assert idx <= (self.vid_clips_list_cumulative_sizes[-1] - 1), "Error: Got invalid clip index {} max idx {}".format(
        #    idx, (self.vid_clips_list_cumulative_sizes[-1] - 1))

        video_idx = bisect.bisect_right(
            self.vid_clips_list_cumulative_sizes, idx)
        if video_idx == 0:
            clip_idx = idx
        else:
            clip_idx = idx - \
                self.vid_clips_list_cumulative_sizes[video_idx - 1]
        return video_idx, clip_idx


class read_video_from_dir_gen(MediaReaderNode):
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

        self.batch_size = 1
        self.dir = params['dir']
        self.seed = params['seed']
        self.format = params['format']
        self.meta_dtype = params["label_dtype"]
        self.num_slices = params['num_slices']
        self.slice_index = params['slice_index']
        self.class_list = params['class_list']
        self.vid_list = params['file_list']
        self.file_classes = params['file_classes']

        self.last_batch_strategy = params['last_batch_strategy']
        self.start_frame_index = params['start_frame_index']
        self.frames_per_clip = params['frames_per_clip']
        self.clips_per_video = params['clips_per_video']
        self.stride = params['stride']
        self.frames_between_clips = params['step_between_clips']

        self.sampler = params['sampler']
        self.slice_once = params['slice_once']
        self.is_modulo_slice = params['is_modulo_slice']

        if (self.seed is None):
            # seed only needed in case of RANDOM_SAMPLER or CONTIGUOUS_RANDOM_SAMPLER,
            # not needed for UNIFORM_SAMPLER or CONTIGUOUS_SAMPLER
            if (self.num_slices > 1):
                if (self.sampler == cs.RANDOM_SAMPLER) or (
                        self.sampler == cs.CONTIGUOUS_RANDOM_SAMPLER):
                    raise ValueError("seed not set")
            else:
                if (self.sampler == cs.RANDOM_SAMPLER) or (
                        self.sampler == cs.CONTIGUOUS_RANDOM_SAMPLER):
                    self.seed = int(time.time_ns() % (2**31 - 1))

        if ((self.class_list != [] and self.vid_list == []) or (
                self.vid_list != [] and self.class_list == [])):
            raise ValueError("Both class_list and file_list must be shared")
        elif ((self.vid_list != []) and (self.file_classes != []) and (len(self.vid_list) != len(self.file_classes))):
            raise ValueError(
                "Both file_list and file_classes must be of same length")
        elif (self.vid_list == [] and self.file_classes != []):
            raise ValueError(
                "file_classes must be shared only if file_list is shared")
        elif (self.vid_list == [] and self.dir == ""):
            raise ValueError("Atleast file_list or dir must be shared")
        elif (self.vid_list != [] and self.dir != ""):
            raise ValueError("Only file_list or dir must be shared")

        # self.rng = np.random.default_rng(self.seed)
        print("Finding classes ...", end=" ")
        self.class_list = gen_class_list(self.dir, self.class_list)
        print("Done!")
        print("Finding videos ...", end=" ")
        self.vid_list = gen_image_list(self.dir, self.format, self.vid_list)
        print("Done!")
        print("Generating labels ...", end=" ")
        self.lbl_list = gen_label_list(
            self.vid_list, self.class_list, self.meta_dtype, self.file_classes)
        print("Done!")

        num_imgs = len(self.vid_list)
        print("Total media files/labels {} classes {}".format(num_imgs,
              len(self.class_list)))
        assert len(self.vid_list) == len(
            self.lbl_list), "wrong num label/video"

        self.iter_loc = 0
        if num_imgs == 0:
            raise ValueError("video list is empty")
        self.num_batches_slice = int(num_imgs / self.batch_size)
        if (self.num_slices < 1):
            raise ValueError("num slice cannot be less then 1")
        if (self.slice_index >= self.num_slices):
            raise ValueError("slice_index cannot be >= num_slices")

        self.first_file = self.vid_list[0]  # ToDo: Update largest file

        self.resample_dtype = dt.INT32

        assert self.clips_per_video > 0, "clips_per_video > 0 expected"
        assert self.frames_per_clip > 0, "frames_per_clip > 0 expected"
        assert self.stride > 0, "stride > 0 expected"
        assert self.frames_between_clips > 0, "step_between_clips > 0 expected"
        assert self.start_frame_index >= 0, "start_frame_index >= 0 expected"

        print(
            "video reader sampler: {} clips_per_video: {} frames_per_clip: {} stride: {} step_between_clips: {} start_frame_index: {}".format(
                self.sampler,
                self.clips_per_video,
                self.frames_per_clip,
                self.stride,
                self.frames_between_clips,
                self.start_frame_index))  # self.last_batch_strategy
        self.batch_size = fw_params.batch_size

        self.video_clips_stride = VideoClipsStride(
            self.frames_per_clip,
            self.frames_between_clips,
            self.vid_list,
            self.start_frame_index,
            self.stride)

        self.ref_vid_clip, self.video_clips_list = self.video_clips_stride.get_video_clip_list()
        self.shuffle = False
        if self.sampler == cs.RANDOM_SAMPLER:
            assert self.seed is not None, "seed not set for RANDOM_SAMPLER"
            self.sampler_inst = RandomSampler(
                self.video_clips_list, self.clips_per_video, self.seed)
            if self.last_batch_strategy == lbs.FILL:
                # ToDo: check if can be enabled
                raise ValueError(
                    "RANDOM_SAMPLER not supported for last_batch_strategy FILL")
        elif self.sampler == cs.UNIFORM_SAMPLER:
            self.sampler_inst = UniformSampler(
                self.video_clips_list, self.clips_per_video)
        elif self.sampler == cs.CONTIGUOUS_SAMPLER:
            self.sampler_inst = ContiguousSampler(
                self.video_clips_list, self.clips_per_video)
        elif self.sampler == cs.CONTIGUOUS_RANDOM_SAMPLER:
            self.sampler_inst = ContiguousSampler(
                self.video_clips_list, self.clips_per_video)
            self.shuffle = True
            assert self.seed is not None, "seed not set for ContiguousSampler"
        else:
            raise ValueError("invalid Sampler")

        sampler_clip_length = self.sampler_inst.get_length()

        self.last_batch_strategy_t = None

        if self.last_batch_strategy == lbs.CYCLIC:
            self.last_batch_strategy_t = lbs_t.LBS_CYCLIC
        elif self.last_batch_strategy == lbs.DROP:
            self.last_batch_strategy_t = lbs_t.LBS_DROP
        elif self.last_batch_strategy == lbs.PAD:
            self.last_batch_strategy_t = lbs_t.LBS_PAD
        elif self.last_batch_strategy == lbs.FILL:
            self.last_batch_strategy_t = lbs_t.LBS_FILL
        elif self.last_batch_strategy == lbs.PARTIAL:
            raise ValueError("LastBatchStrategy PARTIAL not supported")  # ToDo
        elif self.last_batch_strategy == lbs.NONE:
            raise ValueError("LastBatchStrategy NONE not supported")
        else:
            raise ValueError("Unsupported LastBatchStrategy")

        print("seed {} num_slices {} slice_index {}".format(
            self.seed, self.num_slices, self.slice_index))

        # Update seed for shuffler
        seed_shuffler = self.seed
        if (self.seed is None):
            seed_shuffler = -1

        self.shuffler = DatasetShuffler(self.shuffle,           # shuffle
                                        self.slice_once,        # shardOnce
                                        self.last_batch_strategy_t,
                                        self.is_modulo_slice,   # isModSlice
                                        seed_shuffler,              # seed
                                        self.num_slices,
                                        self.slice_index,
                                        self.batch_size,
                                        sampler_clip_length
                                        )
        self.num_batches_slice = self.shuffler.GetNumIterableEle() // self.batch_size

        print("num video: {} num clips: {} batch size: {} sliced, rounded clips: {} num batches: {}".format(len(
            self.vid_list), sampler_clip_length, self.batch_size, self.shuffler.GetNumIterableEle(), self.num_batches_slice))

    def gen_output_info(self):
        """
        Method to generate output type information.

        :returns : output tensor information of type "opnode_tensor_info".
        """

        # out_info_ip = super().gen_output_info()
        out_info = []
        o = opnode_tensor_info(dt.NDT,
                               np.array([self.batch_size],
                                        dtype=np.uint32),
                               "")
        out_info.append(o)
        o = opnode_tensor_info(self.meta_dtype,
                               np.array([self.batch_size],
                                        dtype=np.uint32),
                               "")
        out_info.append(o)

        self.resample_shape = [self.frames_per_clip, self.batch_size]
        self.resample_shape_np = self.resample_shape[::-1]
        o = opnode_tensor_info(self.resample_dtype, np.array(
            self.resample_shape, dtype=np.uint32), "")
        out_info.append(o)

        return out_info

    def get_largest_file(self):
        """
        Method to get largest media in the dataset.

        :returns : largest media element in the dataset.
        """
        return self.first_file

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
        return self.num_batches_slice

    def __iter__(self):
        """
        Method to initialize iterator.

        """

        print("Iter ...", end=" ")
        clip_dataset_iter = self.sampler_inst.get_iter_array()
        idxs = self.shuffler.GenIdxList()

        self.vid_list_slice_iter = clip_dataset_iter[idxs]
        print("Done!")

        self.iter_loc = 0
        return self

    def __next__(self):
        """
        Method to get one batch of dataset ouput from iterator.

        """

        if self.iter_loc > (len(self.vid_list_slice_iter) - 1):
            raise StopIteration

        # resample_idx are frame indexes to be used for each clip in vid_list
        resample_idx = np.zeros(self.resample_shape_np,
                                dtype=self.resample_dtype)

        start = self.iter_loc
        end = self.iter_loc + self.batch_size
        self.iter_loc += self.batch_size

        clip_list = self.vid_list_slice_iter[start:end]
        lbl_list = np.zeros([self.batch_size], dtype=self.meta_dtype)
        vid_list = []

        for idx, clip_idx_list in enumerate(clip_list):
            video_index, clip_index = self.video_clips_stride.get_clip_location(
                clip_idx_list)
            video_path = self.vid_list[video_index]
            vid_list.append(video_path)
            lbl_list[idx] = self.lbl_list[video_index]

            # Get resample index from Reference Clip
            # self.video_clips_list[video_index][clip_index]
            clip_resample_idx = self.ref_vid_clip[clip_index]
            # print("reader next for {} clip idx {} video {} clip {} path {} lbl {} resampling {}".format(
            # idx, clip_idx_list, video_index, clip_index, video_path, lbl_list[idx],
            # clip_resample_idx))

            clip_resample_idx_np = np.array(
                clip_resample_idx, dtype=self.resample_dtype)

            resample_idx[idx] = clip_resample_idx_np

        return vid_list, lbl_list, resample_idx
