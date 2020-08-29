from task import cartpole
from extern.wann import wann_train as wtrain
from extern.wann.neat_src import ann as wnet
from stable_baselines.common import make_vec_env
from stable_baselines import PPO2
from stable_baselines.common.policies import MlpPolicy
import gym
import os
import multiprocessing as mp
import extern.wann.vis as wann_vis
import matplotlib.pyplot as plt
from task import task
import imageio
import numpy as np
import config as run_config


SEED_RANGE_MIN = 1
SEED_RANGE_MAX = 100000000


# TODO: proper logging
def main():
    if run_config.TASK in ['cartpole-balance']:
        run(cartpole.get_task_config())
    if run_config.TASK in ['bipedal-walker']:
        run(cartpole.get_task_config())
    else:
        raise Exception('No implemented environment found. Please refer to list of implemented environments in README')


def run(config):
    RESULTS_PATH = config['RESULTS_PATH']
    EXPERIMENT_ID = config['EXPERIMENT_ID']
    ARTIFACTS_PATH = f'{RESULTS_PATH}artifact{os.sep}{EXPERIMENT_ID}{os.sep}'
    VIS_RESULTS_PATH = f'{RESULTS_PATH}vis{os.sep}{EXPERIMENT_ID}{os.sep}'
    SAVE_GIF_PATH = f'{RESULTS_PATH}gif{os.sep}'
    TB_LOG_PATH = f'{RESULTS_PATH}tb-log{os.sep}{EXPERIMENT_ID}{os.sep}'
    WANN_OUT_PREFIX = f'{ARTIFACTS_PATH}wann{os.sep}'

    paths = [ARTIFACTS_PATH, VIS_RESULTS_PATH, SAVE_GIF_PATH, TB_LOG_PATH, WANN_OUT_PREFIX]
    for p in paths:
        if not os.path.isdir(p):
            os.makedirs(p)

    GAME_CONFIG = config['GAME_CONFIG']
    ENV_NAME = GAME_CONFIG.env_name

    games = {
        ENV_NAME: GAME_CONFIG
    }

    wtrain.init_games_config(games)
    gym.envs.register(
        id=config['WANN_ENV_ID'],
        entry_point=config['ENTRY_POINT'],
        max_episode_steps=GAME_CONFIG.max_episode_length
    )

    wann_param_config = config['WANN_PARAM_CONFIG']
    wann_args = dict(
        hyperparam=wann_param_config,
        outPrefix=WANN_OUT_PREFIX,
        num_workers=mp.cpu_count(),
        games=games
    )

    if run_config.USE_PREV_EXPERIMENT:
        m = PPO2.load(config['PREV_EXPERIMENT_PATH'])
    else:
        if GAME_CONFIG.alg == task.ALG.PPO:
            env = make_vec_env(ENV_NAME, n_envs=mp.cpu_count())
            m = PPO2(MlpPolicy, env, verbose=0, tensorboard_log=TB_LOG_PATH)
        elif GAME_CONFIG.alg == task.ALG.DDPG:
            pass
        elif GAME_CONFIG.alg == task.ALG.TD3:
            pass
        else:
            raise Exception(f'Algorithm configured is not currently supported')

    # Take one step first without WANN to ensure primary algorithm model artifacts are stored
    m.learn(total_timesteps=1)
    m.save(ARTIFACTS_PATH+task.MODEL_ARTIFACT_FILENAME)

    c = 0
    for i in range(run_config.NUM_TRAIN_STEPS):
        print(f'LEARNING ITERATION {i}/{run_config.NUM_TRAIN_STEPS}')
        agent_params = m.get_parameters()
        agent_params = dict((key, value) for key, value in agent_params.items())
        wann_args['agent_params'] = agent_params
        wann_args['agent_env'] = m.get_env()

        if c == 0:
            print('PERFORMING WANN TRAINING STEP...')
            if run_config.TRAIN_WANN:
                wtrain.run(wann_args)
            print('WANN TRAINING STEP COMPLETE')

        # TODO: add callback for visualize WANN interval as well as
        # gif sampling at different stages
        if run_config.VISUALIZE_WANN:
            champion_path = f'{WANN_OUT_PREFIX}_best.out'
            wVec, aVec, _ = wnet.importNet(champion_path)

            wann_vis.viewInd(champion_path, GAME_CONFIG)
            plt.savefig(f'{VIS_RESULTS_PATH}wann-net-graph.png')

        # TODO: add checkpointing and restore from checkpoint
        agent_config = config['AGENT']
        m.learn(total_timesteps=agent_config['total_timesteps'], log_interval=agent_config['log_interval'])
        m.save(ARTIFACTS_PATH+task.MODEL_ARTIFACT_FILENAME)

        # only one iteration when WANN isn't used
        if not run_config.USE_WANN:
            break

        c += 1
        if c >= run_config.RETRAIN_WANN_N_STEPS:
            c = 0

    if run_config.RENDER_TEST_GIFS:
        vid_len = config['VIDEO_LENGTH']
        render_agent(m, ENV_NAME, vid_len, SAVE_GIF_PATH, filename=f'{EXPERIMENT_ID}-agent.gif')
        render_agent(m, ENV_NAME, vid_len, SAVE_GIF_PATH, filename='random.gif')


def render_agent(model, env_name, vid_len,
                 out_path, filename, rand_agent=False, render_gif=True):
    if render_gif:
        with gym.make(env_name) as test_env:
            images = []
            obs = test_env.reset()
            for _ in range(vid_len):
                img = test_env.render(mode='rgb_array')
                images.append(img)

                if rand_agent:
                    a = test_env.action_space.sample()
                else:
                    a = model.predict(obs, deterministic=True)[0]

                obs, _, done, _ = test_env.step(a)
                if done:
                    obs = test_env.reset()

                imageio.mimsave(f'{out_path}{filename}',
                                [np.array(img) for i, image in enumerate(images) if i % 2 == 0], fps=30)


if __name__ == '__main__':
    main()
