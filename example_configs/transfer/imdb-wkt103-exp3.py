import tensorflow as tf

from open_seq2seq.models import LSTMLM
from open_seq2seq.encoders import LMEncoder
# from open_seq2seq.encoders import BidirectionalRNNEncoderWithEmbedding
from open_seq2seq.decoders import FakeDecoder
from open_seq2seq.data import IMDBDataLayer
from open_seq2seq.parts.rnns.weight_drop import WeightDropLayerNormBasicLSTMCell
from open_seq2seq.losses import CrossEntropyLoss
from open_seq2seq.optimizers.lr_policies import fixed_lr
# from open_seq2seq.data.text2text.text2text import SpecialTextTokens
# from open_seq2seq.optimizers.lr_policies import exp_decay

data_root = "/home/chipn/data/aclImdb"
processed_data_folder = 'imdb-processed-data'

base_model = LSTMLM
max_length = 256
binary = True
steps = 10

base_params = {
  # "seed": 1882, # conforming to AWD-LSTM paper
  "restore_best_checkpoint": True,
  "use_horovod": False,
  "num_gpus": 1,

  "batch_size_per_gpu": 32, # conforming to AWD-LSTM paper 80
  "eval_batch_size_per_gpu": 80,
  "num_epochs": 100, # conforming to AWD-LSTM paper 750
  "save_summaries_steps": steps,
  "print_loss_steps": steps,
  "print_samples_steps": steps,
  "save_checkpoint_steps": steps,
  "load_model": "AWD-WKT103-exp24",
  "logdir": "IMDB-WKT103-EXP3",
  "lm_vocab_file": '/home/chipn/dev/OpenSeq2Seq/wkt103-processed-data/vocab.txt',
  "processed_data_folder": processed_data_folder,
  "eval_steps": steps,

  "optimizer": "Adam", # need to change to NT-ASGD
  "optimizer_params": {},
  # luong10 decay scheme

  "lr_policy": fixed_lr,
  "lr_policy_params": {
    "learning_rate": 1e-3
  },

  "summaries": ['learning_rate', 'variables', 'gradients', 
                'variable_norm', 'gradient_norm', 'global_gradient_norm'],
  # "grad_clip":0.25, # conforming to AWD-LSTM paper
  # "max_grad_norm": 0.25, # conform to paper 0.25
  "dtype": tf.float32,
  #"dtype": "mixed",
  #"automatic_loss_scaling": "Backoff",
  "encoder": LMEncoder,
  # "encoder": BidirectionalRNNEncoderWithEmbedding,
  "encoder_params": { # will need to update
    "initializer": tf.random_uniform_initializer,
    "initializer_params": { # need different initializers for embeddings and for weights
      "minval": -0.1,
      "maxval": 0.1,
    },
    # "core_cell": tf.contrib.rnn.LayerNormBasicLSTMCell,
    "core_cell": WeightDropLayerNormBasicLSTMCell,
    "core_cell_params": {
        "num_units": 1024, # paper 1150
        "forget_bias": 1.0,
    },
    "encoder_layers": 3,
    "encoder_dp_input_keep_prob": 1.0,
    "encoder_dp_output_keep_prob": 0.9, # output dropout for middle layer 0.3
    "encoder_last_input_keep_prob": 1.0,
    "encoder_last_output_keep_prob": 0.9, # output droput at last layer is 0.4
    "recurrent_keep_prob": 1.0,
    'encoder_emb_keep_prob': 0.8,
    "encoder_use_skip_connections": False,
    "emb_size": 256,
    "num_tokens_gen": 10,
    "sampling_prob": 0.0, # 0 is always use the ground truth
    "fc_use_bias": True,
    "weight_tied": True,
    "awd_initializer": False,
  },

  "decoder": FakeDecoder, # need a new decoder with AR and TAR

  "regularizer": tf.contrib.layers.l2_regularizer,
  "regularizer_params": {
    'scale': 2e-6, # alpha
  },

  "loss": CrossEntropyLoss,
}

train_params = {
  "data_layer": IMDBDataLayer,
  "data_layer_params": {
    "data_root": data_root,
    "pad_vocab_to_eight": False,
    "shuffle": True,
    "shuffle_buffer_size": 25000,
    "repeat": True,
    "map_parallel_calls": 16,
    "prefetch_buffer_size": 8,
    "binary": binary,
    "max_length": max_length,
    # "small": True,
  },
}
eval_params = {
  "data_layer": IMDBDataLayer,
  "data_layer_params": {
    # "data_root": data_root,
    "pad_vocab_to_eight": False,
    "shuffle": False,
    "repeat": False,
    "map_parallel_calls": 16,
    "prefetch_buffer_size": 1,
    "binary": binary,
    "max_length": max_length,
    # "small": True,
  },
}

infer_params = {
  "data_layer": IMDBDataLayer,
  "data_layer_params": {
    # "data_root": data_root,
    "pad_vocab_to_eight": False,
    "shuffle": False,
    "repeat": False,
    "rand_start": False,
    "map_parallel_calls": 16,
    "prefetch_buffer_size": 8,
    "seed_tokens": "something The only game",
    "binary": binary,
    "max_length": max_length,
  },
}