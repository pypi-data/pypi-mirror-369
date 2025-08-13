.. _quickstart:

Quickstart
==========

.. module:: niquests.models

Eager to get started? This page gives a good introduction in how to get started
with Niquests.

First, make sure that:

* Niquests is :ref:`installed <install>`
* Niquests is :ref:`up-to-date <updates>`

Let's get started with some simple examples.

.. note::

    Any async example must be enclosed in a proper async function and started by ``asyncio.run(...)``.

    .. code:: python

        import asyncio
        import niquests

        async def main() -> None:
            """past your example code here!"""

        if __name__ == "__main__":
            asyncio.run(main())


Make a Request
--------------

Making a request with Niquests is very simple.

Begin by importing the Niquests module:

.. code:: python

    import niquests

Now, let's try to get a webpage. For this example, let's get GitHub's public
timeline.

.. tab:: 🔂 Sync

    .. code:: python

        r = niquests.get('https://api.github.com/events')

.. tab:: 🔀 Async

    .. code:: python

        r = await niquests.aget('https://api.github.com/events')

Now, we have a :class:`Response <niquests.Response>` object called ``r``. We can
get all the information we need from this object.

Niquests' simple API means that all forms of HTTP request are as obvious. For
example, this is how you make an HTTP POST request:

.. tab:: 🔂 Sync

    .. code:: python

        r = niquests.post('https://httpbin.org/post', data={'key': 'value'})

.. tab:: 🔀 Async

    .. code:: python

        r = await niquests.apost('https://httpbin.org/post', data={'key': 'value'})

Nice, right? What about the other HTTP request types: PUT, DELETE, HEAD and
OPTIONS? These are all just as simple:

.. tab:: 🔂 Sync

    .. code:: python

        r = niquests.put('https://httpbin.org/put', data={'key': 'value'})
        r = niquests.delete('https://httpbin.org/delete')
        r = niquests.head('https://httpbin.org/get')
        r = niquests.options('https://httpbin.org/get')

.. tab:: 🔀 Async

    .. code:: python

        r = await niquests.aput('https://httpbin.org/put', data={'key': 'value'})
        r = await niquests.adelete('https://httpbin.org/delete')
        r = await niquests.ahead('https://httpbin.org/get')
        r = await niquests.aoptions('https://httpbin.org/get')

That's all well and good, but it's also only the start of what Niquests can
do.

Passing Parameters In URLs
--------------------------

You often want to send some sort of data in the URL's query string. If
you were constructing the URL by hand, this data would be given as key/value
pairs in the URL after a question mark, e.g. ``httpbin.org/get?key=val``.
Niquests allows you to provide these arguments as a dictionary of strings,
using the ``params`` keyword argument. As an example, if you wanted to pass
``key1=value1`` and ``key2=value2`` to ``httpbin.org/get``, you would use the
following code:

.. tab:: 🔂 Sync

    .. code:: python

        payload = {'key1': 'value1', 'key2': 'value2'}
        r = niquests.get('https://httpbin.org/get', params=payload)

.. tab:: 🔀 Async

    .. code:: python

        payload = {'key1': 'value1', 'key2': 'value2'}
        r = await niquests.aget('https://httpbin.org/get', params=payload)

You can see that the URL has been correctly encoded by printing the URL:

.. code:: python

    print(r.url)  # 'https://httpbin.org/get?key2=value2&key1=value1'

Note that any dictionary key whose value is ``None`` will not be added to the
URL's query string.

You can also pass a list of items as a value:

.. tab:: 🔂 Sync

    .. code:: python

        payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
        r = niquests.get('https://httpbin.org/get', params=payload)

        print(r.url)  # 'https://httpbin.org/get?key1=value1&key2=value2&key2=value3'

.. tab:: 🔀 Async

    .. code:: python

        payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
        r = await niquests.aget('https://httpbin.org/get', params=payload)

        print(r.url)  # 'https://httpbin.org/get?key1=value1&key2=value2&key2=value3'

Response Content
----------------

We can read the content of the server's response. Consider the GitHub timeline
again:

.. tab:: 🔂 Sync

    .. code:: python

        import niquests

        r = niquests.get('https://api.github.com/events')
        print(r.text)  # '[{"repository":{"open_issues":0,"url":"https://github.com/...

.. tab:: 🔀 Async

    .. code:: python

        import niquests

        r = await niquests.aget('https://api.github.com/events')
        print(r.text)  # '[{"repository":{"open_issues":0,"url":"https://github.com/...

Niquests will automatically decode content from the server. Most unicode
charsets are seamlessly decoded.

When you make a request, Niquests makes educated guesses about the encoding of
the response based on the HTTP headers. The text encoding guessed by Niquests
is used when you access ``r.text``. You can find out what encoding Niquests is
using, and change it, using the ``r.encoding`` property:

.. code:: python

    print(r.encoding)  # 'utf-8'

    r.encoding = 'ISO-8859-1'  # force assign a specific encoding!

.. warning:: If Niquests is unable to decode the content to string with confidence, it simply return None.

If you change the encoding, Niquests will use the new value of ``r.encoding``
whenever you call ``r.text``. You might want to do this in any situation where
you can apply special logic to work out what the encoding of the content will
be. For example, HTML and XML have the ability to specify their encoding in
their body. In situations like this, you should use ``r.content`` to find the
encoding, and then set ``r.encoding``. This will let you use ``r.text`` with
the correct encoding.

Niquests will also use custom encodings in the event that you need them. If
you have created your own encoding and registered it with the ``codecs``
module, you can simply use the codec name as the value of ``r.encoding`` and
Niquests will handle the decoding for you.

Binary Response Content
-----------------------

You can also access the response body as bytes, for non-text requests::

    >>> r.content
    b'[{"repository":{"open_issues":0,"url":"https://github.com/...

The ``gzip`` and ``deflate`` transfer-encodings are automatically decoded for you.

The ``br``  transfer-encoding is automatically decoded for you if a Brotli library
like `brotli <https://pypi.org/project/brotli>`_ or `brotlicffi <https://pypi.org/project/brotlicffi>`_ is installed.

The ``zstd``  transfer-encoding is automatically decoded for you if the zstandard library `zstandard <https://pypi.org/project/zstandard>`_ is installed.

For example, to create an image from binary data returned by a request, you can
use the following code::

    >>> from PIL import Image
    >>> from io import BytesIO

    >>> i = Image.open(BytesIO(r.content))

