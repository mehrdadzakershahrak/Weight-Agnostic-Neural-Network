import os
import logging.config
import structlog
from structlog import processors, stdlib, threadlocal, configure

VERSION_NUM = 9

# GLOBAL CONFIGURABLE PARAMETERS
# DEFAULT CONFIGURATION
############################################
TASK = 'lunar-lander'
EXPERIMENT_ID = f'no-wann-sac-lunarlander-v2-{VERSION_NUM}'
SEED = 0  # high level seed for all experiments
USE_PREV_EXPERIMENT = False
PREV_EXPERIMENT_PATH = 'prev-run'
TRAIN_WANN = False
USE_WANN = False
VISUALIZE_WANN = False
RENDER_TEST_GIFS = False
NUM_TRAIN_STEPS = 1
DESCRIPTION = '''
    This experiment implements WANN with the SAC critic sampled from the replay buffer    
    
    lunar lander baselines 1/10
'''
############################################

# TODO: DRY THIS UP
track_run_configs = dict(
    SEED=SEED,
    TASK=TASK,
    EXPERIMENT_ID=EXPERIMENT_ID,
    TRAIN_WANN=TRAIN_WANN,
    USE_WANN=USE_WANN,
    NUM_TRAIN_STEPS=NUM_TRAIN_STEPS
)

performance_log_path = f'result{os.sep}{EXPERIMENT_ID}{os.sep}log{os.sep}alg-step{os.sep}'
if not os.path.isdir(performance_log_path):
    os.makedirs(performance_log_path)

logging.config.dictConfig(
    dict(
        version=1,
        handlers=dict(
            file={
                'class': 'logging.FileHandler',
                'filename': performance_log_path+'alg-performance.log',
                'mode': 'w',
                'formatter': 'jsonformat',
            },
            stdout={
                'class': 'logging.StreamHandler',
                'formatter': 'jsonformat'
            }
        ),
        formatters=dict(
            jsonformat={
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(message)s'
            },
        ),
        loggers={
            '': {
                'handlers': ['stdout', 'file'],
                'level': logging.INFO
            }
        },
        disable_existing_loggers=True
    )
)

configure(
    processors=[
        processors.TimeStamper(fmt='iso'),
        processors.format_exc_info,
        processors.StackInfoRenderer(),
        stdlib.filter_by_level,
        processors.UnicodeDecoder(),
        stdlib.render_to_log_kwargs
    ],
    context_class=threadlocal.wrap_dict(dict),
    logger_factory=stdlib.LoggerFactory(),
    wrapper_class=stdlib.BoundLogger
)


def log():
    return structlog.getLogger('default')
