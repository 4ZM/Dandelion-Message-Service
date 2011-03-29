#!/bin/bash


SSID=$(zenity --entry --text "SSID of the network" --title "SSID")
KEY=$(zenity --entry --text "Encryption key" --title "KEY")

WIFNAME=$(gksudo iwconfig |grep "IEEE 802.11" |awk '{print $1}')

if [ -z $WIFNAME ]; then
	zenity --error --title "NO WIRELESS INTERFACE" --text "ERROR: You don't have any wireless network interface"
	exit 1
else
	echo gksudo ifconfig $WIFNAME down
	echo gksudo iwconfig mode Ad-Hoc essid $SSID key s:$KEY
	echo gksudo avahi-autoipd --check $WIFNAME 
	if [ "$?" == "0" ]; then
		echo gksudo avahi-autoipd --refresh $WIFNAME
	else
		echo gksudo avahi-autoipd -D $WIFNAME
	fi
fi
