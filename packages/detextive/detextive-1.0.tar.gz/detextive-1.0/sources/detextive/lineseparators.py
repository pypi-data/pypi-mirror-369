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


''' Line separator enumeration and utilities. '''


from . import __


class LineSeparators( __.enum.Enum ):
    ''' Line separators for cross-platform text processing. '''

    CR =    '\r'    # Classic MacOS (0xD)
    CRLF =  '\r\n'  # DOS/Windows (0xD 0xA)
    LF =    '\n'    # Unix/Linux (0xA)

    @classmethod
    def detect_bytes(
        selfclass,
        content: __.cabc.Sequence[ int ] | bytes,
        limit: int = 1024
    ) -> __.typx.Optional[ 'LineSeparators' ]:
        ''' Detects line separator from byte content sample.

            Returns detected LineSeparators enum member or None.
        '''
        sample = content[ : limit ]
        found_cr = False
        for byte in sample:
            match byte:
                case 0xd:  # carriage return
                    if found_cr: return selfclass.CR
                    found_cr = True
                case 0xa:  # linefeed
                    if found_cr: return selfclass.CRLF
                    return selfclass.LF
                case _:
                    if found_cr: return selfclass.CR
        return None

    @classmethod
    def normalize_universal( selfclass, content: str ) -> str:
        ''' Normalizes all line separators to Unix LF format. '''
        return content.replace( '\r\n', '\r' ).replace( '\r', '\n' )

    def normalize( self, content: str ) -> str:
        ''' Normalizes specific line separator to Unix LF format. '''
        if LineSeparators.LF is self: return content
        return content.replace( self.value, '\n' )

    def nativize( self, content: str ) -> str:
        ''' Converts Unix LF to this platform's line separator. '''
        if LineSeparators.LF is self: return content
        return content.replace( '\n', self.value )
