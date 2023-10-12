# GPRO TYRES PREDICTION

#### Video Demo:  <URL HERE>

#### Description: a text-based gaming webapp

## Welcome to my CS50x final project

## The basics

GPRO Tyres Prediction is a webapp, running on Python, HTML/CSS and a JS.

The chosen frameworks are Flask for Pyhton/HTML, and Foundation for CSS and JS. It also incorporates some custom CSS and JS scripts.

## Use and purpose

When the time to start working on my CS50x final project came, I considered a few different projects (like a webapp for cinema tickets purchase). After a few days I
came to realize that I had a particular need that could be fulfilled with a webapp, so my original idea changed and started working on it.

[I am](https://gpro.net/ManagerProfile.asp?IDM=232105) part of a small gaming community around a game (a webapp itself) called [Grand Prix Racing Online](https://gpro.net/). Inside this community, besides the titular game, we have a forum
to communicate with the rest of the players base, where we usually play our own mini-games, making use of the forum functionality. This is where the format of a tyres
prediction game (a game where other players predict what tyre brand the players at the top league, Elite, will be picking for every new season), came to life.

I took over the hosting of the game in the forum for season 8 (GPRO season 88), which was around 10 days after I started CS50. Seasons regularly last 9 weeks, so it gave
me enough time to cover the course's material and develop the project to be launched for season 9 (GPRO season 89). You can find Season 8 forum topic [here](https://gpro.net/forum/ViewTopic.asp?TopicId=30769&PostId=4894592#post4894592)
and the Season 9 forum topic [here](https://gpro.net/forum/ViewTopic.asp?TopicId=30846&PostId=4915260#post4915260)

The objectives of the webapp are:

* To make the predictors experience more comfortable, with options that are more user friendly than Google Forms or other alternatives; without losing the ability to edit
predictions.
* To make my own job as the game's host more comfortable, saving me the task of copy/pasting multiple game entries into a spreadsheet, at the risk of committing several errors
and delivering the game's final standings only several hours after the time of the tyres brand reveal for the season.
* To test the concept/game for the future, exploring player's engagement and scalability; with the idea of perhaps integrating the game to the main game platform/server in a
not so distant future.

## What's inside

The project follows the given format of a Flask project:

* It contains 3 Python files:
_app.py, which has the general setup of the webapp and the scripting for all the routes of the app
_helpers.py, which has the login required and admin only decorators.
_eosscript.py, which contains the script to calculate the game results, which gets called form one of the Admin Only routes.

* 1 layout file and 14 templates loaded by it, HTML + Jinja syntax

* Static folder, containing both framework and own css and js files, plus the logo and favicon for the app.

* SQLITE3 database

* Requirements file

In case the CS50 staff wants to explore the webapp, there's an Admin account set, (Admin for both username and password in the database), with full access to all the features.

## Login, Logout, Register, Settings, Data and Password

These routes and templates help with the setup the user's account. Registration form is very simple; as the game is meant to be played by a very small userbase and
might potentially become a part of the main game, decided not to require the users for an e-mail address and let them choose their own usernames. The process is fast, letting
the player be ready to start in under a minute. After registration, some of the provided inputs can be updated, such as password (password route), their league/group in the game
and also their team (from settings/data route), as those are not fixed (they eventually change with time)

Passwords are hashed for safety, and both Register and Login routes make sure to check for human error and redirect the user in case something goes wrong (wrong password confirmation,
already in use username, etc)

## Select process

### First pick

Once players are logged in for the first time, they'll be automatically redirected to the select form/route. Here they can select the assets, players from the Elite league that will be
picking a tyre brand for the new season. All Elite managers are presented with checkboxes, which the users can select and deselect. For convenience, they have a select all checkbox
and a counter at the bottom to keep track of how many selections they have made. The selections (as per game rules) are limited to 30 out of the 40 elite players, and both validated
through JS and at server level with Python (number of managers and existent ids).

Once the users succeed submitting this form, they are redirected to the Predict form. They can later edit the form (while game status is open)

### Edition

If the user already picked assets, those picks are rendered and set as default values in the form for edition. Attempting submission with closed game status results in a
redirect to index.

## Predict Process

### First pick

All the assets that have been chosen in the select step are rendered at this page, with a selection dropdown menu showing the available tyre brands for the current season. The form is
validated at submission, making sure all the selected assets have an associated tyre, and that the tyre id is valid. Tyre choices can be updated while game status is open.

### Edition

While assets do not change from one edition to the other, they'll appear with their already stored tyre choice as default, so the user can remember which it was. If the asset is no longer
in the pool, the entire database row gets deleted. Otherwise, it only gets updated with whatever the user input and submitted. Attempting submission with closed game status results in a
redirect to index.

## Index page

The page is set to display the current user's predictions and the season standings once those are calculated. If the user has not placed any predictions yet (and game status is open),
they'll be redirected to the selections or predictions routes, depending on what step they are missing. Once season is closed, logged in managers can see season results regardless of
if they sent predictions or not.

## Admin Panel

After considering managing the backend with database edition, I realized my life would be a lot easier if I gave myself an Admin Panel with a few different routes and functions. The
Admin Panel button is placed at the start of the regular menu buttons, subject to user id of the admin profile. All the routes that are part of the Admin panel have a special decorator
that prevents its access even with a direct link to the route.

### Password management

Even when the user base is small, and the eventual integration of the app to the main site, I realized I needed a way to hash a new password to the database for the users to
change later in the eventual case of a forgotten password. This is the only action in the admin panel that might need to be executed more than once a season (9 weeks).

### Tyres for the season

Includes a form that lets the admin input what tyre brands will be available for the assets to pick from for the ongoing season.

### Assets for the season

A form to input the current Elite players for the season. In the eventual case of expanding the game to other leagues, I've introduced the league field in several other places of the
database, so a change can be easily implemented without affecting older seasons.

### Season's tyres choices

A form to select and input to the database what is the actual tyre brand that the assets picked. It's a once a season task performed after the Race 1 Qualy deadline.

### Manage game status

After the deadline, there's an immediate need to set the game's status to closed, as that prevents users to keep sending predictions (where the tryre brand picks have
already been revealed). Here is where the close button comes to play.

There's (hopefully) a short twilight period between the closing and the input of the actual tyres choices and results calculation.

When a new season arrives, admin can input it in the provided form field. It not only adds a row to the database, but sets new season current status to True, and sets previous season
current status to false.

Once the season has the assets and the tyre brands input and ready to go, the open button can be used so the game starts taking in predictions.

### Calculate season results

It's an action button that executes the end of season calculation script. Once it's done, the season's final standings are available to be displayed at the index.

## Some web design considerations

I opted for a simple design, with some pops of GPRO brand color, using a slightly customized stylesheet from [Foundation framework](https://get.foundation/), where I changed some
colors to match the theme, plus a few custom classes added in my own stylesheet. Designed a basic logo using a stock tyre image from [PNG Item](https://pngitem.com) (free for personal use)
and [Anton Google Font](https://fonts.google.com/specimen/Anton), which I also used for some of the titles/headers in others places of the app.

The navigation bar combines different elements from Foundation too, mainly some of the responsive navigation classes.

Chose to add a countdown to tyres reveal clock close to the navbar, to the effects of directing the attention of the users to how much time they have left to place their predictions, but
also for some dramatic effect. Credit for most of the clock code to [W3SCHOOLS](https://www.w3schools.com/). This and the other custom JS scripts also had a lot of influence and assistance
from [MDN Web Docs](https://developer.mozilla.org/en-US/about) and [Stack Overflow](https://stackoverflow.com/).

## Deployment and production

As the idea behind was giving the project immediate use, once the main functionality was resolved, I deployed the project on Heroku. It can be found at [this link](https://tyres-prediction-game.herokuapp.com/).

I started coding the project August 4th, 2022 using the provided CS50 codespace; knowing the next tyres reveal at [GPRO](https://gpro.net/) would be August 19th. By August 9th
I had the webapp deployed and some beta testers playing with it, using the already finished season data as example. On the 12th the actual GPRO season was over, so I input part of
the data for S89, which I finished doing on the 13th once I had confirmation that the tyres brands for the season would be the same as the previous one. The webapp has been in
actual production since that day and waiting for showtime on the 19th (hopefully the day I submit my project).

The only differences from the version I am submitting are the small modifications I had to introduce to meet the Heroku requirements (as Heroku works with PostgreSQL and Gunicorn,
for example). I appreciate and thank the [Heroku Deployment Guide](https://cs50.readthedocs.io/heroku/) the CS50 Staff put together so generously. And perhaps an easteregg or 2
I prepared for the regular players :upside_down_face:, it's a game after all :slightly_smiling_face:.

## Beta and Test in Production

Debugging is no easy task, but I had the privilege of being able to hold a short (and, granted, small too) beta for the app. I caught a couple of big bugs during it (some checks I was not
doing at the select and predict routes, plus a problem with the index route because I had forgotten to condition some of the redirections to the season being open), and also became aware
of the need of some custom js scripts that made user's life easier (such as showing a count of the current selections, a select all checkbox, among others).

During the test in production stage, I worked a bit extra on removing some hardcoded values (like the season), thinking of the seasons to come; which I was not too concerned about when I
first deployed the app (wanted to be sure the main features were functional).

## Future and scalability

The database structure is prepared for 2 eventualities:
*Having predictions for more leagues besides Elite
*That the tyre brand variety is different depending on the league.

The code would need some adjustments if/when this happens, but the database would be fully usable and old season data could be retrieved in case it's needed with no foreseeable issues.

Adding more leagues is probably something I'll be looking into in a season or 2 from launching; the tyres variety is purely preventive and there's no indication the circumstance may arise
in the near future.

The case where I am able to host the game in the main game servers is the more challenging one, and would require to re-think most of the code; starting for the fact that the users would be
logged in to the game using the main game login. That alone eliminates the registration process. It also allows more integration features, like automatically taking the assets and tyres data
from the game server upon season start. Some of the base of the code and the concept would be the same, but it'd become a different app all around. I'm still willing to further my learning
and take such challenge if the opportunity arises.