JSON Response Content
---------------------

There's also a builtin JSON decoder, in case you're dealing with JSON data:

.. tab:: 🔂 Sync

    .. code:: python

        import niquests

        r = niquests.get('https://api.github.com/events')
        print(r.json())  # [{'repository': {'open_issues': 0, 'url': 'https://github.com/...

.. tab:: 🔀 Async

    .. code:: python

        import niquests

        r = await niquests.aget('https://api.github.com/events')
        print(r.json())  # [{'repository': {'open_issues': 0, 'url': 'https://github.com/...

In case the JSON decoding fails, ``r.json()`` raises an exception. For example, if
the response gets a 204 (No Content), or if the response contains invalid JSON,
attempting ``r.json()`` raises ``niquests.exceptions.JSONDecodeError``. This wrapper exception
provides interoperability for multiple exceptions that may be thrown by different
python versions and json serialization libraries.

.. warning:: It should be noted that this method will raise ``niquests.exceptions.JSONDecodeError`` if the proper Content-Type isn't set to anything that refer to JSON.

It should be noted that the success of the call to ``r.json()`` does **not**
indicate the success of the response. Some servers may return a JSON object in a
failed response (e.g. error details with HTTP 500). Such JSON will be decoded
and returned. To check that a request is successful, use
``r.raise_for_status()`` or check ``r.status_code`` is what you expect.

.. note:: Since Niquests 3.2, ``r.raise_for_status()`` is chainable as it returns self if everything went fine.

.. tip:: Niquests support using ``orjson`` instead of the ``json`` standard library. To leverage that feature, install ``orjson`` or ``niquests[speedups]``. This can dramatically increase performance.

Raw Response Content
--------------------

In the rare case that you'd like to get the raw socket response from the
server, you can access ``r.raw``. If you want to do this, make sure you set
``stream=True`` in your initial request. Once you do, you can do this:

.. tab:: 🔂 Sync

    .. code:: python

        r = niquests.get('https://api.github.com/events', stream=True)

        r.raw
        # <urllib3.response.HTTPResponse object at 0x101194810>

        r.raw.read(10)
        # b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03'

.. tab:: 🔀 Async

    .. code:: python

        r = await niquests.aget('https://api.github.com/events', stream=True)

        r.raw
        # <urllib3._async.response.AsyncHTTPResponse object at 0x101194810>

        await r.raw.read(10)
        # b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03'


In general, however, you should use a pattern like this to save what is being
streamed to a file:

.. tab:: 🔂 Sync

    .. code:: python

        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

.. tab:: 🔀 Async

    .. code:: python

        with open(filename, 'wb') as fd:
            async for chunk in await r.iter_content(chunk_size=128):
                fd.write(chunk)

    .. warning:: It is recommended to use ``aiofile`` or similar to handle file I/O in async mode.

Using ``Response.iter_content`` will handle a lot of what you would otherwise
have to handle when using ``Response.raw`` directly. When streaming a
download, the above is the preferred and recommended way to retrieve the
content. Note that ``chunk_size`` can be freely adjusted to a number that
may better fit your use cases.

.. note::

   An important note about using ``Response.iter_content`` versus ``Response.raw``.
   ``Response.iter_content`` will automatically decode the ``gzip`` and ``deflate``
   transfer-encodings.  ``Response.iter_raw`` is a raw stream of bytes -- it does not
   transform the response content.  If you really need access to the bytes as they
   were returned, use ``Response.iter_raw``.


Custom Headers
--------------

If you'd like to add HTTP headers to a request, simply pass in a ``dict`` to the
``headers`` parameter.

For example, we didn't specify our user-agent in the previous example:

.. tab:: 🔂 Sync

    .. code:: python

        url = 'https://api.github.com/some/endpoint'
        headers = {'user-agent': 'my-app/0.0.1'}

        r = niquests.get(url, headers=headers)

.. tab:: 🔀 Async

    .. code:: python

        url = 'https://api.github.com/some/endpoint'
        headers = {'user-agent': 'my-app/0.0.1'}

        r = await niquests.aget(url, headers=headers)

Note: Custom headers are given less precedence than more specific sources of information. For instance:

* Authorization headers set with `headers=` will be overridden if credentials
  are specified in ``.netrc``, which in turn will be overridden by the  ``auth=``
  parameter. Niquests will search for the netrc file at `~/.netrc`, `~/_netrc`,
  or at the path specified by the `NETRC` environment variable.
* Authorization headers will be removed if you get redirected off-host.
* Proxy-Authorization headers will be overridden by proxy credentials provided in the URL.
* Content-Length headers will be overridden when we can determine the length of the content.

Furthermore, Niquests does not change its behavior at all based on which custom headers are specified. The headers are simply passed on into the final request.

Note: All header values must be a ``string``, bytestring, or unicode. While permitted, it's advised to avoid passing unicode header values.

More complicated POST requests
------------------------------

Typically, you want to send some form-encoded data — much like an HTML form.
To do this, simply pass a dictionary to the ``data`` argument. Your
dictionary of data will automatically be form-encoded when the request is made:

.. code:: python

    >>> payload = {'key1': 'value1', 'key2': 'value2'}

    >>> r = niquests.post('https://httpbin.org/post', data=payload)
    >>> print(r.text)
    {
      ...
      "form": {
        "key2": "value2",
        "key1": "value1"
      },
      ...
    }

The ``data`` argument can also have multiple values for each key. This can be
done by making ``data`` either a list of tuples or a dictionary with lists
as values. This is particularly useful when the form has multiple elements that
use the same key::

    >>> payload_tuples = [('key1', 'value1'), ('key1', 'value2')]
    >>> r1 = niquests.post('https://httpbin.org/post', data=payload_tuples)
    >>> payload_dict = {'key1': ['value1', 'value2']}
    >>> r2 = niquests.post('https://httpbin.org/post', data=payload_dict)
    >>> print(r1.text)
    {
      ...
      "form": {
        "key1": [
          "value1",
          "value2"
        ]
      },
      ...
    }
    >>> r1.text == r2.text
    True

There are times that you may want to send data that is not form-encoded. If
you pass in a ``string`` instead of a ``dict``, that data will be posted directly.

For example, the GitHub API v3 accepts JSON-Encoded POST/PATCH data::

    >>> import json

    >>> url = 'https://api.github.com/some/endpoint'
    >>> payload = {'some': 'data'}

    >>> r = niquests.post(url, data=json.dumps(payload))

