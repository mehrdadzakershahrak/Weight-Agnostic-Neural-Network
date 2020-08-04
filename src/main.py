from task import cartpole
import argparse
from datetime import datetime
import sys
import multiprocessing as mp


# TODO: add proper logging

def main(args):
    parser = argparse.ArgumentParser(description='WANN as RL Prior Experiment')

    # TODO: perform type assertions on arguments with argparse
    parser.add_argument('--alg', action='store_true', default='ppo')
    parser.add_argument('--env', action='store_true', default='wann-cartpolebalance-v1')
    parser.add_argument('--seed', action='store_true', default=0)
    parser.add_argument('--network', action='store_true', default='mlp')
    parser.add_argument('--num_timesteps', action='store_true', default=2e7)
    parser.add_argument('--log_path', action='store_true', default='results/log/')
    parser.add_argument('--play', action='store_true')
    parser.add_argument('--env_type', action='store_true', default='custom')
    parser.add_argument('--save_path', action='store_true', default=f'~/tmp/WANN/models-{str(datetime.now(tz=None)).replace(" ", "_")}')
    parser.add_argument('--load_path', action='store_true')
    parser.add_argument('-d', '--default', type=str, \
                        help='default hyperparameter file', default='extern/wann/p/default_wann.json')
    parser.add_argument('-p', '--hyperparam', type=str, \
                        help='hyperparameter file', default='extern/wann/p/laptop_swing.json')
    parser.add_argument('-o', '--outPrefix', type=str, \
                        help='file name for result output', default='test')
    parser.add_argument('-n', '--num_worker', type=int, \
                        help='number of cores to use', default=mp.cpu_count())

    # parser.add_argument('--env', help='environment ID', type=str, default='Reacher-v2')
    # parser.add_argument('--env_type',
    #                     help='type of environment, used when the environment type cannot be automatically determined',
    #                     type=str)
    # parser.add_argument('--seed', help='RNG seed', type=int, default=None)
    # parser.add_argument('--alg', help='Algorithm', type=str, default='ppo2')
    # parser.add_argument('--num_timesteps', type=float, default=1e6),
    # parser.add_argument('--network', help='network type (mlp, cnn, lstm, cnn_lstm, conv_only)', default=None)
    # parser.add_argument('--gamestate', help='game state to load (so far only used in retro games)', default=None)
    # parser.add_argument('--num_env',
    #                     help='Number of environment copies being run in parallel. When not specified, set to number of cpus for Atari, and to 1 for Mujoco',
    #                     default=None, type=int)
    # parser.add_argument('--reward_scale', help='Reward scale factor. Default: 1.0', default=1.0, type=float)
    # parser.add_argument('--save_path', help='Path to save trained model to', default=None, type=str)
    # parser.add_argument('--save_video_interval', help='Save video every x steps (0 = disabled)', default=0, type=int)
    # parser.add_argument('--save_video_length', help='Length of recorded video. Default: 200', default=200, type=int)
    # parser.add_argument('--log_path', help='Directory to save learning curve data.', default=None, type=str)
    # parser.add_argument('--play', default=False, action='store_true')

    args, _ = parser.parse_known_args()

    if args.env.strip().lower() in ['wann-cartpolebalance-v1']:
        cartpole.balance(args)
    else:
        raise Exception('No implemented environment found. Please refer to list of implemented environments in README')


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == '__main__':
    main(sys.argv)
