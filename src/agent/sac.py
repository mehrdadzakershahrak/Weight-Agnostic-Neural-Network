from agent import Agent
from copy import copy
from rlkit.torch.sac.sac import SACTrainer as SoftActorCritic_rlkit
from rlkit.torch.networks import FlattenMlp
from rlkit.torch.sac.policies import TanhGaussianPolicy
import numpy as np
import torch
import rlkit.torch.pytorch_util as torch_util


class SAC(Agent):
    def __init__(self, env, replay, policy_net, q_net, v_net, params):
        super().__init__(env, replay, nets=(policy_net, q_net, v_net, params))

        self._params = params
        self._env = env
        self._replay = replay
        self._policy_net = policy_net
        self._q_net = q_net
        self._v_net = v_net

        self._target_q_net = copy.deepcopy(q_net)
        self._target_v_net = copy.deepcopy(v_net)

        self._alg = SoftActorCritic_rlkit(
            env=self._env,
            policy=self._policy_net,
            qf1=self._v_net,
            qf2=self._q_net,
            target_qf1=self._target_v_net,
            target_qf2=self._target_q_net,
            use_automatic_entropy_tuning=False,
            **self._params
        )

    def train(self, n_iters, batch_size=1024):
        # TODO: add logging/checkpointing here
        for _ in range(n_iters):
            batch = self._replay.random_batch(batch_size)
            self._alg.train(batch)

    def load(self):
        pass

    def save(self):
        pass

    def pred(self, deterministic=True):
        pass


def vanilla_nets(env, n_lay_nodes, n_depth, clip_val=1):
    obs_dim = int(np.prod(env.observation_space.shape))
    action_dim = int(np.prod(env.action_space.shape))
    hidden = [n_lay_nodes]*n_depth

    v_net = FlattenMlp(
        hidden_sizes=hidden,
        input_size=obs_dim + action_dim,
        output_size=1,
    ).to(device=torch_util.device)

    q_net = FlattenMlp(
        hidden_sizes=hidden,
        input_size=obs_dim + action_dim,
        output_size=1,
    ).to(device=torch_util.device)

    policy_net = TanhGaussianPolicy(
        hidden_sizes=hidden,
        obs_dim=obs_dim,
        action_dim=action_dim,
    ).to(device=torch_util.device)

    nets = [v_net, q_net, policy_net]
    for n in nets:
        for p in n.parameters():
            p.register_hook(lambda grad: torch.clamp(grad, -clip_val, clip_val))

    return (n for n in nets)
