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
3. You will also need to add the py_trgm. To do this:
  - run `heroku pg:psql` to connect to the database on heroku
  - run `CREATE EXTENSION pg_trgm;` to add the extension
  - check that it was in fact added by running `\dx`. You should see py_trgm listed.
  - that's it! you can exit using `\q`.
4. Deploy to heroku using `git push heroku master`
5. To create an admin, use `heroku run python manage.py createsuperuser`. Follow the prompts to provide a username, password, and email for the admin.

The app should be located at `<your-app-name>.herokuapp.com`

If this doesn't work, try this additional step:
- Run `heroku run python manage.py migrate`

