# Copyright (C) 2012 W. Trevor King <wking@tremily.us>
#
# This file is part of pygor.
#
# pygor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pygor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pygor.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from ..binarywave import load_ibw
from . import Record


class WaveRecord(Record):
    def __init__(self, *args, **kwargs):
        super(WaveRecord, self).__init__(*args, **kwargs)
        self.wave = load_ibw(BytesIO(bytes(self.data)))

    def __str__(self):
        return str(self.wave)
