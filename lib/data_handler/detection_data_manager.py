import logging

import torch
from torch.utils.data.sampler import Sampler

from data_handler.data_manager_api import DataManager, Mode
from roi_data_layer.roidb import combined_roidb
from roi_data_layer.roibatchLoader import roibatchLoader
from torch.utils.data import DataLoader


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BDSampler(Sampler):
    def __init__(self, train_size, batch_size, seed):
        super(BDSampler, self).__init__(data_source="")  # TODO what to do with data_source?
        self.seed = seed  # TODO is it done no the CPU?
        torch.manual_seed(seed)

        self.data_size = train_size
        self.num_per_batch = int(train_size / batch_size)
        self.batch_size = batch_size
        self.range = torch.arange(0, batch_size).view(1, batch_size).long()
        self.leftover_flag = False
        if train_size % batch_size:
            self.leftover = torch.arange(self.num_per_batch * batch_size, train_size).long()
            self.leftover_flag = True

    def __iter__(self):
        rand_num = torch.randperm(self.num_per_batch).view(-1, 1) * self.batch_size
        self.rand_num = rand_num.expand(self.num_per_batch, self.batch_size) + self.range

        self.rand_num_view = self.rand_num.view(-1)

        if self.leftover_flag:
            self.rand_num_view = torch.cat((self.rand_num_view, self.leftover), 0)

        return iter(self.rand_num_view)

    def __len__(self):
        return self.data_size  # TODO (self.data_size + self.batch_size - 1) // self.batch_size


class FasterRCNNDataManager(DataManager):
    def __init__(self, mode, imdb_name, seed, num_workers, is_cuda, batch_size=1):
        super(FasterRCNNDataManager, self).__init__(mode, is_cuda)
        self.imdb, roidb, ratio_list, ratio_index = combined_roidb(imdb_name,
                                                                   training=self.is_train)
        dataset = roibatchLoader(roidb, ratio_list, ratio_index, batch_size,
                                 self.imdb.num_classes, training=self.is_train)

        if mode == Mode.TRAIN:
            train_size = len(roidb)
            self.train_size = train_size
            logger.info('{:d} roidb entries.'.format(train_size))
            sampler_batch = BDSampler(train_size, batch_size, seed)
            data_loader = DataLoader(dataset, batch_size=batch_size, num_workers=num_workers,
                                     sampler=sampler_batch)
        elif mode == Mode.TEST:
            self.imdb.competition_mode(on=True)  # TODO this function is not implemented...
            data_loader = DataLoader(dataset, batch_size=batch_size, num_workers=num_workers,
                                     shuffle=False, pin_memory=True)
        else:
            raise Exception("Not valid mode {} - should be TRAIN or TEST".format(mode))

        self.batch_size = batch_size
        self.iters_per_epoch = int(self.train_size / self.batch_size)
        self.data_iter = iter(data_loader)

    def transform_data_tensors(self, data):
        self.im_data.data.resize_(data[0].size()).copy_(data[0])
        self.im_info.data.resize_(data[1].size()).copy_(data[1])
        self.gt_boxes.data.resize_(data[2].size()).copy_(data[2])
        self.num_boxes.data.resize_(data[3].size()).copy_(data[3])
        return self.im_data, self.im_info, self.gt_boxes, self.num_boxes

    def __len__(self):
        return len(self.imdb.image_index)

    @property
    def num_classes(self):
        return self.imdb.num_classes

