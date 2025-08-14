from habana_frameworks.mediapipe.backend.nodes import opnode_tensor_info
from habana_frameworks.mediapipe.operators.media_nodes import MediaReaderNode
from habana_frameworks.mediapipe.operators.reader_nodes.read_image_from_dir import gen_class_list, gen_image_list, gen_label_list
from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.media_types import readerOutType as ro
from habana_frameworks.mediapipe.media_types import clipSampler as cs
from habana_frameworks.mediapipe.operators.reader_nodes.reader_utils import dataset_shuffler
from habana_frameworks.mediapipe.operators.reader_nodes.video_reader_utils import RandomSampler, UniformSampler, get_num_frame

import numpy as np
import time
import math
from typing import Union, List, Tuple
import warnings
import bisect


def unfold(idx_array: np.ndarray, size: int, step: int, dilation: int = 1) -> np.ndarray:
    """
    Returns all consecutive windows of `size` elements, with `step` between windows. The distance between each element
    in a window is given by `dilation`.
    """
    if idx_array.ndim != 1:
        raise ValueError(
            f"expected 1 dimension instead of {idx_array.ndim}")

    o_stride = idx_array.strides[0]
    numel = idx_array.size
    new_stride = (step * o_stride, dilation * o_stride)
    new_size = ((numel - (dilation * (size - 1) + 1)) // step + 1, size)
    if new_size[0] < 1:
        new_size = (0, size)

    return np.lib.stride_tricks.as_strided(idx_array, new_size, new_stride, writeable=False)


def compute_clips_for_video_fps(
        num_frame_vid: int,
        clip_length: int,
        step: int,
        fps_video: float,
        target_frame_rate: int) -> np.ndarray:
    """
    Compute all consecutive sequences of clips of clip_length from num_frame_vid.
    """
    if target_frame_rate == 0:
        target_frame_rate = fps_video
    total_frames = num_frame_vid * (target_frame_rate / fps_video)
    _idxs = _resample_video_idx(
        int(math.floor(total_frames)), fps_video, target_frame_rate)

    if isinstance(_idxs, slice):
        idxs_temp = np.arange(num_frame_vid, dtype=np.int32)
        idxs_temp = idxs_temp[_idxs]
        idxs = unfold(idxs_temp, clip_length, step)

    else:
        idxs = unfold(_idxs, clip_length, step)

    if idxs.size == 0:
        warnings.warn(
            "video reader: There aren't enough frames in the current video to get a clip for the given clip length (frames_per_clip)."
            "The video (and potentially others) will be skipped.")

    return idxs


def _resample_video_idx(num_frame_vid: int, original_fps: float,
                        new_fps: int) -> Union[slice, np.ndarray]:
    """
    calculate resample index for video with num_frame_vid frames at original_fps to new_fps
    """
    step = original_fps / new_fps

    if step.is_integer():
        # optimization: if step is integer, don't need to perform
        # advanced indexing
        step = int(step)
        return slice(None, None, step)

    idxs = np.arange(num_frame_vid, dtype=np.float32) * step
    idxs = np.floor(idxs).astype(np.int32)
    return idxs


class VideoClipsFps:
    def __init__(self, frames: int, step: int, frame_rate: int, vid_list: np.ndarray) -> None:
        """
        Given a list of video files 'vid_list', compute all consecutive subvideos of size
        'frames_per_clip', where the distance between each subvideo in the
        same video is defined by `step_between_clips`.

        frames_per_clip: size of a clip in number of frames
        step_between_clips: step between each clip
        target_frame_rate: If specified(i.e. not 0), resample the videos so that they have the same `target_frame_rate`.
        If 0, resampling based on fps is not done.
        """

        self.frames_per_clip = frames
        self.step_between_clips = step
        self.target_frame_rate = frame_rate

        # start_time = time.time()
        print("compute num_frame, fps ...")
        num_frame, avg_frame_rate = get_num_frame(vid_list)
        # total_time = time.time() - start_time
        print("compute num_frame, fps Done")
        # print("compute num_frame, fps Done, time {}s".format(total_time))

        assert len(vid_list) == len(num_frame), "wrong num frame"
        assert len(vid_list) == len(avg_frame_rate), "wrong frame rate"

        self.vid_list_num_frame_np = np.array(num_frame, dtype=np.uint32)
        self.vid_list_avg_frame_rate_np = np.array(
            avg_frame_rate, dtype=np.float64)

        max_frame_rate = np.max(self.vid_list_avg_frame_rate_np)

        print("max frame rate {} in video files".format(max_frame_rate))

        self.compute_clips(self.frames_per_clip,
                           self.step_between_clips, self.target_frame_rate)
        # print("compute_clips Done")

    def compute_clips(self, num_frames: int, step: int, target_frame_rate: int):
        """
        Compute all consecutive sequences of clips from self.vid_list_num_frame_np.

        Args:
            num_frames (int): number of frames for the clip
            step (int): distance between two clips
            target_frame_rate (int): frame rate at which all video are to be resampled.
                                     If 0, frame resampling based on fps is not done.
        """

        self.vid_clips_list = []

        for num_frame_vid, fps_vid in zip(
                self.vid_list_num_frame_np, self.vid_list_avg_frame_rate_np):
            clips = compute_clips_for_video_fps(
                num_frame_vid, num_frames, step, fps_vid, target_frame_rate)
            self.vid_clips_list.append(clips)

        clip_lengths = np.array([len(v)
                                for v in self.vid_clips_list], dtype=np.uint32)
        self.vid_clips_list_cumulative_sizes = clip_lengths.cumsum(0).tolist()

        # check Clip list is List[np.ndarray]
        for clip in self.vid_clips_list:
            assert isinstance(
                clip, np.ndarray), "expected clip instance of np.ndarray"

    def get_video_clip_list(self) -> List[np.ndarray]:
        return self.vid_clips_list

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


class read_video_from_dir(MediaReaderNode):
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
        self.drop_remainder = params['drop_remainder']
        self.pad_remainder = params['pad_remainder']
        self.format = params['format']
        self.meta_dtype = params["label_dtype"]
        self.num_slices = params['num_slices']
        self.slice_index = params['slice_index']
        self.class_list = params['class_list']
        self.vid_list = params['file_list']
        self.file_classes = params['file_classes']

        # fixed_clip_mode output clips: start_frame_index to frames_per_clip
        self.fixed_clip_mode = params['fixed_clip_mode']
        self.shuffle = params['shuffle']  # used only for fixed_clip_mode
        # used only for fixed_clip_mode
        self.start_frame_index = params['start_frame_index']

        # clip_length_in_frames
        self.frames_per_clip = params['frames_per_clip']
        self.clips_per_video = params['clips_per_video']
        # if target_frame_rate set to 0, frame resampling based on fps is not done
        self.target_frame_rate = params['target_frame_rate']
        self.step_between_clips = params['step_between_clips']

        self.sampler = params['sampler']

        # self.max_file = params['max_file']
        # self.file_sizes = params['file_sizes']

        if (self.seed is None):
            if (self.num_slices > 1):
                if (((self.fixed_clip_mode) and (self.shuffle)) or (
                        (self.fixed_clip_mode == False) and (self.sampler == cs.RANDOM_SAMPLER))):
                    raise ValueError("seed not set")
            else:
                if (((self.fixed_clip_mode) and (self.shuffle)) or (
                        (self.fixed_clip_mode == False) and (self.sampler == cs.RANDOM_SAMPLER))):
                    # max supported seed value is 32bit so modulo
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
        print("seed {} num_slices {} slice_index {}".format(
            self.seed, self.num_slices, self.slice_index))

        self.first_file = self.vid_list[0]  # ToDo: Update largest file

        self.resample_dtype = dt.INT32

        self.is_modulo_slice = True

        assert self.frames_per_clip > 0, "frames_per_clip > 0 expected"

        if self.fixed_clip_mode:
            """
            Each video is used to generate a clip from 'start_frame_index' of length 'frames_per_clip'
            """
            assert self.start_frame_index >= 0, "start_frame_index >= 0 expected"

            print("video reader: Fixed Clip mode, start_frame_index: {} frames_per_clip: {} shuffle: {}".format(
                self.start_frame_index, self.frames_per_clip, self.shuffle))
        else:

            assert self.clips_per_video > 0, "clips_per_video > 0 expected"
            assert self.step_between_clips > 0, "step_between_clips > 0 expected"

            if self.sampler == cs.RANDOM_SAMPLER:
                print(
                    "video reader sampler: Random frames_per_clip: {} target_frame_rate: {}".format(
                        self.frames_per_clip,
                        self.target_frame_rate))
            elif self.sampler == cs.UNIFORM_SAMPLER:
                print(
                    "video reader sampler: Uniform frames_per_clip: {} target_frame_rate: {}".format(
                        self.frames_per_clip,
                        self.target_frame_rate))
            else:
                raise ValueError("unsupported sampler ", self.sampler)

        self.batch_size = fw_params.batch_size

        if not self.fixed_clip_mode:

            self.video_clips = VideoClipsFps(
                self.frames_per_clip,
                self.step_between_clips,
                self.target_frame_rate,
                self.vid_list)

            self.video_clips_list = self.video_clips.get_video_clip_list()
            if self.sampler == cs.RANDOM_SAMPLER:
                assert self.seed is not None, "seed not set"
                self.sampler_inst = RandomSampler(
                    self.video_clips_list, self.clips_per_video, self.seed)
            else:
                self.sampler_inst = UniformSampler(
                    self.video_clips_list, self.clips_per_video)

            sampler_clip_length = self.sampler_inst.get_length()

            self.shuffler = dataset_shuffler(None,  # shuffle, shuffle_across_dataset is False, so seed not set for dataset_shuffler
                                             False,  # shuffle
                                             self.slice_index,
                                             self.num_slices,
                                             self.batch_size,
                                             sampler_clip_length,
                                             self.drop_remainder,
                                             self.pad_remainder,
                                             False,  # shuffle_across_dataset
                                             self.is_modulo_slice,
                                             True)  # pad_across_dataset

        else:
            if self.shuffle:
                assert self.seed is not None, "seed not set"

            sampler_clip_length = len(self.vid_list)
            self.shuffler = dataset_shuffler(self.seed,
                                             self.shuffle,
                                             self.slice_index,
                                             self.num_slices,
                                             self.batch_size,
                                             sampler_clip_length,
                                             self.drop_remainder,
                                             self.pad_remainder,
                                             self.shuffle,  # shuffle_across_dataset
                                             self.is_modulo_slice,
                                             True)  # pad_across_dataset

        # idxs not needed here, only len needed
        self.num_batches_slice = self.shuffler.get_num_iterable_elements() // self.batch_size
        print("num video: {} num clips: {} batch size: {} sliced, rounded clips: {} num batches: {}".format(len(
            self.vid_list), sampler_clip_length, self.batch_size, self.shuffler.get_num_iterable_elements(), self.num_batches_slice))

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

        if not self.fixed_clip_mode:
            print("Iter ...", end=" ")
            clip_dataset_iter = self.sampler_inst.get_iter_array()
            idxs = self.shuffler.gen_idx_list()

            self.vid_list_slice_iter = clip_dataset_iter[idxs]
            print("Done!")

        else:

            shuffle_idx = self.shuffler.gen_idx_list()

            self.vid_list_slice_iter = self.vid_list[shuffle_idx]
            self.lbl_list_slice_iter = self.lbl_list[shuffle_idx]

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

        if not self.fixed_clip_mode:

            clip_list = self.vid_list_slice_iter[start:end]
            lbl_list = np.zeros([self.batch_size], dtype=self.meta_dtype)
            vid_list = []

            for idx, clip_idx_list in enumerate(clip_list):
                video_index, clip_index = self.video_clips.get_clip_location(
                    clip_idx_list)
                video_path = self.vid_list[video_index]
                vid_list.append(video_path)
                lbl_list[idx] = self.lbl_list[video_index]
                clip_resample_idx = self.video_clips_list[video_index][clip_index]
                # print("reader next for {} clip idx {} video {} clip {} path {} lbl {} resampling {}".format(
                # idx, clip_idx_list, video_index, clip_index, video_path, lbl_list[idx],
                # clip_resample_idx))

                clip_resample_idx_np = np.array(
                    clip_resample_idx, dtype=self.resample_dtype)

                resample_idx[idx] = clip_resample_idx_np

        else:

            vid_list = self.vid_list_slice_iter[start:end]
            lbl_list = self.lbl_list_slice_iter[start:end]

            resample_single_vid = np.arange(self.start_frame_index, (
                self.start_frame_index + self.frames_per_clip), dtype=self.resample_dtype)

            for i in range(self.batch_size):
                resample_idx[i] = resample_single_vid

        return vid_list, lbl_list, resample_idx
