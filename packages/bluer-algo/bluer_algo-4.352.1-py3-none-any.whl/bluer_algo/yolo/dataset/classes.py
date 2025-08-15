import os
import cv2
import os
import random
from tqdm import tqdm
import numpy as np
from typing import Dict, Any, List

from blueness import module
from bluer_options.logger import log_list, log_list_as_str
from bluer_objects import objects, file, path
from bluer_objects.logger.image import log_image_grid

from bluer_algo import NAME
from bluer_algo.host import signature
from bluer_algo.logger import logger

NAME = module.name(__file__, NAME)


class YoloDataset:
    def __init__(
        self,
        object_name: str,
        log: bool = True,
    ):
        self.object_name = object_name

        self.valid, self.metadata = file.load_yaml(
            objects.path_of(
                object_name=object_name,
                filename="metadata.yaml",
            )
        )

        object_path = objects.object_path(object_name)

        self.train_images_path = os.path.join(
            path.absolute(
                self.metadata["path"],
                object_path,
            ),
            self.metadata["train"],
        )

        self.train_labels_path = self.train_images_path.replace(
            "images",
            "labels",
        )

        list_of_images = [
            file.name(filename)
            for filename in file.list_of(
                os.path.join(self.train_images_path, "*.jpg"),
                recursive=False,
            )
        ]
        if log:
            logger.info(f"found {len(list_of_images)} image(s).")

        list_of_labels = [
            file.name(filename)
            for filename in file.list_of(
                os.path.join(self.train_labels_path, "*.txt"),
                recursive=False,
            )
        ]
        if log:
            logger.info(f"found {len(list_of_labels)} label(s).")

        self.list_of_records = [
            record_id for record_id in list_of_images if record_id in list_of_labels
        ]

        missing_images = [
            record_id
            for record_id in list_of_images
            if record_id not in self.list_of_records
        ]
        if missing_images and log:
            log_list(logger, "missing", missing_images, "image(s)", itemize=False)

        missing_labels = [
            record_id
            for record_id in list_of_labels
            if record_id not in self.list_of_records
        ]
        if missing_labels and log:
            log_list(logger, "missing", missing_labels, "label(s)", itemize=False)

        if log:
            logger.info(
                "{}: {} record(s)".format(
                    NAME,
                    len(self.list_of_records),
                )
            )

    def review(self, verbose: bool = False) -> bool:
        object_path = objects.object_path(self.object_name)

        output_dir = os.path.join(object_path, "review")
        if not path.create(output_dir):
            return False

        list_of_records = random.sample(
            self.list_of_records,
            min(
                3 * 4,
                len(self.list_of_records),
            ),
        )

        items: List[Dict[str, Any]] = []
        for record_id in tqdm(list_of_records):
            success, image = file.load_image(
                os.path.join(
                    self.train_images_path,
                    f"{record_id}.jpg",
                ),
                log=verbose,
            )
            image = np.ascontiguousarray(image)
            if not success:
                return success

            success, label_info = file.load_text(
                os.path.join(
                    self.train_labels_path,
                    f"{record_id}.txt",
                )
            )
            if not success:
                return success

            h, w = image.shape[:2]
            for line in label_info:
                cls, x, y, bw, bh = map(float, line.strip().split())
                x1, y1 = int((x - bw / 2) * w), int((y - bh / 2) * h)
                x2, y2 = int((x + bw / 2) * w), int((y + bh / 2) * h)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    image,
                    self.metadata["names"][int(cls)],
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

            output_filename = os.path.join(
                output_dir,
                f"{record_id}.jpg",
            )
            if not file.save_image(
                output_filename,
                image,
                log=verbose,
            ):
                return False

            items.append({"filename": output_filename})

        return log_image_grid(
            items,
            cols=4,
            rows=3,
            verbose=verbose,
            filename=objects.path_of(
                object_name=self.object_name,
                filename="review.png",
            ),
            header=[
                f"count: {len(self.list_of_records)}",
                log_list_as_str(
                    title="",
                    list_of_items=list(self.metadata["names"].values()),
                    item_name_plural="class(es)",
                ),
            ],
            footer=signature(),
            log=verbose,
        )
