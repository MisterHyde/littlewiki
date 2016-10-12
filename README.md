DESCRIPTION

A little server using cherrypy to facilitate.
Creates an index file which lists all .rst files in the given directory.
And checks on reload if a .rst file has changed, if yes the html file will be updated.

CONFIGURATION

The self.rstpath is the path where the .rst files lies.
It is possible to store the .rst files in subdirectorys with directorys for pictures, which must be named 'img'.
The self.htmlpath is the path where the .html files resident.
If in the self.htmlpath is a file main.css rst2html will use it to style the pages.

DEPENDENCIES

+ cherrypy
+ python3
+ docutils
