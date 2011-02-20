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
    final static String HEXES = "0123456789ABCDEF";
    
    public static String toHex(byte[] array) {
        return toHex(array, null);
    }
    
    public static String toHex(byte[] array, String byteSeparator) {
        final StringBuilder hex = new StringBuilder(2 * array.length);
        for (final byte b : array) {
            hex.append(HEXES.charAt((b & 0xF0) >> 4)).append(HEXES.charAt((b & 0x0F)));
            if (byteSeparator != null)
                hex.append(byteSeparator);
        }
        return hex.toString();
    }
    
    public static byte[] fromHex(String hex) {
        return fromHex(hex, "");
    }
    
    public static byte[] fromHex(String hex, String byteSeparator) {
        String tightHex = hex.replaceAll(byteSeparator, "");
        int noBytes = (tightHex.length() + 1) / 2;
        byte[] bytes = new byte[noBytes];
        for (int i = 0; i < noBytes; ++i) {
            bytes[i] = (byte) ((HEXES.indexOf(tightHex.charAt(i*2)) << 4) | (HEXES.indexOf(tightHex.charAt(i*2+1))));
        }
        return bytes;
    }
}
