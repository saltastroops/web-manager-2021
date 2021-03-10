import hashlib
import pathlib
from functools import cache
from urllib.parse import urlparse


def _autoversion_hash(file_path: pathlib.Path) -> str:
    """Calculate the MD5 hash for a binary file-like object."""

    md5 = hashlib.md5()  # nosec
    with open(file_path, "rb") as f:
        content = f.read()
    md5.update(content)

    return md5.hexdigest()


@cache
def autoversion(url: str) -> str:
    """
    Append the file hash as a version query parameter.

    This filter adds a query parameter v to the url whose value is the hash of the file
    to which the url is pointing. For example, if the url is

    https://example.com/static/css/main.css

    the filter returns a string like

    https://example.com/static/css/main.css?v=8e3249d1ed722a56ca3dfc0536accc33

    Using this new string as the URL solves the caching issue for static files, as the
    value of the query parameter will change whenever the file is modified.

    The filter should handle all normal URLs correctly, but might fail for edge cases
    which are not relevant for URLS of static files. However, relative file paths are
    not allowed as URL, nor are directories.

    You can use the filter as follows in a Jinja2 template:

    {{ 'https://example.com/static/css/main.css' | autoversion }}

    This function is based on
    https://ana-balica.github.io/2014/02/01/autoversioning-static-assets-in-flask/.

    """

    # get the file path
    o = urlparse(url)
    path = o.path if o.path else "/"

    # relative file paths are not allowed
    if not path.startswith("/"):
        raise ValueError(
            f"The autoversion filter does not accept relative file paths: {path}"
        )

    # check the file exidts and is no directory
    file_path = pathlib.Path(path[1:])
    if not file_path.exists():
        raise IOError(f"The file {file_path.absolute()} does not exist.")
    if file_path.is_dir():
        raise ValueError(
            f"The autoversion filter does not accept directories: "
            f"{file_path.absolute()}"
        )

    # add the version query parameter
    hash_value = _autoversion_hash(file_path)
    query = o.query
    if query:
        query += f"&v={hash_value}"
    else:
        query = f"v={hash_value}"

    scheme_string = f"{o.scheme}://" if o.scheme else ""
    params_string = f";{o.params}" if o.params else ""
    query_string = f"?{query}" if query else ""
    fragment_string = f"#{o.fragment}" if o.fragment else ""

    return (
        scheme_string
        + o.netloc
        + o.path
        + params_string
        + query_string
        + fragment_string
    )
