#!/bin/bash
# Copyright (c) 2011 Lars Larsson <lars.la@gmail.com>
# 
# This file is part of Dandelion Messaging System.
# 
# Dandelion is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Dandelion is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dandelion.  If not, see <http://www.gnu.org/licenses/>.

SSID=$(zenity --entry --text "SSID of the network" --title "SSID")

WIFNAME=$(gksudo iwconfig |grep "IEEE 802.11" |awk '{print $1}')

if [ -z $WIFNAME ]; then
	zenity --error --title "NO WIRELESS INTERFACE" --text "ERROR: You don't have any wireless network interface"
	exit 1
else
	gksudo "service network-manager stop"
	gksudo "ifconfig $WIFNAME down"
	gksudo "iwconfig $WIFNAME mode Ad-Hoc essid $SSID"
	gksudo "avahi-autoipd --check $WIFNAME"
	if [ "$?" == "0" ]; then
		gksudo "avahi-autoipd --refresh $WIFNAME"
	else
		gksudo "avahi-autoipd -D $WIFNAME"
	fi
fi
