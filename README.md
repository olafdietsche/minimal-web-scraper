# Minimal web scraper

This is a small web scraper using [lxml](http://lxml.de/). It allows
loading web pages, following links and filling out forms.

## Usage

    import web
    from lxml import etree
    import http.client

    http.client.HTTPConnection.debuglevel = 1

    ua = web.UserAgent()
    response = ua.get('http://www.example.com/login.php')
    doc = ua.parse(response)

    form = web.Form(response, doc)
    response = form.submit(ua, {'username': 'mary@example.com',
                                'password': 'Secret'})
    doc = ua.parse(response)

    response = ua.follow_link(response, doc,
                              "//div[contains(@class, 'foo')]/a/@href")
    doc = ua.parse(response)

## License

BSD-3
