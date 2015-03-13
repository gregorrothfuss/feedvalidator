# Introduction #

AppClientTest is a program for testing your AtomPub service.


# Details #

AppClientTest is a program for testing your AtomPub service. It has been updated to use the AtomPubBase module and also sports HTML output as an option. To make it easier to develop I've transcluded via svn:externals all the libraries you will need as long as you are running Python 2.5. You will need to install elementtree if you are on something older than 2.5. The transcluding means it is this easy to get up and running from svn:

```
$ svn co http://feedvalidator.googlecode.com/svn/trunk/apptestsuite/client/validator/ validator
$ python validator/appclienttest.py --output=results.html "http://bitworking.org/projects/apptestsite/app.cgi/service/;service_document" 
$ firefox results.html
```