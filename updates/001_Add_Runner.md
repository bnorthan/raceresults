## Adding a new model

To add a new model I had to modify the following

1.  Add Runner to models
2.  Add views to list all runners, and results for a runner.
3.  Add html template to show list of all runners and results for one
runner.
4.  Add path and urls for runners and runner to urls.py
5.  Add Runner to admin.py so we can edit/delete them using the admin
interface.
6.  Generate the migrations (note the migrations may not be clean,
    because as developing the app and learning I've been deleting
    migrations in a somewhat ad-hoc way).
    
    
See https://github.com/bnorthan/raceresults/commit/d11730c45e9035698a4fe5ce83b21c144cde39c7
