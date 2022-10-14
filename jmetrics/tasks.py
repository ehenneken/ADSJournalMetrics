from __future__ import absolute_import, unicode_literals
import os
import sys
from builtins import str
import jmetrics.app as app_module
import inspect
#from jmetrics.metrics import Eigenfactor
# ============================= INITIALIZATION ==================================== #

from adsputils import setup_logging, load_config

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
config = load_config(proj_home=proj_home)
app = app_module.jmetrics('ads-journal-metrics', proj_home=proj_home, local_config=globals().get('local_config', {}))
logger = app.logger
# ============================= FUNCTIONS ========================================= #
def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def create_metrics(**args):
    # For what year are we creating the metrics?
    year = args['year']
    # Was a specific collection specified?
    collection = args['collection']
    # Were specifics metrics specified?
    metrics = config.get('METRICS')
    if args['metrics']:
        # If metrics were specified, override the default
        metrics = list(set([m.strip().upper() for m in args['metrics'].split(',')]) & set(config.get('METRICS')))
    # Are we overriding the default collection (of everything)?
    if args['collection'] != 'ALL':
        sys.stderr.write('No special collections are defined at this moment\n')
    # Start generating the metrics
    for metric in metrics:
        sys.stderr.write('Generating: {0}\n'.format(metric))
        mod = __import__('jmetrics.metrics', fromlist=[metric.title()])
        class_ = getattr(mod, metric.title())
        instance = class_()
        instance.get_metrics(year)

        
        
