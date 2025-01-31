# coding=utf-8
# Copyright 2020 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Training and evaluation"""

import run_lib
from absl import app
from absl import flags
from ml_collections.config_flags import config_flags
import tensorflow as tf
import logging
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '5,6,7'
os.environ['TF_USE_NVLINK_FOR_PARALLEL_COMPILATION'] = '0'
os.environ[' JAX_OMNISTAGING '] = '1'

FLAGS = flags.FLAGS

config_flags.DEFINE_config_file(
  "config", None, "Training configuration.", lock_config=True)
flags.DEFINE_string("workdir", None, "Work directory.")
flags.DEFINE_enum("mode", None, ["train", "eval","fid_stats"], "Running mode: train or eval or fid_stats")
flags.DEFINE_string("eval_folder", "eval",
                    "The folder name for storing evaluation results")
flags.DEFINE_string("fid_folder", "assets/stats",
                    "The folder name for storing FID statistics")
flags.mark_flags_as_required(["workdir", "config", "mode"])


def main(argv):
  tf.config.experimental.set_visible_devices([], "GPU")
  os.environ['XLA_PYTHON_CLIENT_PREALLOCATE'] = 'false'

  if FLAGS.mode == "train":
    # Create the working directory
    tf.io.gfile.makedirs(FLAGS.workdir)
    # Set logger so that it outputs to both console and file
    handler1 = logging.StreamHandler()
    # Make logging work for both disk and Google Cloud Storage
    gfile_stream = tf.io.gfile.GFile(os.path.join(FLAGS.workdir, 'stdout.txt'), 'w')
    handler2 = logging.StreamHandler(gfile_stream)
    formatter = logging.Formatter('%(levelname)s - %(filename)s - %(asctime)s - %(message)s')
    handler1.setFormatter(formatter)
    handler2.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    logger.setLevel('INFO')
    # Run the training pipeline
    run_lib.train(FLAGS.config, FLAGS.workdir)
  elif FLAGS.mode == "eval":
    # Run the evaluation pipeline
    run_lib.evaluate(FLAGS.config, FLAGS.workdir, FLAGS.eval_folder)
  elif FLAGS.mode == "fid_stats":
    # Calculate the FID statistics
    run_lib.fid_stats(FLAGS.config, FLAGS.fid_folder)
  else:
    raise ValueError(f"Mode {FLAGS.mode} not recognized.")


if __name__ == "__main__":
  app.run(main)
