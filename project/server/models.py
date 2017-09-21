# project/server/models.py


import datetime

from project.server import app, db, bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    fave_map = relationship('UserFaves')

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        )
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)

    def faves(self):
        fm = self.fave_map
        if not fm: return
        f = []
        for r in fm: f.append(r.game)
        return f

    def add_fave(self, game_id):
        """ add a game_id as a favorite for this user """
        if self.has_fave(game_id): return
        db.session.add(UserFaves(user_id=self.id,game_id=game_id))
        db.session.commit()

    def del_fave(self, game_id):
        """ rm a game_id as a favorite for this user """
        UserFaves.query.filter_by(
            user_id=self.id,
            game_id=game_id
        ).delete()
        db.session.commit()

    def has_fave(self, game_id):
        """ Return true if user has marked game_id as favorite """
        r = UserFaves.query.filter_by(
            user_id=self.id,
            game_id=game_id
        ).first()
        if r: return True
        return False

class UserFaves(db.Model):

    __tablename__ = "user_faves"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)
    time_stamp = db.Column(db.DateTime, nullable=False)

    user = relationship('User', back_populates='fave_map')
    game = relationship('Game')

    def __init__(self,user_id,game_id):
        self.user_id = user_id
        self.game_id = game_id
        self.time_stamp = datetime.datetime.now()


class Game(db.Model):

    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    upc = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String(255))
    amazon_id = db.Column(db.String(32), nullable=False)
    bestbuy_id = db.Column(db.String(32))
    psn_id = db.Column(db.String(64))
    target_id = db.Column(db.String(32))
    walmart_id = db.Column(db.String(32))

    def __init__(self, prodapi_hash):
        """ create a Game object from a prodapi.amazon lookup """
        p = prodapi_hash

        # Title formatting/repair
        #
        # Strip irrititating title decorators,
        # Add more to this list as we find them
        # (also, py regex can blow goats)
        import re
        regexlist = [
            r'(?: )(?:-)(?: )',
            r'Playstation(?: )4',
            'PS4',
            'Action RPG',
            'Standard Edition',
        ]
        t = p.get('title')
        for r in regexlist:
            regx = re.compile(r, re.IGNORECASE)
            t = regx.sub("",t)

        # drop the ampersand
        t = t.replace('&','and')

        # clean up whitespace
        t = t.strip();

        self.title = t
        self.publisher = p.get('publisher')
        self.upc       = p.get('upc')
        self.img_url   = p.get('img_url')
        self.amazon_id = p.get('store_id')


class GameViewHistory(db.Model):

    __tablename__ = "game_view_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime, nullable=False)
    game_id = db.Column(db.Integer, ForeignKey('games.id'), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)

    user = relationship("User")
    game = relationship("Game", lazy='joined')

    def __init__(self,game_id,user_id=None):
        self.time_stamp = datetime.datetime.now()
        self.game_id = game_id
        if user_id: self.user_id = user_id


class PriceHistory(db.Model):

    __tablename__ = "price_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, ForeignKey('games.id'), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)
    store_id = db.Column(db.String(16))
    time_stamp = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    user = relationship("User")
    game = relationship("Game")
