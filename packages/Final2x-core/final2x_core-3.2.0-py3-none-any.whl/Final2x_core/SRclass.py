import math

import cv2
import numpy as np
from ccrestoration import AutoModel, SRBaseModel
from loguru import logger

from Final2x_core.config import SRConfig
from Final2x_core.util import PrintProgressLog, get_device


class CCRestoration:
    """
    Super-resolution class for processing images, using ccrestoration.

    :param config: SRConfig
    """

    def __init__(self, config: SRConfig) -> None:
        self.config: SRConfig = config

        tile = (128, 128) if self.config.use_tile else None

        PrintProgressLog().set(len(self.config.input_path), 1)

        self._SR_class: SRBaseModel = AutoModel.from_pretrained(
            pretrained_model_name=self.config.pretrained_model_name,
            device=get_device(self.config.device),
            fp16=False,
            tile=tile,
            gh_proxy=self.config.gh_proxy,
        )

        logger.info("SR Class init, device: " + str(self._SR_class.device))

    @logger.catch  # type: ignore
    def process(self, img: np.ndarray) -> np.ndarray:
        """
        set target size, and process image
        :param img: img to process
        :return:
        """

        _target_size = (
            math.ceil(img.shape[1] * self.config.target_scale),
            math.ceil(img.shape[0] * self.config.target_scale),
        )

        img = self._SR_class.inference_image(img)
        PrintProgressLog().printProgress()

        if abs(float(self.config.target_scale) - float(self.config.cc_model_scale)) < 1e-3:  # type: ignore
            return img

        img = cv2.resize(img, _target_size, interpolation=cv2.INTER_LINEAR)

        return img