Please note that the above code will NOT add the ``Content-Type`` header
(so in particular it will NOT set it to ``application/json``).

If you need that header set and you don't want to encode the ``dict`` yourself,
you can also pass it directly using the ``json`` parameter (added in version 2.4.2)
and it will be encoded automatically:

    >>> url = 'https://api.github.com/some/endpoint'
    >>> payload = {'some': 'data'}

    >>> r = niquests.post(url, json=payload)

Note, the ``json`` parameter is ignored if either ``data`` or ``files`` is passed.

POST a Multipart Form-Data without File
---------------------------------------

Since Niquests 3.1.2 it is possible to overrule the default conversion to ``application/x-www-form-urlencoded`` type.
You can submit a form-data by helping Niquests understand what you meant.

    >>> url = 'https://httpbin.org/post'
    >>> payload = {'some': 'data'}

    >>> r = niquests.post(url, data=payload, headers={"Content-Type": "multipart/form-data"})

Now, instead of submitting a urlencoded body, as per the default, Niquests will send instead a proper
form-data.

.. note:: You can also specify manually a boundary in the header value. Niquests will reuse it. Otherwise it will assign a random one.

POST a Multipart-Encoded File
-----------------------------

Niquests makes it simple to upload Multipart-encoded files::

    >>> url = 'https://httpbin.org/post'
    >>> files = {'file': open('report.xls', 'rb')}

    >>> r = niquests.post(url, files=files)
    >>> r.text
    {
      ...
      "files": {
        "file": "<censored...binary...data>"
      },
      ...
    }

You can set the filename, content_type and headers explicitly::

    >>> url = 'https://httpbin.org/post'
    >>> files = {'file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}

    >>> r = niquests.post(url, files=files)
    >>> r.text
    {
      ...
      "files": {
        "file": "<censored...binary...data>"
      },
      ...
    }

If you want, you can send strings to be received as files::

    >>> url = 'https://httpbin.org/post'
    >>> files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}

    >>> r = niquests.post(url, files=files)
    >>> r.text
    {
      ...
      "files": {
        "file": "some,data,to,send\\nanother,row,to,send\\n"
      },
      ...
    }

In the event you are posting a very large file as a ``multipart/form-data``
request, you may want to stream the request. By default, ``niquests`` does not
support this, but there is a separate package which does -
``requests-toolbelt``. You should read `the toolbelt's documentation
<https://toolbelt.readthedocs.io>`_ for more details about how to use it.

For sending multiple files in one request refer to the :ref:`advanced <advanced>`
section.


Response Status Codes
---------------------

We can check the response status code::

    >>> r = niquests.get('https://httpbin.org/get')
    >>> r.status_code
    200

Niquests also comes with a built-in status code lookup object for easy
reference::

    >>> r.status_code == niquests.codes.ok
    True

If we made a bad request (a 4XX client error or 5XX server error response), we
can raise it with
:meth:`Response.raise_for_status() <niquests.Response.raise_for_status>`::

    >>> bad_r = niquests.get('https://httpbin.org/status/404')
    >>> bad_r.status_code
    404

    >>> bad_r.raise_for_status()
    Traceback (most recent call last):
      File "requests/models.py", line 832, in raise_for_status
        raise http_error
    niquests.exceptions.HTTPError: 404 Client Error

But, since our ``status_code`` for ``r`` was ``200``, when we call
``raise_for_status()`` we get::

    >>> r.raise_for_status()
    <Response HTTP/2 [200]>

All is well.


Response Headers
----------------

We can view the server's response headers using a Python dictionary::

    >>> r.headers
    {
        'content-encoding': 'gzip',
        'transfer-encoding': 'chunked',
        'connection': 'close',
        'server': 'nginx/1.0.4',
        'x-runtime': '148ms',
        'etag': '"e1ca502697e5c9317743dc078f67693f"',
        'content-type': 'application/json'
    }

The dictionary is special, though: it's made just for HTTP headers. According to
`RFC 7230 <https://tools.ietf.org/html/rfc7230#section-3.2>`_, HTTP Header names
are case-insensitive.

So, we can access the headers using any capitalization we want:

.. raw:: html

   <pre class="terminhtml">
    >>> r.headers['Content-Type']
    'application/json'
    >>> r.headers.get('content-type')
    'application/json'
   </pre>

It is also special in that the server could have sent the same header multiple
times with different values, but requests combines them so they can be
represented in the dictionary within a single mapping, as per
`RFC 7230 <https://tools.ietf.org/html/rfc7230#section-3.2>`_:

    A recipient MAY combine multiple header fields with the same field name
    into one "field-name: field-value" pair, without changing the semantics
    of the message, by appending each subsequent field value to the combined
    field value in order, separated by a comma.

It most cases you'd rather quickly access specific key element of headers.
Fortunately, you can access HTTP headers as they were objects.

.. raw:: html

   <pre class="terminhtml">
    >>> r.oheaders.content_type.charset
    'utf-8'
    >>> r.oheaders.report_to.max_age
    '604800'
    >>> str(r.oheaders.date)
    'Mon, 02 Oct 2023 05:34:48 GMT'
    >>> from kiss_headers import get_polymorphic, Date
    >>> h = get_polymorphic(r.oheaders.date, Date)
    >>> repr(h.get_datetime())
    datetime.datetime(2023, 10, 2, 5, 39, 46, tzinfo=datetime.timezone.utc)
   </pre>

To explore possibilities, visit the ``kiss-headers`` documentation at https://jawah.github.io/kiss-headers/

Cookies
-------

If a response contains some Cookies, you can quickly access them:

.. raw:: html

   <pre class="terminhtml">
    >>> url = 'http://example.com/some/cookie/setting/url'
    >>> r = niquests.get(url)

    >>> r.cookies['example_cookie_name']
    'example_cookie_value'
   </pre>

To send your own cookies to the server, you can use the ``cookies``
parameter:

.. raw:: html

   <pre class="terminhtml">
    >>> url = 'https://httpbin.org/cookies'
    >>> cookies = dict(cookies_are='working')

    >>> r = niquests.get(url, cookies=cookies)
    >>> r.text
    '{"cookies": {"cookies_are": "working"}}'
   </pre>

