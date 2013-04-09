
# Form Server #

Allows you to quickly serve HTML forms and retrieve responses. Just add a HTML form and a CSV input file.

Use
```
form_server.py --input input.csv run template.html
```
Where the input.csv is a tab-delimited file with all the fields used in your html template file. Where the html file is a html file that servers a form that users can fill in. The form can use [Jinja2](http://jinja.pocoo.org/docs/) syntax and has the variables from a single row in input.csv available. For example, if "url" is a column in the csv file, the html file can contain:
```
<p>{{ url }}</p>
```

You can start the server again without providing a new input file by excluding '--input input.csv' from the command.

After the server has been running a while and results have collected, use
```
form_server.py results results.csv
```
Where the csv file is where you want the results to be saved. The returned results from the html forms will be placed in the csv file.

Both of these commands can optionally use '--db DB_FILENAME', if you want to change the default name of the sqlite db file (db.sqlite).
