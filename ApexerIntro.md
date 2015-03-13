# Introduction #

Apexer is the Atom Publishing Protocol Exerciser, a command line tools that gets installed with the [`atompubbase`](AtomPubBase.md) Python library. It allows you to interact with an Atom Publishing Protocol service via the command line, including manipulating media entries.

# Installation #

See ApexerInstall.

# Overview #

Apexer is a command line tool that has the same 'sub-command' type of interface as subversion. If you run `apexer help` you will get a list of sub-commands that you can use. You can then get help for each sub-command, for example:
```
$ apexer help service
service: Set the service document to work from.
usage: service [URI]

  Sets the service document to be the one located at URI.


options:
  -s SESSION, --session=SESSION
                        A file for the session state.
  -d CREDENTIALS, --credentials=CREDENTIALS
                        File containing credentials. The file must contain a
                        username on one line and the password on the next.
  -c CACHE, --cache=CACHE
                        Directory to store the HTTP cache in.
  -r, --raw             Print the raw response body received.
  -i, --include         Print the HTTP headers received.
```

Apexer is a modal program, that is, it remembers where you were the next time you run the program. As you interact with an Atom Publishing Protocol (AtomPub) service you will move down from the Service Document to a Collection and finally to working with an individual Entry. The current Service Document, Collection and Entry are saved by `apexer` and remembered the next time the program is run. That information is the Session State and it is looked for in the following places (and in the following order):

```
   - command line argument
   - $APEXER_CMD_LINE_SESSION
   - $HOME/.apexer/session
```

# Example #

Let's walk through a simple example of using `apexer`. We start at the Service Document:
```
apexer service "http://bitworking.org/projects/apptestsite/app.cgi/service/;service_document"
```

Note that we didn't give it a session file, and I haven't defined the environment variable `APEXER_CMD_LINE_SESSION` so the session file will be store in `$HOME/.apexer/session`, and will be created if not present.

I can now get a list of all the collections supported at that service:

```
$ apexer lc
0   entry
1   draft
2   trash
3   media
4   trash
```

Use the `collection` sub-command to choose which collection you want to work with:

```
$ apexer collection 0
```

Use `ls` to get a list of the entries in the 'entry' collection.

```
$ apexer ls
0   Test Post From AtomPubBase Live Test
1   untitled
2   untitled
3   a test of atomic
4   test fude
5   Pgla
6   Something spooky happened today
7   None
8   Hello from Atomic
9   More
```

By default `ls` will only give the last 10 entries, use `--all` to see them all. Select an entry to work with and then retrieve a copy of that entry:

```
$ apexer entry 3
$ apexer get
```

If you don't supply a file name to `get` then it stores the entry in a file named 'entry'.

```
$ cat entry
<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
     <title>a test of atomic</title>
     <link href="http://bitworking.org/news/18/a-test-of-atomic" />
     <id>http://bitworking.org/news/18/a-test-of-atomic</id>
     <author>
        <name>Joe Gregorio</name>
     </author>
     <updated>2007-12-12T11:39:18.951001-04:00</updated>
     <app:edited>2007-12-12T11:39:18.951001-04:00</app:edited>
     <summary type="xhtml">
          <div xmlns="http://www.w3.org/1999/xhtml">just testing...</div>
     </summary>
     <link href="." rel="edit" />
         <content type="xhtml">
              <div xmlns="http://www.w3.org/1999/xhtml"><p>Enter some text here.blubb</p></div>
         </content>
</entry>
```

We can now edit that entry in a text editor and to update it we use the `put` subcommand:

```
$ vim entry
$ apexer put
```

Again, if no file name is given then `put` looks for a file named 'entry'. You can remove that entry from the collection via `delete`.

```
$ apexer delete
$ apexer ls
0   Test Post From AtomPubBase Live Test
1   untitled
2   untitled
3   test fude
4   Pgla
5   Something spooky happened today
6   None
7   Hello from Atomic
8   More
```

The contents of the entry are left in the file 'entry'.

You can use the sub-command `create` to create a new entry in the collection.

```
$ apexer create entry --content-type="application/atom+xml"
$ apexer ls
0   a test of atomic
1   Test Post From AtomPubBase Live Test
2   untitled
3   untitled
4   test fude
5   Pgla
6   Something spooky happened today
7   None
8   Hello from Atomic
9   More
```

## Media Collections ##

You work with media collections in the same exact way, using the `getmedia` and `putmedia` sub-commands. For these commands if a local file name is not given the name 'media' is used.

```
$ apexer lc
0   entry
1   draft
2   trash
3   media
4   trash

$ apexer collection 3
$ apexer ls
0   None
1   Creek
2   None
3   None
4   None
5   None
6   None
7   None
8   None
9   None

$ apexer entry 1
$ apexer get
$ cat entry
<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
     <title>Creek</title>
     <link href="http://bitworking.org/news/416/Creek" />
     <id>http://bitworking.org/news/416/Creek</id>
     <author>
        <name>Joe Gregorio</name>
     </author>
     <updated>2008-01-06T22:56:12.851899-04:00</updated>
     <app:edited>2008-01-06T22:56:12.851899-04:00</app:edited>
     <summary type="xhtml">
          <div xmlns="http://www.w3.org/1999/xhtml" />
     </summary>
     <link href="." rel="edit" />
         <link href=";media" rel="edit-media" />
         <content src="http://bitworking.org/images/dev/416-Creek.jpe" type="image/jpeg" />
</entry>

$ apexer getmedia creek.jpeg
$ gimp creek.jpeg
$ apexer putmedia creek.jpeg
```