Cookies are returned in a :class:`~niquests.cookies.RequestsCookieJar`,
which acts like a ``dict`` but also offers a more complete interface,
suitable for use over multiple domains or paths.  Cookie jars can
also be passed in to requests:

.. raw:: html

   <pre class="terminhtml">
    >>> jar = niquests.cookies.RequestsCookieJar()
    >>> jar.set('tasty_cookie', 'yum', domain='httpbin.org', path='/cookies')
    >>> jar.set('gross_cookie', 'blech', domain='httpbin.org', path='/elsewhere')
    >>> url = 'https://httpbin.org/cookies'
    >>> r = niquests.get(url, cookies=jar)
    >>> r.text
    '{"cookies": {"tasty_cookie": "yum"}}'
   </pre>

Redirection and History
-----------------------

By default Niquests will perform location redirection for all verbs except
HEAD.

We can use the ``history`` property of the Response object to track redirection.

The :attr:`Response.history <niquests.Response.history>` list contains the
:class:`Response <niquests.Response>` objects that were created in order to
complete the request. The list is sorted from the oldest to the most recent
response.

For example, GitHub redirects all HTTP requests to HTTPS:

.. raw:: html

   <pre class="terminhtml">
    >>> r = niquests.get('http://github.com/')
    >>> r.url
    'https://github.com/'
    >>> r.status_code
    200
    >>> r.history
    [<Response HTTP/2 [301]>]
   </pre>

If you're using GET, OPTIONS, POST, PUT, PATCH or DELETE, you can disable
redirection handling with the ``allow_redirects`` parameter:

.. raw:: html

   <pre class="terminhtml">
    >>> r = niquests.get('http://github.com/', allow_redirects=False)
    >>> r.status_code
    301
    >>> r.history
    []
   </pre>

If you're using HEAD, you can enable redirection as well:

.. raw:: html

   <pre class="terminhtml">
    >>> r = niquests.head('http://github.com/', allow_redirects=True)
    >>> r.url
    'https://github.com/'
    >>> r.history
    [<Response HTTP/2 [301]>]
   </pre>

Timeouts
--------

You can tell Niquests to stop waiting for a response after a given number of
seconds with the ``timeout`` parameter. Nearly all production code should use
this parameter in nearly all requests. By default GET, HEAD, OPTIONS ships with a
30 seconds timeout delay and 120 seconds for the rest::

    >>> niquests.get('https://github.com/', timeout=0.001)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    niquests.exceptions.Timeout: HTTPConnectionPool(host='github.com', port=80): Request timed out. (timeout=0.001)


.. note::

    ``timeout`` is not a time limit on the entire response download;
    rather, an exception is raised if the server has not issued a
    response for ``timeout`` seconds (more precisely, if no bytes have been
    received on the underlying socket for ``timeout`` seconds). If no timeout is specified explicitly, requests
    use the default according to your HTTP verb. Either 30 seconds or 120 seconds.

.. warning::

    We know that users are surprised by the ``timeout`` behaviors. You should know
    that Niquests is bound to some legacy behaviors that existed well prior us.
    Let's say that you set up ``timeout=1`` to a specific host. Now let's say on
    purpose that the host is down. Then we should expect the request to fail
    exactly 1s after. That is correct. But! Beware that if the host has more than
    1 DNS records (either A or AAAA), they all will be tested with set timeout limit!
    So if ``example.tld`` has two IPs associated, then you should expect 2s max delay.
    And so on, so forth...

.. tip::

    Set ``happy_eyeballs=True`` when constructing your ``Session`` to try all endpoints simultaneously.
    This will help you circumvent most of the connectivity issues.

.. warning::

    Unfortunately, due to a Python restriction, we cannot ensure that ``timeout`` is respected if your system DNS is
    unresponsive. This only applies in synchronous mode (i.e. not async).
    To circumvent that issue, you should use a more modern DNS resolver solution. See ``resolver=...`` parameter.

Errors and Exceptions
---------------------

In the event of a network problem (e.g. DNS failure, refused connection, etc),
Niquests will raise a :exc:`~niquests.exceptions.ConnectionError` exception.

:meth:`Response.raise_for_status() <niquests.Response.raise_for_status>` will
raise an :exc:`~niquests.exceptions.HTTPError` if the HTTP request
returned an unsuccessful status code.

If a request times out, a :exc:`~niquests.exceptions.Timeout` exception is
raised.

If a request exceeds the configured number of maximum redirections, a
:exc:`~niquests.exceptions.TooManyRedirects` exception is raised.

All exceptions that Niquests explicitly raises inherit from
:exc:`niquests.exceptions.RequestException`.

HTTP/3 over QUIC
----------------

**Niquests** relies on urllib3.future that relies on the qh3 package.
The underlying package may or may not be installed on your environment.

If it is not present, no HTTP/3 or QUIC support will be present.

If you uninstall the qh3 package it disable the support for HTTP/3 without breaking anything.
On the overhand, installing it manually (may require compilation toolchain) will bring its support.

Find a quick way to know if your environment is capable of emitting HTTP/3 requests by:

.. raw:: html

   <pre class="terminhtml">
    >>> from niquests import get
    >>> r = get("https://1.1.1.1")
    >>> r
    <Response HTTP/2 [200]>
    >>> r = get("https://1.1.1.1")
    >>> r
    <Response HTTP/3 [200]>
   </pre>

The underlying library natively understand the ``Alt-Svc`` header and is constantly looking for the ``h3``
alternative service. Once it finds it, and is deemed valid, it opens up a QUIC connection to the target.
It is saved in-memory by Niquests.

You may also run the following command ``python -m niquests.help`` to find out if you support HTTP/3.
In 98 percents of the case, the answer is yes!

.. note:: Since urllib3.future version 2.4+ we support negotiating HTTP/3 without a first TCP connection if the remote peer indicated in a HTTPS (DNS) record that the server support HTTP/3.

Multiplexed Connection
----------------------

Starting from Niquests 3.2 you can issue concurrent requests without having multiple connections.
It can leverage multiplexing when your remote peer support either HTTP/2, or HTTP/3.

The only thing you will ever have to do to get started is to specify ``multiplexed=True`` from
within your ``Session`` constructor.

Any ``Response`` returned by get, post, put, etc... will be a lazy instance of ``Response``.

.. note::

   An important note about using ``Session(multiplexed=True)`` is that, in order to be efficient
   and actually leverage its perks, you will have to issue multiple concurrent request before
   actually trying to access any ``Response`` methods or attributes.

