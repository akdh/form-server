
# Form Server #

Allows you to quickly serve HTML forms and retrieve responses. Just add a HTML form and a CSV input file.

Use
```
form_server.py input input.csv "ID_STRING" table.sqlite
```
Where the input.csv is a tab-delimited file with all the fields used in your html file (see below) and the sqlite file is where the results will be stored (does not have to be created). ID_STRING is a [Jinja2](http://jinja.pocoo.org/docs/) formatted string that is unique for each row in input.csv.

Then use
```
form_server.py run template.html table.sqlite
```
Where the html file is a html file that servers a form that users can fill in. The form can use [Jinja2](http://jinja.pocoo.org/docs/) syntax and has the variables from a single row in input.csv available. For example, if "url" is a column in the csv file, the html file can contain:
```
<p>{{ url }}</p>
```

The sqlite file is the same as in the first line.

Finally, after the server has been running a while and results have collected, use
```
form_server.py results results.csv table.sqlite
```
Where the csv file is where you want the results to be saved and the sqlite file is the same as the previous two commands. The returned results from the html forms will be placed in the csv file.
