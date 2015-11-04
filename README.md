# gmail-empty-trash

Simple script to empty your gmail trash

Since the setting to automatically delete trash is not configurable

and only happens every 30 days, you can use this to empty your trash

on a more regular basis using a crontask.

## Setup

Follow the instructions here to generate a `client_secret.json` file and place it alongside the script.

https://developers.google.com/gmail/api/quickstart/python

## Usage

``` shell
$ pip install --upgrade google-api-python-client
$ python empty-trash.py
```

## Using launchd to automate it on OSX

Setup a `gmail-empty-trash.plist` file in `~/Library/LaunchAgents`

This setup will run the script every ten minutes.

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
   "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
 <plist version="1.0">
 <dict>
     <key>Label</key>
     <string>com.eric.gmail</string>
     <key>ProgramArguments</key>
     <array>
         <string>/path/to/python</string>
         <string>/path/to/script/empty-trash.py</string>
     </array>
     <key>StartInterval</key>
     <integer>600</integer>
 </dict>
 </plist>
```

Load the LaunchAgent

``` shell
$ launchctl load -w ~/Library/LaunchAgents/gmail-empty-trash.plist
```