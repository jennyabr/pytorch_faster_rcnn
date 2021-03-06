# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""Factory method for easily getting imdbs by name."""
from __future__ import absolute_import
from __future__ import division

from data_manager.classic_detection.datasets.coco import coco
from data_manager.classic_detection.datasets.imagenet import imagenet
from data_manager.classic_detection.datasets.pascal_voc import pascal_voc
from data_manager.classic_detection.datasets.vg import vg


def get_imdb(db_name, data_dir):
    """Get an imdb (image database) by name."""
    __sets = {}

    # Set up voc_<year>_<split>
    for year in ['2007', '2012']:
        for split in ['train', 'val', 'trainval', 'test']:
            name = 'voc_{}_{}'.format(year, split)
            __sets[name] = (lambda split=split, year=year: pascal_voc(split, year, data_dir=data_dir))

    # Set up coco_2014_<split>
    for year in ['2014']:
        for split in ['train', 'val', 'minival', 'valminusminival', 'trainval']:
            name = 'coco_{}_{}'.format(year, split)
            __sets[name] = (lambda split=split, year=year: coco(split, year, data_dir=data_dir))

    # Set up coco_2014_cap_<split>
    for year in ['2014']:
        for split in ['train', 'val', 'capval', 'valminuscapval', 'trainval']:
            name = 'coco_{}_{}'.format(year, split)
            __sets[name] = (lambda split=split, year=year: coco(split, year, data_dir=data_dir))

    # Set up coco_2015_<split>
    for year in ['2015']:
        for split in ['test', 'test-dev']:
            name = 'coco_{}_{}'.format(year, split)
            __sets[name] = (lambda split=split, year=year: coco(split, year, data_dir=data_dir))

    # Set up vg_<split>
    for version in ['150-50-20', '150-50-50', '500-150-80', '750-250-150', '1750-700-450', '1600-400-20']:
        for split in ['minitrain', 'smalltrain', 'train', 'minival', 'smallval', 'val', 'test']:
            name = 'vg_{}_{}'.format(version, split)
            __sets[name] = (lambda split=split, version=version: vg(version, split, data_dir=data_dir))

    # Set up image net.
    for split in ['train', 'val', 'val1', 'val2', 'test']:
        name = 'imagenet_{}'.format(split)
        devkit_path = 'data/imagenet/ILSVRC/devkit'
        data_path = 'data/imagenet/ILSVRC'
        __sets[name] = (
            lambda split=split, devkit_path=devkit_path, data_path=data_path:
            imagenet(split, data_dir=data_dir, devkit_path=devkit_path, data_path=data_path))

    if db_name not in __sets:
        raise KeyError('Unknown dataset: {}'.format(db_name))
    return __sets[db_name]()

