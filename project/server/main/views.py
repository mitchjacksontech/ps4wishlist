# project/server/main/views.py


#################
#### imports ####
#################
import logging

from flask import (
    abort,
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct

from project.server import db
from project.server.models import Game, GameViewHistory


################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)
logger = logging.getLogger('log')



@main_blueprint.route('/')
def home():

    # Grab a distinct list of recently viewed games for display
    rg = []

    # doesn't product distinct :-/
    #r = GameViewHistory.query.distinct('game_id').limit(6)
    q = GameViewHistory.query
    # distinct is not supported in sqlite btw
    q = q.distinct(GameViewHistory.game_id)
    q = q.order_by(GameViewHistory.time_stamp.desc())
    q = q.limit(10)
    r = q.all()

    for g in r: rg.append(g.game)

    return render_template('main/home.html',recent_games=rg)


@main_blueprint.route("/about/")
def about():
    return render_template("main/about.html")


@main_blueprint.route("/search", methods=['GET','POST'])
def search():

    games = []
    if request.method == 'POST' and request.form.get('search_text'):
        from project.prodapi.amazon import ProductSearch
        games = ProductSearch(request.form['search_text'],ResultLimit=15)

    return render_template('main/search.html',games=games)


@main_blueprint.route("/game/find")
def find_game():
    """ Load a show_game page from an asin """
    # 404 if we aren't passed an asin
    asin = request.args.get('asin')
    logger.critical("Found asin as '%s'" % asin )
    if not asin: abort(404)

    # Try to load game from database
    game = Game.query.filter(Game.amazon_id == asin).first()

    # If we can't find the game in the database, create a new
    # datbase record
    if not game:
        from project.prodapi.amazon import ProductById
        r = ProductById(asin)

        # If we still can't do a lookup using the asin either,
        # throw an error
        if not r:
            logger.info("Unable to search amazon for asin '%s'" % asin)
            abort(404)

        # Add this game to our database
        game = Game(r)
        db.session.add(game)
        db.session.commit()

    return redirect(url_for('main.show_game',game_id=game.id))


@main_blueprint.route("/game/<int:game_id>")
def show_game(game_id):
    game = Game.query.get(game_id)
    if not game: abort(404)

    # Log this game view
    gvh = GameViewHistory(game_id=game_id)
    db.session.add(gvh)
    db.session.commit()

    stores = [
        { "title" : "Amazon", "shortname" : "amazon", "id" : game.amazon_id },
        { "title" : "Best Buy", "shortname" : "bestbuy", "id" : game.bestbuy_id },
        { "title" : "PSN", "shortname" : "psn" , "id" : game.psn_id },
        { "title" : "Target", "shortname" : "target", "id" : game.target_id },
        { "title" : "Wal-Mart", "shortname" : "walmart", "id" : game.walmart_id },
        #{ "title" : "Gamestop", "shortname" : "gamestop" },

    ]

    return render_template("/main/show_game.html", game=game, stores=stores)
