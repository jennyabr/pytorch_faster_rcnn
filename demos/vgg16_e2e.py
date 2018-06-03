from __future__ import absolute_import
from __future__ import division
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

from pipeline.faster_rcnn.run_functions.run_classic_pipeline import \
    create_and_train_with_err_handling, pred_eval_with_err_handling
from util.config import ConfigProvider


config_file = os.path.join(os.getcwd(), 'demos', 'cfgs', 'vgg16.yml')
cfg = ConfigProvider()
cfg.load(config_file)
create_and_train_with_err_handling(cfg)
pred_eval_with_err_handling(cfg)