Modern browsers like Firefox, and Chrome utilize something really like ``multiplexed=True`` mode!
It's a bit like if we have a controlled concurrent environment.

Gather responses
~~~~~~~~~~~~~~~~

Emitting concurrent requests and loading them via `Session.gather()`::

    from niquests import Session
    from time import time

    s = Session(multiplexed=True)

    before = time()
    responses = []

    responses.append(
      s.get("https://httpbingo.org/delay/3")
    )

    responses.append(
      s.get("https://httpbingo.org/delay/1")
    )

    s.gather()

    print(f"waited {time() - before} second(s)")  # will print 3s


Direct Access
~~~~~~~~~~~~~

Emitting concurrent requests and loading them via direct access::

    from niquests import Session
    from time import time

    s = Session(multiplexed=True)

    before = time()
    responses = []

    responses.append(
      s.get("https://httpbingo.org/delay/3")
    )

    responses.append(
      s.get("https://httpbingo.org/delay/1")
    )

    # internally call gather with self (Response)
    print(responses[0].status_code)  # 200! :! Hidden call to s.gather(responses[0])
    print(responses[1].status_code)  # 200!

    print(f"waited {time() - before} second(s)")  # will print 3s

The possible algorithms are actually nearly limitless, and you may arrange/write you own scheduling technics!

Session Gather
--------------

The ``Session`` instance expose a method called ``gather(*responses, max_fetch = None)``, you may call it to
improve the efficiency of resolving your _lazy_ responses.

Here are the possible outcome of invocation::

    s.gather()  # resolve all pending "lazy" responses
    s.gather(resp)  # resolve given "resp" only
    s.gather(max_fetch=2)  # resolve two responses (the first two that come)
    s.gather(resp_a, resp_b, resp_c)  # resolve all three
    s.gather(resp_a, resp_b, resp_c, max_fetch=1)  # only resolve the first one

.. note:: Call to ``s.gather`` is optional, you can access at will the responses properties and methods at any time.

Async session
-------------

You may have a program that require ``awaitable`` HTTP request. You are in luck as **Niquests** ships with
an implementation of ``Session`` that support **async**.

All known methods remain the same at the sole difference that it return a coroutine.

Here is a basic example::

    import asyncio
    from niquests import AsyncSession, Response

    async def fetch(url: str) -> Response:
        async with AsyncSession() as s:
            return await s.get(url)

    async def main() -> None:
        tasks = []

        for _ in range(10):
            tasks.append(asyncio.create_task(fetch("https://httpbingo.org/delay/1")))

        responses = await asyncio.gather(*tasks)

        print(responses)

    if __name__ == "__main__":
        asyncio.run(main())


.. warning:: For the time being **Niquests** only support **asyncio** as the backend library for async. Contributions are welcomed if you want it to be compatible with **anyio** for example.

.. note:: Shortcut functions `get`, `post`, ..., from the top-level package does not support async.

Async and Multiplex
-------------------

You can leverage a multiplexed connection while in an async context!
It's the perfect solution while dealing with two or more hosts that support HTTP/2 onward.

Look at this basic sample::

    import asyncio
    from niquests import AsyncSession, Response

    async def fetch(url: str) -> list[Response]:
        responses = []

        async with AsyncSession(multiplexed=True) as s:
            for _ in range(10):
                responses.append(await s.get(url))

            await s.gather()

            return responses

    async def main() -> None:
        tasks = []

        for _ in range(10):
            tasks.append(asyncio.create_task(fetch("https://httpbingo.org/delay/1")))

        responses_responses = await asyncio.gather(*tasks)
        responses = [item for sublist in responses_responses for item in sublist]

        print(responses)

    if __name__ == "__main__":
        asyncio.run(main())


.. warning:: Combining AsyncSession with ``multiplexed=True`` and passing ``stream=True`` produces ``AsyncResponse``, make sure to call ``await session.gather()`` before trying to access directly the lazy instance of response.

AsyncResponse for streams
-------------------------

Delaying the content consumption in an async context can be easily achieved using::

    import niquests
    import asyncio

    async def main() -> None:

        async with niquests.AsyncSession() as s:
            r = await s.get("https://httpbingo.org/get", stream=True)

            async for chunk in await r.iter_content(16):
                print(chunk)

    if __name__ == "__main__":

        asyncio.run(main())

Or using the ``iter_line`` method as such::

    import niquests
    import asyncio

    async def main() -> None:

        async with niquests.AsyncSession() as s:
            r = await s.get("https://httpbingo.org/get", stream=True)

            async for chunk in r.iter_line():
                print(chunk)

    if __name__ == "__main__":
        asyncio.run(main())

Or simply by doing::

    import niquests
    import asyncio

    async def main() -> None:

        async with niquests.AsyncSession() as s:
            r = await s.get("https://httpbingo.org/get", stream=True)
            payload = await r.json()

    if __name__ == "__main__":

        asyncio.run(main())

When you specify ``stream=True`` within a ``AsyncSession``, the returned object will be of type ``AsyncResponse``.
So that the following methods and properties will be coroutines (aka. awaitable):

- iter_content(...)
- iter_lines(...)
- content
- json(...)
- text(...)
- close()

When enabling multiplexing while in an async context, you will have to issue a call to ``await s.gather()``
to avoid blocking your event loop.

Here is a basic example of how you would do it::

    import niquests
    import asyncio

    async def main() -> None:

        responses = []

        async with niquests.AsyncSession(multiplexed=True) as s:
            responses.append(
                await s.get("https://httpbingo.org/get", stream=True)
            )
            responses.append(
                await s.get("https://httpbingo.org/get", stream=True)
            )

            print(responses)

            await s.gather()

            print(responses)

            for response in responses:
                async for chunk in await response.iter_content(16):
                    print(chunk)


    if __name__ == "__main__":

        asyncio.run(main())

.. warning:: Accessing (non awaitable attribute or method) of a lazy ``AsyncResponse`` without a call to ``s.gather()`` will raise an error.

Scale your Session / Pool
-------------------------

By default, Niquests allow, concurrently 10 hosts, and 10 connections per host.
You can at your own discretion increase or decrease the values.

To do so, you are invited to set the following parameters within a Session constructor:

``Session(pool_connections=10, pool_maxsize=10)``

- **pool_connections** means the number of host target (or pool of connections if you prefer).
- **pool_maxsize** means the maximum of concurrent connexion per host target/pool.

