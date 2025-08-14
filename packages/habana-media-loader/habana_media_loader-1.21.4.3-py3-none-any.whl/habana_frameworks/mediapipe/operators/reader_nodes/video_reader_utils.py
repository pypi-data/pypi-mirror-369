import numpy as np
from typing import List, Tuple, Union
import av

# ToDo: enable only for testing
g_use_torch_for_fps = False


if g_use_torch_for_fps:

    # ToDo: May not be needed
    import torch.utils.data
    from torchvision.datasets.utils import tqdm
    from typing import TypeVar

    T = TypeVar("T")

    def _collate_fn(x: T) -> T:
        # Dummy collate function to be used with _VideoFrameRateDataset
        return x

    def videoFrameNumFrameRate(file_path: str) -> Tuple[int, float]:
        try:
            with av.open(file_path, metadata_errors="ignore") as container:
                video_stream = container.streams.video[0]
                total_frames = video_stream.frames
                avg_frame_rate = float(video_stream.average_rate)
        except av.AVError:
            print("Got AVError in File ", file_path)
            # Ignore Video with AV Error
            total_frames = 0
            avg_frame_rate = 1.0
        return total_frames, avg_frame_rate

    class _VideoFrameRateDataset:
        """
        Dataset used to parallelize the reading of the number of frames and frame rate
        of a list of videos, given their paths in the filesystem.
        """

        def __init__(self, video_paths: np.ndarray) -> None:
            self.video_paths = video_paths

        def __len__(self) -> int:
            return len(self.video_paths)

        def __getitem__(self, idx: int) -> Tuple[int, float]:
            return videoFrameNumFrameRate(self.video_paths[idx])

    def compute_num_frame_torch(vid_list: np.ndarray) -> Tuple[List[int], List[float]]:
        """
        get number of frames and average frame rate of each video using torch.utils.data.DataLoader
        """

        num_frame_list = []
        avg_frame_rate_list = []
        num_workers = 4  # ToDo: Update if needed

        # use a DataLoader to parallelize videoFrameNumFrameRate, so need to
        # create a dummy dataset first
        dl: torch.utils.data.DataLoader = torch.utils.data.DataLoader(
            _VideoFrameRateDataset(vid_list),
            batch_size=16,
            num_workers=num_workers,
            collate_fn=_collate_fn,
        )

        with tqdm(total=len(dl)) as pbar:
            for batch in dl:
                pbar.update(1)
                num_frames, fps = list(zip(*batch))
                num_frame_list.extend(num_frames)
                avg_frame_rate_list.extend(fps)

        return num_frame_list, avg_frame_rate_list

else:
    from tqdm import tqdm

    def compute_num_frame(vid_list: np.ndarray) -> Tuple[List[int], List[float]]:
        """
        get number of frames and average frame rate of each video.
        """
        num_frame_list = []
        avg_frame_rate_list = []

        with tqdm(total=len(vid_list)) as pbar:
            for file in vid_list:
                pbar.update(1)
                try:
                    with av.open(file, metadata_errors="ignore") as container:
                        video_stream = container.streams.video[0]
                        total_frames = video_stream.frames
                        avg_frame_rate = float(video_stream.average_rate)
                except av.AVError:
                    print("Got AVError in File ", file)
                    # Ignore Video with AV Error
                    total_frames = 0
                    avg_frame_rate = 1.0
                num_frame_list.append(total_frames)
                avg_frame_rate_list.append(avg_frame_rate)
            return num_frame_list, avg_frame_rate_list


def get_num_frame(vid_list):
    if not g_use_torch_for_fps:
        num_frame, avg_frame_rate = compute_num_frame(vid_list)
    else:
        num_frame, avg_frame_rate = compute_num_frame_torch(vid_list)
    return num_frame, avg_frame_rate


