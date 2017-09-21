"""
prodapi.bestbuy
Look up ps4 games via the bestbuy products api

BESTBUY_API_KEY is a required environment variable

result = ProductByUPC(upc)
"""

import os
import json
import logging
from urllib.request import urlopen


def ProductByUPC(upc):
    url = "%s(upc=%s&(categoryPath.id=%s))?apiKey=%s&format=json" % (
        config['BESTBUY_API_URL'],
        upc,
        config['BESTBUY_CATEGORYPATH'],
        config['BESTBUY_API_KEY'] ,
        )
    logging.info("Fetch URL: %s" % url)
    response = urlopen(url)
    data     = response.read().decode("utf-8")
    result   = json.loads(data);

    if ( 'products' in result ) and ( result['products'] ):
        return __result_to_hash(result['products'][0])

    return None


def __result_to_hash(r):
    return {
        "store_id"     : r.get('productId'),
        "upc"          : r.get('upc'),
        "title"        : r.get('name'),
        "publisher"    : r.get('manufacturer'),
        "sale_price"   : str(r.get('salePrice')).replace(".",""),
        "retail_price" : str(r.get('regularPrice')).replace(".",""),
        "store_url"    : r.get('url'),
        "img_url"      : None,
    }


def __setconfig():
    """ Find bestbuy API access tokens in the unix environment """

    # only load config once
    if 'BESTBUY_API_KEY' in config:
        return None;

    config['BESTBUY_API_KEY'] = os.getenv('BESTBUY_API_KEY')
    if not config['BESTBUY_API_KEY']:
        raise EnvironmentError("Please set BESTBUY_API_KEY environment variable")

    config['BESTBUY_API_URL'] = os.environ.get(
        'BESTBUY_API_URL',
        'https://api.bestbuy.com/v1/products'
    )
    config['BESTBUY_CATEGORYPATH'] = os.environ.get(
        'BESTBUY_CATEGORYPATH',
        'pcmcat295700050012'
    )


config = {}
__setconfig()
