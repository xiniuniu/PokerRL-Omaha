import numpy as np
import os
os.environ["OMP_NUM_THREADS"] = "1"
import random
import torch


from PokerRL.game.games import DiscretizedNLHoldem, PLO
from PokerRL.eval.lbr.LBRArgs import LBRArgs
from PokerRL.game import bet_sets
from PokerRL.game.Poker import Poker
from PokerRL.game.wrappers import VanillaEnvBuilder

from DeepCFR.EvalAgentDeepCFR import EvalAgentDeepCFR
from DeepCFR.TrainingProfile import TrainingProfile
from DeepCFR.workers.driver.Driver import Driver

if __name__ == '__main__':
    # in case we need reproductability
    """
    seed = 105
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.enabled = False
    torch.backends.cudnn.deterministic = True
    """

    ctrl = Driver(t_prof=TrainingProfile(name="PLO_3m_7.5mX14-b5000-last-patience350-Leaky-lr0.004-dense_residual",
                                         nn_type="dense_residual",

                                         DISTRIBUTED=True,
                                         CLUSTER=False,
                                         n_learner_actor_workers=14,  # 14 workers

                                         max_buffer_size_adv=3000000,  # 3e6
                                         export_each_net=False,
                                         # path_strategy_nets="",
                                         checkpoint_freq=9999,  # produces A SHITLOAD of Gbs!
                                         eval_agent_export_freq=1,

                                         # How many actions out of all legal on current step to branch randomly
                                         # = action breadth limit
                                         # 3 is the default, 4 is the current max for b_2
                                         n_actions_traverser_samples=4,
                                         # number of traversals equal to the number of entries that will be added
                                         # to adv buffer
                                         n_traversals_per_iter=150000,
                                         # number of mini_batch fetches and model updates on each iteration
                                         n_batches_adv_training=1500,
                                         max_n_las_sync_simultaneously=20,

                                         use_pre_layers_adv=True,
                                         n_cards_state_units_adv=192,
                                         n_merge_and_table_layer_units_adv=64,  # 64
                                         n_units_final_adv=64,  # 64
                                         lr_patience_adv=350,  # decrease by a factor 0.5(in PSWorker)
                                         lr_adv=0.004,

                                         # size of batch to feed to NN at once, fetched from buffer randomly.
                                         mini_batch_size_adv=5000,
                                         init_adv_model="last",  # last, random

                                         game_cls=PLO,  # PLO or DiscretizedNLHoldem
                                         env_bldr_cls=VanillaEnvBuilder,
                                         agent_bet_set=bet_sets.PL_2,
                                         n_seats=2,
                                         start_chips=10000,

                                         # You can specify one or both modes. Choosing both is useful to compare them.
                                         eval_modes_of_algo=(
                                             EvalAgentDeepCFR.EVAL_MODE_SINGLE,  # SD-CFR
                                         ),

                                         # enables simplified obs. Default works also for 3+ players
                                         use_simplified_headsup_obs=True,

                                         log_verbose=True,
                                         lbr_args=LBRArgs(lbr_bet_set=bet_sets.PL_2,
                                                          n_lbr_hands_per_seat=1,
                                                          lbr_check_to_round=Poker.TURN,
                                                          # recommended to set to Poker.TURN for 4-round games.
                                                          n_parallel_lbr_workers=1,
                                                          use_gpu_for_batch_eval=False,
                                                          DISTRIBUTED=False,
                                                          ),
                                         ),
                  eval_methods={
                      "": 99,  # lbr, br, h2h
                  },
                  n_iterations=64)

    ctrl.run()