class RandomSampler:
    """
    Samples at most max_clips_per_video clips for each video randomly
    """

    def __init__(self,
                 video_clips: Union[List[np.ndarray],
                                    List[int]],
                 max_clips_per_video: int,
                 seed: int) -> None:
        self.max_clips_per_video = max_clips_per_video
        #  list of clips or clip lengths
        self.vid_clips_list = video_clips
        self.rng = np.random.default_rng(seed)

    def get_iter_array(self) -> np.ndarray:
        idxs = []
        s = 0
        # select at most self.max_clips_per_video for each video, randomly
        for c in self.vid_clips_list:
            if (isinstance(c, np.ndarray)):
                length = len(c)
            else:
                assert isinstance(c, int), "expected int clip length"
                length = c
            size = min(length, self.max_clips_per_video)

            sampled = self.rng.permutation(length)[:size] + s
            s += length
            idxs.append(sampled)
        idxs = np.concatenate(idxs)
        # shuffle all clips randomly
        perm = self.rng.permutation(len(idxs))
        idxs_np = np.array(idxs[perm], dtype=np.uint32)
        return idxs_np

    def get_length(self) -> int:
        """
        Calculates number of clips that will be generated at each iter
        """
        sampler_length = 0
        for c in self.vid_clips_list:
            if (isinstance(c, np.ndarray)):
                length = len(c)
            else:
                assert isinstance(c, int), "expected int clip length"
                length = c
            size = min(length, self.max_clips_per_video)
            sampler_length += size

        return sampler_length


class UniformSampler:
    """
    Samples num_clips_per_video clips for each video.
    """

    def __init__(self, video_clips: Union[List[np.ndarray],
                 List[int]], num_clips_per_video: int) -> None:
        self.num_clips_per_video = num_clips_per_video
        #  list of clips or clip lengths
        self.vid_clips_list = video_clips

    def get_iter_array(self) -> np.ndarray:
        """
        Sample self.num_clips_per_video clips for each video, equally spaced.
        """
        idxs = []
        s = 0
        # select self.num_clips_per_video for each video, uniformly spaced
        for c in self.vid_clips_list:
            if (isinstance(c, np.ndarray)):
                length = len(c)
            else:
                assert isinstance(c, int), "expected int clip length"
                length = c
            if length == 0:
                continue

            sampled = np.floor(np.linspace(
                s, s + length - 1, num=self.num_clips_per_video, dtype=np.float32)).astype(np.int32)

            s += length
            idxs.append(sampled)
        idxs = np.concatenate(idxs)
        idxs_np = np.array(idxs, dtype=np.uint32)
        return idxs_np

    def get_length(self) -> int:
        """
        Calculates number of clips that will be generated at each iter
        """
        sampler_length = 0
        for c in self.vid_clips_list:
            if (isinstance(c, np.ndarray)):
                length = len(c)
            else:
                assert isinstance(c, int), "expected int clip length"
                length = c
            if length == 0:
                continue
            sampler_length += self.num_clips_per_video
        return sampler_length


class ContiguousSampler:
    """
    Samples at most max_clips_per_video contiguous clips for each video
    """

    def __init__(self, video_clips: Union[List[np.ndarray],
                 List[int]], num_clips_per_video: int) -> None:
        self.max_clips_per_video = num_clips_per_video
        #  list of clips or clip lengths
        self.vid_clips_list = video_clips

    def get_iter_array(self) -> np.ndarray:
        """
        Sample self.max_clips_per_video contiguous clips for each video.
        """
        idxs = []
        s = 0
        # select at most self.max_clips_per_video contiguous clips for each video,
        for c in self.vid_clips_list:
            if (isinstance(c, np.ndarray)):
                length = len(c)
            else:
                assert isinstance(c, int), "expected int clip length"
                length = c
            if length == 0:
                continue
            size = min(length, self.max_clips_per_video)

            sampled = np.arange(size, dtype=np.uint32) + s
            s += length
            idxs.append(sampled)
        idxs = np.concatenate(idxs)
        idxs_np = np.array(idxs, dtype=np.uint32)
        return idxs_np

    def get_length(self) -> int:
        """
        Calculates number of clips that will be generated at each iter
        """
        sampler_length = 0
        for c in self.vid_clips_list:
            if (isinstance(c, np.ndarray)):
                length = len(c)
            else:
                assert isinstance(c, int), "expected int clip length"
                length = c
            size = min(length, self.max_clips_per_video)
            sampler_length += size

        return sampler_length
