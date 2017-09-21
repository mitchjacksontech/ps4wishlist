"""
result = ProductByUPC(upc)
"""

import os
import json
import logging
from urllib.request import urlopen
from urllib.error import HTTPError

def ProductByUPC(upc):
    url = 'https://api.walmartlabs.com/' + \
          'v1/' + \
          'items' + \
          '?apiKey=%s' % config['WALMART_API_KEY'] + \
          '&upc=%s' % upc;
    logging.info("Fetch URL: %s" % url)

    try:
        response = urlopen(url)
        data     = response.read().decode("utf-8")
        result   = json.loads(data);
    except HTTPError as e:
        # Searches return 404 if not found
        if e.code == 404:
            return None
        else:
            raise
    except:
        raise

    if ( 'items' in result ) and ( result['items'] ):
        return __result_to_hash(result['items'][0])

    return None


def __result_to_hash(r):
    """ Convert a walmart api data structure to standard prodapi hash """
    return {
        "store_id"     : r.get('itemId'),
        "upc"          : r.get('upc'),
        "title"        : r.get('name'),
        "publisher"    : r.get('brandName'),
        "sale_price"   : str(r.get('salePrice')).replace(".",""),
        "retail_price" : str(r.get('msrp')).replace(".",""),
        "store_url"    : r.get('productUrl'),
        "img_url"      : r.get('largeImage'),
    }


def __setconfig():
    """ find walmart developer api key in environment, or die """

    if 'WALMART_API_KEY' in config:
        return None

    config['WALMART_API_KEY'] = os.environ.get('WALMART_API_KEY')
    if not config['WALMART_API_KEY']:
        raise EnvironmentError("Please set WALMART_API_KEY environment variable")



config = {}
__setconfig()
