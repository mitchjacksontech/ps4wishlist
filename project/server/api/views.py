# project/server/api/views.py

#---------------------------------
# imports
#---------------------------------
import logging

from flask import (
    abort,
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from project.server import db, logger
from project.server.models import Game


#---------------------------------
# config
#---------------------------------
api_blueprint = Blueprint('api', __name__)


#---------------------------------
# views:
#  favorites management
#
#  /api/fave/add/<game_id>
#  /api/fave/del/<game_id>
#---------------------------------
@api_blueprint.route('/api/fave/add/<int:game_id>')
def api_add_fave(game_id):
    """ Add game_id to the user favorites """

    if not current_user.is_authenticated: abort(401)

    g = Game.query.get(game_id)
    if not g: abort(400)

    current_user.add_fave(game_id)
    return jsonify("success")


@api_blueprint.route('/api/fave/del/<int:game_id>')
def api_del_fave(game_id):
    """ Rm game_id from user favorites """

    if not current_user.is_authenticated: abort(401)
    current_user.del_fave(game_id)
    return jsonify("success")


#---------------------------------
# views:
#  Update the stored store_id for a game
#  !requres administrative privileges!
#
#  /api/setstoreid/<store_name>/<game_id>
#  POST: store_id: <id>
#---------------------------------
@api_blueprint.route('/api/setstoreid/<store_name>/<int:game_id>/<store_id>')
def api_set_store_id(store_name,game_id,store_id):
    """ Update store_id for a game """

    if not current_user.admin: abort(401)

    g = Game.query.get(game_id)
    if not g: abort(400)

    setattr(g,store_name+'_id',store_id)
    db.session.commit()
    return jsonify("success")


#---------------------------------
# views:
#  price checks
#
#  /api/price/<store_name>/<game_id>
#  /api/price/<store_name>/<game_id>/<store_id>
#---------------------------------
@api_blueprint.route('/api/price/<store_name>/<int:game_id>', defaults={'store_id':None})
@api_blueprint.route('/api/price/<store_name>/<int:game_id>/<store_id>')
def api_price_from_game_id(store_name,game_id,store_id):
    """ Return jsn object with price information """
    game = Game.query.get(game_id)
    if not game:
        logger.warning("Unable to load game for game_id(%s)" % game_id)
        abort(404)

    # don't just concat store_name into a function name
    # even though it would be simpler
    rf = {
        'amazon'   : __api_price_amazon,
        'bestbuy'  : __api_price_bestbuy,
        'psn'      : __api_price_psn,
        'target'   : __api_price_target,
        'walmart'  : __api_price_walmart,
    }
    if store_name in rf:
        pricecheck = rf[store_name](game)
        if pricecheck is not None:
            logger.info("Price check for game %s" % game.title)
            logger.info("Retail Price: %s" % pricecheck.get('retail_price'))
            logger.info("Sale Price: %s" % pricecheck.get('sale_price'))
        else:
            logger.info("Failed Price Check %s/%s" % (store_name,game_id))
        return jsonify(pricecheck)
    else:
        logger.warning("store_name not supported (%s)" % store_name)
        abort(404)


def __api_price_amazon(game):
    from project.prodapi.amazon import ProductById
    return(ProductById(game.amazon_id))


def __api_price_bestbuy(game):
    from project.prodapi.bestbuy import ProductByUPC
    if game.bestbuy_id:
        # todo implement ProductById in prodapi.bestbuy
        return(ProductByUPC(game.upc))
    else:
        r = ProductByUPC(game.upc)
        if 'store_id' in r:
            game.bestbuy_id = r['store_id']
            db.session.add(game)
            db.session.commit()
        return(r)


def __api_price_psn(game):
    if game.psn_id:
        from project.prodapi.psn import ProductById
        return(ProductById(game.psn_id))
    else:
        from project.prodapi.psn import ProductByTitle
        r = ProductByTitle(game.title)
        if r is not None and 'store_id' in r and r['store_id']:
            game.psn_id = r['store_id']
            db.session.add(game)
            db.session.commit()
        return(r)


def __api_price_target(game):
    if game.target_id:
        from project.prodapi.target import ProductById
        return(ProductById(game.target_id))
    else:
        from project.prodapi.target import ProductByTitle
        r = ProductByTitle(game.title)
        if r is not None and 'store_id' in r and r['store_id']:
            game.target_id = r['store_id']
            db.session.add(game)
            db.session.commit()
        return(r)


def __api_price_walmart(game):
    # todo implement ProductById in walmart api
    from project.prodapi.walmart import ProductByUPC
    if game.walmart_id:
        return(ProductByUPC(game.upc))
    else:
        r = ProductByUPC(game.upc)
        if r is not None and 'store_id' in r and r['store_id']:
            game.walmart_id = r['store_id']
            db.session.add(game)
            db.session.commit()
        return(r)


#@api_blueprint.route('/api/price/<store_name>/<int:game_id>/<store_id>')
#def api_price_from_store_id(store_name,game_id,store_id):
#    return 1;
