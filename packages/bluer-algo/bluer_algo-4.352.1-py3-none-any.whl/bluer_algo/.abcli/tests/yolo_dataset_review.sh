#! /usr/bin/env bash

function test_bluer_algo_yolo_dataset_review() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_algo_yolo_dataset_review \
        ,$options \
        $BLUER_ALGO_COCO128_TEST_DATASET
}
