// Copyright (c) 2011 Anders Sundman <anders@4zm.org>
//
// This file is part of the Riot Control Messaging System (RCMS).
//
// RCMS is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version. 
//
// The RCMS is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with the RCMS.  If not, see <http://www.gnu.org/licenses/>.

public class HexFormater {
    public static String toHex(byte[] array) {
        return toHex(array, null);
    }
    
    public static String toHex(byte[] array, String byteSeparator) {
        final String HEXES = "0123456789ABCDEF";
        final StringBuilder hex = new StringBuilder(2 * array.length);
        for (final byte b : array) {
            hex.append(HEXES.charAt((b & 0xF0) >> 4)).append(HEXES.charAt((b & 0x0F)));
            if (byteSeparator != null)
                hex.append(byteSeparator);
        }
        return hex.toString();
    }
}
