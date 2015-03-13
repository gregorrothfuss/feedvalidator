# Introduction #

How to install Apexer

# Prerequisites #

Apexer depends on `httplib2`, which you can get from [here](http://code.google.com/p/httplib2/).

# Details #

```
$ svn checkout http://feedvalidator.googlecode.com/svn/trunk/apptestsuite/client/
$ cd client
$ python setup.py install
```

On a system you don't have root on you can install `apexer` locally:

```
$ python setup.py install --prefix=$HOME
```