from blueness import module
from bluer_objects import file, objects
from bluer_objects.metadata import post_to_object

from bluer_algo import NAME
from bluer_algo.yolo.dataset.classes import YoloDataset
from bluer_algo.logger import logger


NAME = module.name(__file__, NAME)


def ingest(
    object_name: str,
    log: bool = True,
    verbose: bool = False,
) -> bool:
    logger.info(
        "{}.ingest -> {}".format(
            NAME,
            object_name,
        )
    )

    if not file.copy(
        file.absolute(
            "../../../../assets/coco_128.yaml",
            file.path(__file__),
        ),
        objects.path_of(
            object_name=object_name,
            filename="metadata.yaml",
        ),
        log=log,
    ):
        return False

    dataset = YoloDataset(
        object_name=object_name,
    )
    if not dataset.valid:
        return False

    return post_to_object(
        object_name,
        "dataset",
        {
            "count": len(dataset.list_of_records),
            "source": "coco_128",
        },
    )