.. tip:: Due to the multiplexed aspect of both HTTP/2, and HTTP/3 you can issue, usually, more than 200 requests per connection without ever needing to create another one.

.. note:: This setting is most useful for multi-threading/tasks application.

Pool Connections
~~~~~~~~~~~~~~~~

Setting ``pool_connections=2`` will keep the connection to ``host-b.tld`` and ``host-c.tld``.
``host-a.tld`` will be silently discarded.

.. code:: python

    import niquests

    with niquests.Session(pool_connections=2) as s:
        s.get("https://host-a.tld/some")
        s.get("https://host-b.tld/some")
        s.get("https://host-c.tld/some")

.. attention::

    Unfortunately, due to backward compatibility issues, those settings applies PER SCHEME.
    ``pool_connections=2`` will allow up to 2 HTTP (unencrypted) and 2 HTTPS (encrypted)
    connections. Meaning that you can still get 4 hosts being kept alive.

Pool Maxsize
~~~~~~~~~~~~

Setting ``pool_maxsize=2`` will allow up to 2 connection to ``host-a.tld``.
This settings is only useful in a concurrent environment. Either async or threaded.

DNS Resolution
--------------

Niquests has a built-in support for DNS over HTTPS, DNS over TLS, DNS over UDP, and DNS over QUIC.
Thanks to our built-in system trust store access, you don't have to worry one bit about certificates validation.

This feature is based on the native implementation brought to you by the awesome **urllib3.future**.
Once you have specified a custom resolver (e.g. not the system default), you will automatically be protected with
DNSSEC in additions to specifics security perks on chosen protocol.

Specify your own resolver
~~~~~~~~~~~~~~~~~~~~~~~~~

In order to specify a resolver, you have to use a ``Session``. Each ``Session`` can have a different resolver.
Here is a basic example that leverage Google public DNS over HTTPS.

.. tab:: 🔂 Sync

    .. code:: python

        from niquests import Session

        with Session(resolver="doh+google://") as s:
            resp = s.get("https://httpbingo.org/get")

.. tab:: 🔀 Async

    .. code:: python

        from niquests import AsyncSession

        async with AsyncSession(resolver="doh+google://") as s:
            resp = await s.get("https://httpbingo.org/get")

Here, the domain name (**httpbingo.org**) will be resolved using the provided DNS provider (e.g. Google public and encrypted DNS).

.. note:: By default, Niquests still use the good old, often insecure, system DNS.

Use multiple resolvers
~~~~~~~~~~~~~~~~~~~~~~

You may specify a list of resolvers to be tested in presented order.

.. tab:: 🔂 Sync

    .. code:: python

        from niquests import Session

        with Session(resolver=["doh+google://", "doh://cloudflare-dns.com"]) as s:
            resp = s.get("https://httpbingo.org/get")

.. tab:: 🔀 Async

    .. code:: python

        from niquests import AsyncSession

        async with AsyncSession(resolver=["doh+google://", "doh://cloudflare-dns.com"]) as s:
            resp = await s.get("https://httpbingo.org/get")

The second entry ``doh://cloudflare-dns.com`` will only be tested if ``doh+google://`` failed to provide a usable answer.

.. note:: In a multi-threaded context, both resolvers are going to be used in order to improve performance.

Supported DNS url
~~~~~~~~~~~~~~~~~

Niquests support a wide range of DNS protocols. Here are a few examples::

    "doh+google://"  # shortcut url for Google DNS over HTTPS
    "dot+google://"  # shortcut url for Google DNS over TLS
    "doh+cloudflare://" # shortcut url for Cloudflare DNS over HTTPS
    "doq+adguard://" # shortcut url for Adguard DNS over QUIC
    "dou://1.1.1.1"  # url for DNS over UDP (Plain resolver)
    "dou://1.1.1.1:8853" # url for DNS over UDP using port 8853 (Plain resolver)
    "doh://my-resolver.tld" # url for DNS over HTTPS using server my-resolver.tld

.. note:: Learn more by looking at the **urllib3.future** documentation: https://urllib3future.readthedocs.io/en/latest/advanced-usage.html#using-a-custom-dns-resolver

Set DNS via environment
~~~~~~~~~~~~~~~~~~~~~~~

You can set the ``NIQUESTS_DNS_URL`` environment variable with desired resolver, it will be
used in every Session **that does not manually specify a resolver.**

Example::

    export NIQUESTS_DNS_URL="doh://google.dns"

Disable DNS certificate verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply add ``verify=false`` into your DNS url to pursue.

.. tab:: 🔂 Sync

    .. code:: python

        from niquests import Session

        with Session(resolver="doh+google://default/?verify=false") as s:
            resp = s.get("https://httpbingo.org/get")

.. tab:: 🔀 Async

    .. code:: python

        from niquests import AsyncSession

        async with AsyncSession(resolver="doh+google://default/?verify=false") as s:
            resp = await s.get("https://httpbingo.org/get")

.. warning:: Doing a ``s.get("https://httpbingo.org/get", verify=False)`` does not impact the resolver.

Timeouts
~~~~~~~~

You may set a specific timeout for domain name resolution by appending ``?timeout=1`` to the resolver configuration.

.. tab:: 🔂 Sync

    .. code:: python

        from niquests import Session

        with Session(resolver="doh+google://default/?timeout=1") as s:
            resp = s.get("https://httpbingo.org/get")

.. tab:: 🔀 Async

    .. code:: python

        from niquests import AsyncSession

        async with AsyncSession(resolver="doh+google://default/?timeout=1") as s:
            resp = await s.get("https://httpbingo.org/get")

This will prevent any DNS resolution that last longer to a second.

Happy Eyeballs
--------------

.. note:: Available since version 3.5.5+

Thanks to the underlying library (urllib3.future) we are able to serve the Happy Eyeballs feature, one toggle away.

Happy Eyeballs (also called Fast Fallback) is an algorithm published by the IETF that makes dual-stack applications
(those that understand both IPv4 and IPv6) more responsive to users by attempting to connect using both IPv4 and IPv6
at the same time (preferring IPv6), thus minimizing common problems experienced by users with imperfect IPv6 connections or setups.

The name “happy eyeballs” derives from the term “eyeball” to describe endpoints which represent human Internet end-users, as opposed to servers.

.. tab:: 🔂 Sync

    .. code:: python

        import niquests

        with niquests.Session(happy_eyeballs=True) as s:
            ...

