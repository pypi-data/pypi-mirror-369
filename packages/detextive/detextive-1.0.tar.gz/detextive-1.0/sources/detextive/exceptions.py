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


''' Family of exceptions for package API. '''


from . import __


class Omniexception( BaseException ):
    ''' Base for all exceptions raised by package API. '''
    # TODO: Class and instance attribute concealment and immutability.

    _attribute_visibility_includes_: __.cabc.Collection[ str ] = (
        frozenset( ( '__cause__', '__context__', ) ) )


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class CharsetDetectFailure( Omnierror, RuntimeError ):
    ''' Character encoding detection fails. '''

    def __init__( self, location: str ) -> None:
        super( ).__init__(
            f"Character encoding detection failed for content at "
            f"'{location}'." )


class ContentDecodeFailure( Omnierror, UnicodeError ):
    ''' Content cannot be decoded with detected charset. '''

    def __init__( self, location: str, charset: str ) -> None:
        super( ).__init__(
            f"Content at '{location}' cannot be decoded using charset "
            f"'{charset}'." )


class TextualMimetypeInvalidity( Omnierror, ValueError ):
    ''' MIME type is invalid for textual content processing. '''

    def __init__( self, location: str, mimetype: str ) -> None:
        super( ).__init__(
            f"MIME type '{mimetype}' is not textual for content at "
            f"'{location}'." )
