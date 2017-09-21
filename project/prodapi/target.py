"""
result = ProductByTitle(title)
result = ProductById(tcin)
"""

import json
import logging
from urllib.request import urlopen

def ProductByTitle(title):

    # I'm hijacking the ajax api call of the
    # search results page on target.com

    # they translate spaces to underscores in
    # queried search strings into +
    title = title.replace(' ','+')

    # online json viewer was blocked from Searching
    # this api.  Possible we'll get blocked too.
    # Let's find out!

    # category      = 5xtg5   # Video Games
    # faceted_value = 55jy8   # PS4
    url = "http://redsky.target.com/" + \
          "v1/"                 + \
          "plp/"                + \
          "search"              + \
          "?keyword=%s" % title + \
          "&count=24"           + \
          "&offset=0"           + \
          "&category=5xtg5"     + \
          "&sort_by=relevance"  + \
          "&faceted_value=55jy8"

    logging.info("Fetch URL: %s" % url)
    response = urlopen(url)
    data     = response.read().decode("utf-8")
    result   = json.loads(data);

    # ( this garbage is a recommended pattern for a
    #   complex conditional.  also why im not a python fan )
    if      ('search_response' in result ) \
        and ('items'           in result['search_response'] ) \
        and ('Item'            in result['search_response']['items'] ) \
        and (result['search_response']['items']['Item']):
        return __result_to_hash(result['search_response']['items']['Item'][0]);

    return None


def ProductById(tcin):
    """ Search target using the tcid """
    # Target uses the same search function for text serch and id search
    return ProductByTitle(tcin)


def __result_to_hash(r):
    """ Convert target api results to standard prodapi hash """
    return {
        "store_id"     : r.get('tcin'),
        "upc"          : r.get('upc'),
        "title"        : r.get('title'),
        "publisher"    : r.get('brand'),
        "sale_price"   : str(r['offer_price']['price']).replace(".",""),
        "retail_price" : str(r['list_price']['price']).replace(".",""),
        "store_url"    : "http://www.target.com/p/-/-/A-%s" % r.get('tcin'),
        "img_url"      : None,
    }
