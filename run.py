from __future__ import print_function
import argparse
import datetime
import sys
import os

from jmetrics import tasks

# ============================= INITIALIZATION ==================================== #

from adsputils import setup_logging, load_config
proj_home = os.path.realpath(os.path.dirname(__file__))
config = load_config(proj_home=proj_home)
logger = setup_logging('run.py', proj_home=proj_home,
                        level=config.get('LOGGING_LEVEL', 'INFO'),
                        attach_stdout=config.get('LOG_STDOUT', False))
                        

# =============================== FUNCTIONS ======================================= #


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', dest='year',
                        help='Year for journal metrics')
    parser.add_argument('-c', '--collection', default='ALL', dest='collection',
                        help='Collection to generate journal metrics for (optional)')
    parser.add_argument('-m', '--metrics', dest='metrics',
                        help='Comma-separated list of metrics (optional)')
    
    args = parser.parse_args()

    try:
        jmetrics = tasks.create_metrics(collection=args.collection, year=args.year, metrics=args.metrics)
    except Exception as error:
        logger.error('Creating journal metrics for year {0} failed: {1}'.format(args.year, error))
        sys.exit('Creating journal metrics for year {0} failed: {1}'.format(args.year, error))