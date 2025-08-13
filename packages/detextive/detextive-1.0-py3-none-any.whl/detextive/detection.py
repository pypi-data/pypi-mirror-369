# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Core detection function implementations. '''


from . import __
from . import exceptions as _exceptions


Content: __.typx.TypeAlias = __.typx.Annotated[
    bytes,
    __.ddoc.Doc( "Raw byte content for analysis." )
]
Location: __.typx.TypeAlias = __.typx.Annotated[
    str | __.Path,
    __.ddoc.Doc( "File path, URL, or path components for context." )
]

_TEXTUAL_MIME_TYPES = frozenset( (
    'application/ecmascript',
    'application/graphql',
    'application/javascript',
    'application/json',
    'application/ld+json',
    'application/x-httpd-php',
    'application/x-javascript',
    'application/x-latex',
    'application/x-perl',
    'application/x-php',
    'application/x-python',
    'application/x-ruby',
    'application/x-shell',
    'application/x-tex',
    'application/x-yaml',
    'application/xhtml+xml',
    'application/xml',
    'application/yaml',
    'image/svg+xml',
) )
_TEXTUAL_SUFFIXES = ( '+xml', '+json', '+yaml', '+toml' )


def detect_charset( content: Content ) -> __.typx.Optional[ str ]:
    ''' Detects character encoding with UTF-8 preference and validation.

        Returns None if no reliable encoding can be determined.
    '''
    result = __.chardet.detect( content )
    charset = result[ 'encoding' ]
    if charset is None: return charset
    if charset.startswith( 'utf' ): return charset
    match charset:
        case 'ascii': return 'utf-8'  # Assume superset
        case _: pass
    # Shake out false positives, like 'MacRoman'
    try: content.decode( 'utf-8' )
    except UnicodeDecodeError: return charset
    return 'utf-8'


def detect_mimetype(
    content: Content,
    location: Location
) -> __.typx.Optional[ str ]:
    ''' Detects MIME type using content analysis and extension fallback.

        Returns standardized MIME type strings or None if detection fails.
    '''
    try: return __.puremagic.from_string( content, mime = True )
    except ( __.puremagic.PureError, ValueError ):
        return __.mimetypes.guess_type( str( location ) )[ 0 ]


def detect_mimetype_and_charset(
    content: Content,
    location: Location, *,
    mimetype: __.Absential[ str ] = __.absent,
    charset: __.Absential[ str ] = __.absent,
) -> tuple[ str, __.typx.Optional[ str ] ]:
    ''' Detects MIME type and charset with optional parameter overrides.

        Returns tuple of (mimetype, charset). MIME type defaults to
        'text/plain' if charset detected but MIME type unknown, or
        'application/octet-stream' if neither detected.
    '''
    mimetype_ = (
        detect_mimetype( content, location )
        if __.is_absent( mimetype ) else mimetype )
    charset_ = (
        detect_charset( content ) if __.is_absent( charset ) else charset )
    if not mimetype_:
        if charset_:
            mimetype_ = 'text/plain'
            try:
                _validate_mimetype_with_trial_decode(
                    content, str( location ), mimetype_, charset_ )
            except _exceptions.TextualMimetypeInvalidity: pass
            else: return mimetype_, charset_
        mimetype_ = 'application/octet-stream'
    if is_textual_mimetype( mimetype_ ): return mimetype_, charset_
    if not __.is_absent( charset ):
        _validate_mimetype_with_trial_decode(
            content, str( location ), mimetype_, charset )
        return mimetype_, charset
    return mimetype_, None  # no charset for non-textual content


def is_textual_mimetype( mimetype: str ) -> bool:
    ''' Validates if MIME type represents textual content.

        Consolidates textual MIME type patterns from all source
        implementations. Supports text/* prefix, specific application
        types (JSON, XML, JavaScript, etc.), and textual suffixes
        (+xml, +json, +yaml, +toml).

        Returns True for MIME types representing textual content.
    '''
    if mimetype.startswith( ( 'text/', 'text/x-' ) ): return True
    if mimetype in _TEXTUAL_MIME_TYPES: return True
    return mimetype.endswith( _TEXTUAL_SUFFIXES )


def is_textual_content( content: bytes ) -> bool:
    ''' Determines if byte content represents textual data.

        Returns True for content that can be reliably processed as text.
    '''
    mimetype, charset = detect_mimetype_and_charset( content, 'unknown' )
    return charset is not None and is_textual_mimetype( mimetype )


def _is_probable_textual_content( content: str ) -> bool:
    ''' Validates decoded content using heuristic analysis.

        Applies heuristics to detect meaningful text vs binary data:
        - Limits control characters to <10% (excluding common whitespace)
        - Requires >=80% printable characters

        Returns True for content likely to be meaningful text.
    '''
    if not content: return False
    common_whitespace = '\t\n\r'
    ascii_control_limit = 32
    control_chars = sum(
        1 for c in content
        if ord( c ) < ascii_control_limit and c not in common_whitespace )
    if control_chars > len( content ) * 0.1: return False
    printable_chars = sum(
        1 for c in content
        if c.isprintable( ) or c in common_whitespace )
    return printable_chars >= len( content ) * 0.8


def _validate_mimetype_with_trial_decode(
    content: bytes, location: Location, mimetype: str, charset: str
) -> None:
    ''' Validates charset fallback and returns appropriate MIME type. '''
    try: text = content.decode( charset )
    except ( UnicodeDecodeError, LookupError ) as exc:
        raise _exceptions.TextualMimetypeInvalidity(
            str( location ), mimetype ) from exc
    if not _is_probable_textual_content( text ):
        raise _exceptions.TextualMimetypeInvalidity(
            str( location ), mimetype )
