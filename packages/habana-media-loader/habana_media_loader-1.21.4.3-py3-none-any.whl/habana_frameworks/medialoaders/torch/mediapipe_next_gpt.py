#!/bin/env python
import numpy as np

from habana_frameworks.mediapipe import fn  # NOQA
from habana_frameworks.mediapipe.mediapipe import MediaPipe  # NOQA
from habana_frameworks.mediapipe.media_types import imgtype as it  # NOQA
from habana_frameworks.mediapipe.media_types import dtype as dt  # NOQA
from habana_frameworks.mediapipe.media_types import randomCropType as rct  # NOQA
from habana_frameworks.mediapipe.media_types import ftype as ft  # NOQA

g_RGB_MEAN_VALUES = [0.48145466, 0.4578275, 0.40821073]
g_RGB_STD_VALUES = [0.26862954, 0.26130258, 0.27577711]
g_RGB_MULTIPLIER = 255

g_resize_dim = 224


class NextGptVisionMediaPipe(MediaPipe):

    """
    Class defining nextGPT Vision media pipe

    """

    def __init__(self, batch_size, media_queue, queue_depth=0, device="legacy", num_thread=1):

        assert queue_depth == 0, "queue depth 0 expected"
        assert device == "legacy", "legacy device only supported"

        self.batch_size = batch_size
        self.queue_depth = queue_depth
        resize_dim = g_resize_dim

        super().__init__(device=device,
                         prefetch_depth=self.queue_depth,
                         batch_size=self.batch_size,
                         num_threads=num_thread,
                         pipe_name=self.__class__.__name__)

        self.input = fn.ReadMediaDatasetFromExt(ext_queue=media_queue)

        self.decode = fn.ImageDecoder(output_format=it.RGB_P,
                                      resize=[resize_dim, resize_dim],
                                      resampling_mode=ft.BICUBIC,
                                      random_crop_type=rct.CENTER_CROP,
                                      )

        mean_data = np.array(
            [m * g_RGB_MULTIPLIER for m in g_RGB_MEAN_VALUES], dtype=np.float32)
        std_data = np.array([1 / (s * g_RGB_MULTIPLIER)
                            for s in g_RGB_STD_VALUES], dtype=np.float32)

        self.std_node = fn.MediaConst(
            data=std_data, shape=[1, 1, 3], batch_broadcast=False, dtype=dt.FLOAT32)
        self.mean_node = fn.MediaConst(
            data=mean_data, shape=[1, 1, 3], batch_broadcast=False, dtype=dt.FLOAT32)

        self.cmn = fn.CropMirrorNorm(
            crop_w=resize_dim, crop_h=resize_dim, crop_d=0, dtype=dt.FLOAT32)

        # self.transp = fn.Transpose(permutation=[2, 0, 1, 3], tensorDim=4, dtype=dt.FLOAT32)

        print("NextGptVisionMediaPipe batch_size {}".format(self.batch_size))

    def definegraph(self):
        files = self.input()
        image = self.decode(files)  # WHCN

        std = self.std_node()
        mean = self.mean_node()
        image = self.cmn(image, mean, std)

        # image = self.transp(image) # WHCN -> CWHN
        return image