.. tab:: 🔀 Async

    .. code:: python

        import niquests

        async with niquests.AsyncSession(happy_eyeballs=True) as s:
            ...

A mere ``happy_eyeballs=True`` is sufficient to leverage its potential.

.. note:: In case a server yield multiple IPv4 addresses but no IPv6, this still applies. Meaning that Niquests will connect concurrently to presented addresses and determine what is the fastest endpoint.

.. note:: Like urllib3.future, you can pass an integer to increase the default number of concurrent connection to be tested. See https://urllib3future.readthedocs.io/en/latest/advanced-usage.html#happy-eyeballs to learn more.

OCSP requests (certificate revocation checks) will follow given ``happy_eyeballs=True`` parameter.

.. warning:: This feature is disabled by default and we are actually planning to make it enabled as the default in a future major.

WebSockets
----------

.. note:: Available since version 3.9+ and requires to install an extra. ``pip install niquests[ws]``.

It is undeniable that WebSockets are a vital part of the web ecosystem along with HTTP. We noticed that
most users met frictions when trying to deal with a WebSocket server for the first time, that is why
we decided to expand Niquests capabilities to automatically handle WebSockets for you.

Quick start
~~~~~~~~~~~

In the following example, we will explore how to interact with a basic, but well known echo server.

.. tab:: 🔂 Sync

    .. code:: python

        from niquests import Session

        with Session() as s:
            resp = s.get(
                "wss://echo.websocket.org",
            )

            print(resp.status_code)  # it says "101", for "Switching Protocol"

            print(resp.extension.next_payload())  # unpack the next message from server

            resp.extension.send_payload("Hello World")  # automatically sends a text message to the server

            print(resp.extension.next_payload() == "Hello World")  # output True!

            resp.extension.close()  # don't forget this call to release the connection!

.. tab:: 🔀 Async

    .. code:: python

        from niquests import AsyncSession
        import asyncio

        async def main() -> None:
            async with AsyncSession() as s:
                resp = await s.get("wss://echo.websocket.org")

                # ...

                print(await resp.extension.next_payload())  # unpack the next message from server

                await resp.extension.send_payload("Hello World")  # automatically sends a text message to the server

                print((await resp.extension.next_payload()) == "Hello World")  # output True!

                await resp.extension.close()

.. warning:: Without the extra installed, you will get an exception that indicate that the scheme is unsupported.

.. note:: Historically, Requests only accepted http:// and https:// as schemes. But now, you may use wss:// for WebSocket Secure or ws:// for WebSocket over PlainText.

.. warning:: Be careful when accessing ``resp.extension``, if anything goes wrong in the "establishment" phase, meaning the server denies us the WebSocket upgrade, it will be worth ``None``.

WebSocket and HTTP/2+
~~~~~~~~~~~~~~~~~~~~~

By default, Niquests negotiate WebSocket over HTTP/1.1 but it is well capable of doing so over HTTP/2 and HTTP/3 following RFC8441.
But rare are the servers capable of bootstrapping WebSocket over a multiplexed connection. There's a little tweak to the URL
so that it can infer your desire to use a modern protocol, like so ``wss+rfc8441://echo.websocket.org``.

.. warning:: echo.websocket.org don't support WebSocket over HTTP/2.

Ping and Pong
~~~~~~~~~~~~~

Ping sent by a server are automatically handled/answered by Niquests each time to read from the socket with `next_payload()`.
However, we do not send automatically Ping TO the server.

.. tab:: 🔂 Sync

    .. code:: python

        from niquests import Session

        with Session() as s:
            resp = s.get(
                "wss://echo.websocket.org",
            )

            resp.extension.ping()  # send a ping to the websocket server, notify it that you're still there!

.. tab:: 🔀 Async

    .. code:: python

        from niquests import AsyncSession

        async with AsyncSession() as s:
            resp = await s.get(
                "wss://echo.websocket.org",
            )

            await resp.extension.ping()  # send a ping to the websocket server, notify it that you're still there!

You can use the elementary methods provided by Niquests to construct your own logic.

Binary and Text Messages
~~~~~~~~~~~~~~~~~~~~~~~~

You may use ``next_payload()`` and ``send_payload(...)`` with str or bytes.

If ``next_payload()`` output bytes, then it is a BinaryMessage.
If ``next_payload()`` output str, then it is a TextMessage.

The same apply to ``send_payload(...)``, if passed item is str, then we send a TextMessage.
Otherwise, it will be a BinaryMessage.

.. warning:: Niquests does not buffer "incomplete" message (e.g. end marker for a message). It returns every chunk received as is.

.. note:: If ``next_payload()`` returns ``None``, that means that the remote choose to close the connection.

Others
~~~~~~

Every other features still applies with WebSocket, like proxies, happy eyeballs, thread/task safety, etc...
See relevant docs for more.

Example with Concurrency
~~~~~~~~~~~~~~~~~~~~~~~~

In the following example, we will see how to communicate with a WebSocket server that echo what we send to him.
We will use a Thread for the reads and the main thread for write operations.

.. tab:: 🔂 Sync

    .. code:: python

        from __future__ import annotations

        from niquests import Session, Response, ReadTimeout
        from threading import Thread
        from time import sleep


        def pull_message_from_server(my_response: Response) -> None:
            """Read messages here."""
            iteration_counter = 0

            while my_response.extension.closed is False:
                try:
                    # will block for 1s top
                    message = my_response.extension.next_payload()

                    if message is None:  # server just closed the connection. exit.
                        print("received goaway from server")
                        return

                    print(f"received message: '{message}'")
                except ReadTimeout:  # if no message received within 1s
                    pass

                sleep(1)  # let some time for the write part to acquire the lock
                iteration_counter += 1

                # send a ping every four iteration
                if iteration_counter % 4 == 0:
                    my_response.extension.ping()
                    print("ping sent")

        if __name__ == "__main__":

            with Session() as s:
                # connect to websocket server "echo.websocket.org" with timeout of 1s (both read and connect)
                resp = s.get("wss://echo.websocket.org", timeout=1)

                if resp.status_code != 101:
                    exit(1)

                t = Thread(target=pull_message_from_server, args=(resp,))
                t.start()

                # send messages here
                for i in range(30):
                    to_send = f"Hello World {i}"
                    resp.extension.send_payload(to_send)
                    print(f"sent message: '{to_send}'")
                    sleep(1)  # let some time for the read part to acquire the lock

                # exit gently!
                resp.extension.close()

                # wait for thread proper exit.
                t.join()

                print("program ended!")

    .. warning:: The sleep serve the purpose to relax the lock on either the read or write side, so that one would not block the other forever.

