Noun Project scraper (obsolete)
===============================

The noun project website has redesigned several times since this was written, and it will assuredly not work anymore.

-----

`The Noun Project <http://thenounproject.com>`_ is excellent, but the experience of downloading and using large numbers of icons from it is poor.  You download a zip file, which you then have to extract, and it has a random ID name rather than a meaningful noun name, and then associating the proper attribution with the icon is a pain.

This simple scraper makes this easier!  Point it at an index file on http://thenounproject.com, and it downloads the icons found on that page.  It:

 * Downloads the .svg
 * Creates a JSON format file with all the metadata associated with it
 * Converts the .svg to .png's in a variety of sizes
 * Formats proper attribution as html.
 * Names everything with the noun for easy file browsing.

Downloads are cached and throttled to a maximum of one every 5 seconds to be
nice, and stay within the terms of use of the website.

Requirements
------------

Relies on `requests <http://docs.python-requests.org/en/latest/index.html>`_, `PIL <http://www.pythonware.com/products/pil/>`_, `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup>`_, `inkscape <http://inkscape.org/>`_ (used in non-gui mode), and a unix-ish command environment (OS X or Linux).

Python dependencies can be installed with::

    pip install -r requirements.txt

Usage
-----

::

    python scrape.py <nounproject index URL> [<more URLs> ...]
 
example::

    python scrape.py http://thenounproject.com/collections/modern-pictograms/

The script will create two directories:

 * `cache`: A cache of html files downloaded from thenounproject.com.  Files will be preferentially used from the cache first, to avoid hitting the server.  If you want to re-download after having run the script, remove this directory and its contents.
 * `icons`: The icons downloaded end up here.  Files are named according to the scheme::

    <noun>-<icon-id>.svg                => the original svg.
    <noun>-<icon-id>.json               => metadata in json format.
    <noun>-<icon-id>-<size>.png         => rasterized icons in png format.
    <noun>-<icon-id>-attribution.html   => attribution in HTML format.

License
-------

Copyright (c) 2012, Charlie DeTar
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
