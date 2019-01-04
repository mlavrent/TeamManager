# Team Manager
This is a web application built with Django that manages a team, currently including purchase request authorizations. Further plans include adding member clock in/out, roster management, and possibly other things. Feel free to leave suggestions!

## Purchase Request App
This is intended to help a team keep track of purchase requests. It comes with the following features:
- Add purchase requests, including name, cost, quantity, and a link to the product
- Notify the person reviewing the requests by email
- Accept/reject purchase requests and notify person in charge of finances by email
- Show a history of past purchase requests

## Installation
I recommend running this application on Heroku. To deploy the app to Heroku:
1. Clone this repository using `git clone https://github.com/MLavrentyev/TeamManager`
2. Run `heroku create <your-app-name>`
3. Add the following config vars (under the settings page of Heroku): `APP_PASS` (your email password), `SECRET_KEY` (the django secret key, can be generated here: https://www.miniwebtool.com/django-secret-key-generator/), and `WEB_CONCURRENCY` (recommended value is 3). `DATABASE_URL` should already be set.
4. Add the host name to `ALLOWED_HOSTS` in /team_manager/settings.py. You may also want to modify the `TIME_ZONE` to match your team's timezone. You can run `pytz.all_timezones` to get a list of acceptable values.
5. Deploy to heroku using `git push heroku master`
6. To create an admin, use `heroku run python manage.py createsuperuser`. Follow the prompts to provide a username, password, and email for the admin.

The app should be located at `<your-app-name>.herokuapp.com`

If this doesn't work, try this additional step:
- Run `heroku run python manage.py migrate`

## Running locally
If you want to run this locally on your machine to do a quick test or for development, follow these steps. Note that you will need to have PostgreSQL installed on your own machine for this to work.
1. Clone this repository using `git clone https://github.com/MLavrentyev/TeamManager`
2. Create a file named `runlocal.sh` in the main project directory. It should contain the following, where the four fields should be filled in with your credentials:
```shell
export APP_PASS='<email password>'
export SECRET_KEY='<django secret key>'
export DB_USER='<database user>'
export DB_PASS='<database password>'

python manage.py runserver
``` 
3. Run `./runlocal.sh` to start your local server.
4. Visit localhost:8000/ to view the site.
