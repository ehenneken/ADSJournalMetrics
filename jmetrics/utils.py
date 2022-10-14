import re
import os
import sys
import urllib.request, urllib.parse, urllib.error
import requests
import math
from datetime import date
# ============================= INITIALIZATION ==================================== #

from adsputils import setup_logging, load_config

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
config = load_config(proj_home=proj_home)
logger = setup_logging(__name__, proj_home=proj_home,
                        level=config.get('LOGGING_LEVEL', 'INFO'),
                        attach_stdout=config.get('LOG_STDOUT', False))
# =============================== HELPER FUNCTIONS ================================ #
def _group(lst, n):
    """
    Transform a list of values into a list of tuples of length n
    
    param: lst: the input list
    param: n: tuple length
    """
    for i in range(0, len(lst), n):
        val = lst[i:i+n]
        if len(val) == n:
            yield tuple(val)

def _make_dict(tup, key_is_int=False):
    """
    Turn list of tuples into a dictionary
    
    param: tup: list of tuples
    param: key_is_int: keys of dictionary will be integers if true
    """
    newtup = tup
    if key_is_int:
        newtup = [(int(re.sub("[^0-9]", "", e[0])), e[1]) for e in tup]        
    return dict(newtup)

def _do_query(conf, params):
    """
    Send of a query to the ADS API (essentially, any API defined by config values)
    
    param: conf: dictionary with configuration values
    param: params: idctionary with query parameters
    """
    headers = {}
    headers["Authorization"] = "Bearer:{}".format(conf['ADS_API_TOKEN'])
    headers["Accept"] = "application/json"
    url = "{}/search/query?{}".format(conf['ADS_API_URL'], urllib.parse.urlencode(params))
    r_json = {}
    try:
        r = requests.get(url, headers=headers)
    except Exception as err:
        logger.error("Search API request failed: {}".format(err))
        raise
    if not r.ok:
        msg = "Search API request with error code '{}'".format(r.status_code)
        logger.error(msg)
        raise Exception(msg)
    else:
        try:
            r_json = r.json()
        except ValueError:
            msg = "No JSON object could be decoded from Search API"
            logger.error(msg)
            raise Exception(msg)
        else:
            return r_json
    return r_json

# =============================== DATA RETRIEVAL FUNCTIONS ==================== #

def _get_facet_data(conf, query_string, facet):
    """
    Do an ADS API facet query
    
    param: conf: dictionary with configuration values
    param: query_string: the query string to execute pivot query on
    param: facet: the facet to return
    """
    params = {
        'q':query_string,
        'fl': 'id',
        'rows': 1,
        'facet':'on',
        'facet.field': facet,
        'facet.limit': 1000,
        'facet.mincount': 1,
        'facet.offset':0,
        'sort':'date desc'
    }
    data = _do_query(conf, params)
    results = data['facet_counts']['facet_fields'].get(facet)
    # Return a dictionary with facet values and associated frequencies
    return _make_dict(list(_group(results, 2)))