"""
result = ProductById(psn_id)
result = ProductByTitle(title)
"""

import logging
import json
from urllib.request import urlopen
from urllib.error import HTTPError


def ProductById(psn_id):
    """ Fetch a hash of infomration about a psn_Id """
    url = "https://store.playstation.com/" + \
          "chihiro-api/" + \
          "viewfinder/" + \
          "US/" + \
          "en/" + \
          "999/" + \
          "%s" % psn_id + \
          "?size=30" + \
          "&gkb=1" + \
          "&geoCountry=US"

    try:
        logging.info("Fetch URL: %s" % url)
        response = urlopen(url)
        data     = response.read().decode("utf-8")
        result   = json.loads(data);
        if ( 'default_sku' in result ) and ( result['default_sku'] ):
            return __result_to_hash(result)
    except HTTPError as e:
        if e.code == 404:
            return None
        else:
            raise
    except: raise

    return None


def ProductByTitle(title):

    # I'm hijacking the ajax api call of the
    # game search box on store.playstation.com.

    # they translate spaces to underscores in
    # queried search strings
    title = title.replace(' ','_')

    # they seem to remove apostrophies
    title = title.replace("'","")

    # I haven't found this documented anywhere
    # easily searchable.  I did find a nifty
    # place... psdevwiki.com.  If I can pick
    # apart these parameters, I'll post the
    # details there
    url = "https://store.playstation.com/" + \
          "store/"     + \
          "api/"       + \
          "chihiro/"   + \
          "00_09_000/" + \
          "tumbler/"   + \
          "US/"        + \
          "en/"        + \
          "999/"       + \
          "%s" % title + \
          "?suggested_size=5" + \
          "&mode=game";

    logging.info("Fetch URL: %s" % url)
    response = urlopen(url)
    data     = response.read().decode("utf-8")
    result   = json.loads(data);

    if ( 'links' in result ) and ( result['links'] ):
        return __result_to_hash(result['links'][0])

    return None


def __result_to_hash(r):
    """ Convert a psn searchbox search to standard prodapi hash """
    g = {
        "store_id"     : r.get('id'),
        "upc"          : None,
        "title"        : r.get('name'),
        "publisher"    : r.get('provider_name'),
        "retail_price" : r['default_sku']['price'],
        #"store_url"    : r.get('url'),
        "img_url"      : None,
    }

    # Set price from 'bonus_price' if it's there
    # or Set Price from rewards price if it's there
    # else use retail price
    #
    #r['default_sku']['rewards'][0]['bonus_price']
    # do you have it? aka more ways python is dumb
    if ( 'default_sku' in r \
         and 'rewards' in r['default_sku'] \
         and len(r['default_sku']['rewards']) > 0 \
        ):
        if 'bonus_price' in r['default_sku']['rewards'][0]:
            g["sale_price"] = r['default_sku']['rewards'][0]['bonus_price']
        elif 'price' in r['default_sku']['rewards'][0]:
            g["sale_price"] = r['default_sku']['rewards'][0]['price']
    else:
        g["sale_price"] = g.get("retail_price")

    # https://store.playstation.com/#!/en-us/games/foo/cid=<id>
    # Build Store URL
    g['store_url'] = "https://store.playstation.com/#!/en-us/games/perimus/cid=%s" % r.get('id')

    return g
