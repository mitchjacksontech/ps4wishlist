# PS4 Wish List
A live copy of this application is running at [beta.ps4wishlist.com](https://beta.ps4wishlist.com)
There is a large price discrepency between retailers for the same Playstation 4 games.  I wanted
to build a website where I could check prices on a game, and ask the website to notify me over
email if the game's retail price at any store dropped below an inputted price threshold.

# Work In Progress
So far I've given only a few evenings to this project.  It needs more work to be functionally
useful and reliable

# Please forgive my light documentation
This was a prototyping, lets-learn-python-and-flask project.  I wasn't expecting the code to be seen, or
worked with, by anyone else.  My package documentation is pretty sparse.  Please don't take
this to mean I don't document my code.

# Tech Stack
* [Fedora Linux](https://fedoraproject.org) [Linode](https://linode.com) instance
* [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) through [Apache Web Server](https://apache.org)
* [SQLite](https://www.sqlite.org) with [SQLAlchemy ORM](https://www.sqlalchemy.org)
* [Python3](https://python.org) with the [Flask Microframework](http://flask.pocoo.org)
* Responsive web design using [Bootstrap3](http://getbootstrap.com)'s grid layout

# Database Model
[Object Code for the Database Model](/project/server/models.py)

I would upgrade to MariaDB if this website was going to have any real users.  With
SQLAlchemy, this is as simple as changing the DSN string

# Checking Prices: The real challenge
[Here is prodapi, the price checking module](project/prodapi)

Three quarters of the work on this project went into the price checking modules.
I currently support price lookups to
five different online stores.  Not every product can be succesfully found, and
priced at each store.  In some cases, the checked price is for the wrong product.
I have a design plan to remedy that bug, but it's not yet in place.

Amazon, Best-Buy and Wal-Mart have public APIs for accessing product information.
Target and the Playstation Network store don't. 

## A note on price caching
The TOS for all price APIs require you do not cache pricing information.  Any
prices displayed to an end user must be retrieved live, every time.   Only
basic product information is cacshed in the database,  Prices are live checked.
When viewing a game details page, [like this one for No Man's Sky](https://beta.ps4wishlist.com/game/9),
The prices are checked by javascript after the page has loaded.  Otherwise, the
website would feel very sluggish.  You can watch the price matrix populate over
a second or so after the page renders.

## Amazon Product Advertising API
[Python source prodapi/amazon.py](project/prodapi/amazon.py)

I use the the [Amazon Product Advertising API](http://docs.aws.amazon.com/AWSECommerceService/latest/DG/ItemSearch.html)
extensively in this website.  When a user searches for a game, the search results
are generated via the Amazon API.  The game images and description text are also
provided by amazon.

The game is added to the local database if somebody views it's price details.
At this point, we make note of **the UPC code**, **the ASIN**, and the game's
**full official tital**.

Amazon advertists different prices for prime members, used products, new product,
and other offerings.  Selecting the correct price to display from the dozens the
API returns is an iffy proposition.

## Best Buy
[Python source prodapi/bestbuy.py](project/prodapi/bestbuy.py)

The [Best Buy Developer API](https://developer.bestbuy.com) allows item look-up via **UPC code**.
This is rather straight forward. 

## PSN
[Python source prodapi/psn.py](project/prodapi/psn.py)

The [Playstation Network Store](https://store.playstation.com) is a challenge.  These
are digital copies of the game, not physical.  Sony offers _no official API solution_ to
interact with their information.  But their entire web infrastructure is built on REST
services.  Sniffing the HTTP traffic while browsing their store website reveals
private api urls for search and product services.  These return massive json results.
Using the search API, we make our best guess from the search results which returned
game is the right one.  Then we make note of the **PSN_id**.  We can check the price
easily for this game using it's unique PSN identifier in the future.

## Target
[Python source prodapi/target.py](project/prodapi/target.py)

Target offers a developer API, but they keep it quite private.  I wasn't able to gain
access.  Like with the PSN, I sniffed the HTTP sessions on the target website, and found
the REST service used by the javascript on target.com to populate search results.
By simulating target.com search-box activity requests to [red sky API](https://redsky.target.com),
I perform a title search for the product and, if an appropriate match is found, make a
note of the product's **TCID**, target's internal product identifier.  With the TCID,
we can make other requests to determine the current price.

## Wal-Mart
[Python source prodapi/walmart.py](project/prodapi/walmart.py)

Wal-mart offers [a Developer API](https://developer.bestbuy.com), with search by **UPC**.
