from urllib.parse import quote

__author__ = 'pahaz'


def escape_uri_path(path):
    """
    Escape the unsafe characters from the path portion
    of a Uniform Resource Identifier (URI).

    >>> escape_uri_path('/I \xe2\x99\xa5 MiniDjango/?foo=bar')
    '/I%20%C3%A2%C2%99%C2%A5%20MiniDjango/%3Ffoo%3Dbar'
    >>> escape_uri_path('/I ♥ MiniDjango/')
    '/I%20%E2%99%A5%20MiniDjango/'
    """
    # These are the "reserved" and "unreserved" characters 
    # specified in sections 2.2 and 2.3 of RFC 2396:
    #   reserved    = ";"|"/"|"?"|":"|"@"|"&"|"="|"+"|"$"|","
    #   unreserved  = alphanum|mark
    #   mark        = "-"|"_"|"."|"!"|"~"|"*"|"'"|"("|")"
    # The list of safe characters here is constructed subtracting 
    # ";", "=", and "?" according to section 3.3 of RFC 2396.
    # The reason for not subtracting and escaping "/" is that 
    # we are escaping the entire path, not a path segment.
    return quote(path, safe="/:@&+$,-_.!~*'()")


def iri_to_uri(iri):
    """
    Convert an Internationalized Resource Identifier (IRI)
    portion to a URI portion that is suitable for inclusion
    in a URL.

    This is the algorithm from section 3.1 of RFC 3987.
    However, since we are assuming input is either UTF-8
    or unicode already, we can simplify things a little
    from the full method.

    >>> iri_to_uri('/I \xe2\x99\xa5 MiniDjango/?foo=bar')
    '/I%20%C3%A2%C2%99%C2%A5%20MiniDjango/?foo=bar'
    >>> iri_to_uri('/I ♥ MiniDjango/')
    '/I%20%E2%99%A5%20MiniDjango/'
    """
    # The list of safe characters here is constructed from
    # the "reserved" and "unreserved" characters specified
    # in sections 2.2 and 2.3 of RFC 3986:
    #     reserved    = gen-delims/sub-delims
    #     gen-delims  = ":"/"/"/"?"/"#"/"["/"]"/"@"
    #     sub-delims  = "!"/"$"/"&"/"'"/"("/")"
    #                  /"*"/"+"/","/";"/"="
    #     unreserved  = ALPHA/DIGIT/"-"/"."/"_"/"~"
    # Of the unreserved characters, urllib.quote already
    # considers all but the ~ safe.
    # The % character is also added to the list of safe
    # characters here, as the end of section 3.1 of RFC 3987
    # specifically mentions that % must not be converted.
    return quote(iri, safe="/#%[]=:;$&()+,!?*@'~")
