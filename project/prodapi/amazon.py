"""
r = ProductSearch(Title,ResultLimit=n)
r = ProductById(asin)
r = ProductByUPC(upc)

"""
import sys, os
from amazon.api import AmazonAPI, SearchException, AsinNotFound


def ProductSearch(
    Title,
    SearchIndex="VideoGames",
    Platform="Playstation 4",
    ResultLimit=1,
    ):
    """ Pass a search string to get the first match from search results """

    # Try a search by title
    # if that returns no results, try a search by keyword
    try:
        results = amazon.search_n(
            ResultLimit,
            Title=Title,
            SearchIndex=SearchIndex,
            #Platform=Platform,
        )

        # only return results if
        # ProductTypeName is CONSOLE_VIDEO_GAMES or DOWNLOADABLE_VIDEO_GAME

        # lines like this make me hate python even more
        filtered_results = []
        for i, p in enumerate(results):

            # limit our results to ResultLimit
            if filtered_results.count == ResultLimit:
                break;

            # Blacklist
            # Filter out results containing these keywords
            skip = False # another crap hack because this bs http://www.python.org/dev/peps/pep-3136/
            bl = ['SEASON PASS','Season Pass','season pass','dlc','DLC','Expansion Pass','Digital Code']
            for b in bl:
                if b in p.title:
                    skip = True
            if skip: continue

            if (
                p.get_attribute('ProductTypeName') in ('CONSOLE_VIDEO_GAMES','DOWNLOADABLE_VIDEO_GAME')
                and p.get_attribute('Platform') == 'PlayStation 4'
                ):
                filtered_results.append(__result_to_hash(p))
        if filtered_results:
            return filtered_results
        else:
            return None
    except SearchException:
        return None
    except:
        raise


def ProductById(item_id):
    """  Pass an amazon item_id to return a hash of product details """
    try:
        ProductObj = amazon.lookup(ItemId=item_id)
        if ProductObj:
            return __result_to_hash(ProductObj)
        else:
            return None
    except AsinNotFound:
        return None
    except:
        raise



def ProductByUPC(upc):
    """
    Return an item, or a list of items, matching the
    supplied UPC from amazon
    """
    try:
        r = amazon.lookup(
            IdType='UPC',
            ItemId=upc,
            SearchIndex="VideoGames",
        )
        if r:
            return __result_to_hash(r[0])
    except AsinNotFound:
        return None
    except:
        raise


# def ProductByName(name):
#     try:
#         results = amazon.lookup(name=name)
#     except:
#         raise


def XmlById(item_id):
    """
    Pass an amazon item_id to return the full xml of the amazon api response
    """
    try:
        ProductObj = amazon.lookup(ItemId=item_id)
        return ProductObj.to_string()
    except AsinNotFound:
        raise
    except:
        raise


# def ProductObjById(item_id):
#     """ Return an amazon.api product lookup object """
#     from amazon.api import AsinNotFound
#     try:
#         ProductObj = amazon.lookup(ItemId=item_id)
#         return ProductObj
#     except AsinNotFound:
#         return None
#     except:
#         raise


def __result_to_hash(r):
    """ Transform an amazon product object to a prodapi hash """
    rh = {
        "store_id"     : r.asin,
        "upc"          : r.upc,
        "title"        : r.title,
        "publisher"    : r.publisher,
        "sale_price"   : str(r.price_and_currency[0]).replace(".",""),
        "retail_price" : str(r.list_price[0]).replace(".",""),
        "store_url"    : r.offer_url,
        "img_url"      : r.large_image_url,
    }
    if rh['sale_price'] == "None": rh['sale_price'] = rh['retail_price']
    return rh



def __setconfig():
    """ Find amazon API access tokens in the unix environment """
    # only load config once
    if 'AMAZON_SECRET_KEY' in config:
        return None;

    kvals = ['AMAZON_ACCESS_KEY', 'AMAZON_SECRET_KEY', 'AMAZON_ASSOC_TAG']

    for k in kvals:
        config[k] = os.getenv(k)
        if not(config.get(k,None)):
            raise EnvironmentError("Please set %s environmet variable" % k)



# Prepare module for use by
# * Load amazon developer credentaials from environemnt variables
# * Instantiate an amazon api object
config = {}
__setconfig()
amazon = AmazonAPI(
    config['AMAZON_ACCESS_KEY'],
    config['AMAZON_SECRET_KEY'],
    config['AMAZON_ASSOC_TAG'],
)