.. tab:: 🔀 Async

    .. code:: python

        import asyncio
        from niquests import AsyncSession, ReadTimeout, Response

        async def read_from_ws(my_response: Response) -> None:
            iteration_counter = 0

            while my_response.extension.closed is False:
                try:
                    # will block for 1s top
                    message = await my_response.extension.next_payload()

                    if message is None:  # server just closed the connection. exit.
                        print("received goaway from server")
                        return

                    print(f"received message: '{message}'")
                except ReadTimeout:  # if no message received within 1s
                    pass

                await asyncio.sleep(1)  # let some time for the write part to acquire the lock
                iteration_counter += 1

                # send a ping every four iteration
                if iteration_counter % 4 == 0:
                    await my_response.extension.ping()
                    print("ping sent")

        async def main() -> None:
            async with AsyncSession() as s:
                resp = await s.get("wss://echo.websocket.org", timeout=1)

                print(resp)

                task = asyncio.create_task(read_from_ws(resp))

                for i in range(30):
                    to_send = f"Hello World {i}"
                    await resp.extension.send_payload(to_send)
                    print(f"sent message: '{to_send}'")
                    await asyncio.sleep(1)  # let some time for the read part to acquire the lock

                # exit gently!
                await resp.extension.close()
                await task


        if __name__ == "__main__":
            asyncio.run(main())

.. note:: The given example are really basic ones. You may adjust at will the settings and algorithm to match your requisites.

Server Side Event (SSE)
-----------------------

.. note:: Available since version 3.11.2+

Server side event or widely known with its acronym SSE is a extremely popular method to stream continuously event
from the server to the client in real time.

Before this built-in feature, most way to leverage this were to induce a bit of hacks into your http client.

Starting example
~~~~~~~~~~~~~~~~

Thanks to urllib3-future native SSE extension, we can effortlessly manage a stream of event.
Here is a really basic example of how to proceed.

.. tab:: 🔂 Sync

    .. code:: python

        import niquests

        if __name__ == "__main__":

            r = niquests.post("sse://httpbingo.org/sse")

            print(r)  # output: <Response HTTP/2 [200]>

            while r.extension.closed is False:
                print(r.extension.next_payload())  # ServerSentEvent(event='ping', data='{"id":0,"timestamp":1732857000473}')

.. tab:: 🔀 Async

    .. code:: python

        import niquests
        import asyncio

        async def main() -> None:
            async with niquests.AsyncSession() as s:
                r = await s.post("sse://httpbingo.org/sse")

                print(r)  # output: <Response HTTP/2 [200]>

                while r.extension.closed is False:
                    print(await r.extension.next_payload())  # ServerSentEvent(event='ping', data='{"id":0,"timestamp":1732857000473}')

        if __name__ == "__main__":

            asyncio.run(main())

We purposely set the scheme to ``sse://`` to indicate our intent to consume a SSE endpoint.

.. note:: ``sse://`` is using ``https://`` under the hood. To avoid using an encrypted connection, use ``psse://`` instead.

You will notice that the program is similar to our ``WebSocket`` implementation. Excepted that the ``next_payload()``
method returns by default a ``ServerSentEvent`` object.

Extracting raw event
~~~~~~~~~~~~~~~~~~~~

In the case where your server weren't compliant to the defined web standard for SSE (e.g. add custom field/line style)
you can extract a ``str`` instead of a ``ServerSentEvent`` object by passing ``raw=True`` into our ``next_payload()``
method.

As such::

    while r.extension.closed is False:
        print(r.extension.next_payload(raw=True))  # "event: ping\ndata: {"id":9,"timestamp":1732857471733}\n\n"

.. warning:: As with WebSocket, ``next_payload`` method may return None if the server terminate the stream.

Interrupt the stream
~~~~~~~~~~~~~~~~~~~~

A server may send event forever. And to avoid the awkward situation where your client receive unsolicited data
you should at all time close the SSE extension to notify the remote peer about your intent to stop.

For example, the following test server send events until you say to stop: ``sse://sse.dev/test``

See how to stop cleanly the flow of events:

.. tab:: 🔂 Sync

    .. code:: python

        import niquests

        if __name__ == "__main__":

            r = niquests.post("sse://sse.dev/test")

            events = []

            while r.extension.closed is False:
                event = r.extension.next_payload()

                if event is None:  # the remote peer closed it himself
                    break

                events.append(event)  # add the event to list

                if len(events) >= 10:  # close ourselves SSE stream & notify remote peer.
                    r.extension.close()

.. tab:: 🔀 Async

    .. code:: python

        import niquests
        import asyncio

        async def main() -> None:
            async with niquests.AsyncSession() as s:
                r = await s.post("sse://sse.dev/test")

                events = []

                while r.extension.closed is False:
                    event = await r.extension.next_payload()

                    if event is None:  # the remote peer closed it himself
                        break

                    events.append(event)  # add the event to list

                    if len(events) >= 10:  # close ourselves SSE stream & notify remote peer.
                        await r.extension.close()

        if __name__ == "__main__":

            asyncio.run(main())

ServerSentEvent
~~~~~~~~~~~~~~~

.. note:: A ``ServerSentEvent`` object is returned by default with the ``next_payload()`` method. Or None if the server terminate the flow of events.

It's a parsed SSE (single event). The object have nice shortcuts like:

- ``payload.json()`` (any) to automatically unserialize passed json data.
- ``payload.id`` (str)
- ``payload.data`` (str) for the raw message payload
- ``payload.event`` (str) for the event type (e.g. message, ping, etc...)
- ``payload.retry`` (int)

The full class source is located at https://github.com/jawah/urllib3.future/blob/3d7c5d9446880a8d473b9be4db0bcd419fb32dee/src/urllib3/contrib/webextensions/sse.py#L14

Notes
~~~~~

SSE can be reached from HTTP/1, HTTP/2 or HTTP/3 at will. Niquests makes this very easy.
Moreover every features like proxies, happy-eyeballs, hooks, etc.. can be used as you always did.

-----------------------

Ready for more? Check out the :ref:`advanced <advanced>` section.
