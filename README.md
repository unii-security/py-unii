# Python library to interface with Alphatronics UNii security systems

![logo](https://raw.githubusercontent.com/unii-security/py-unii/main/logo.png)

## Introduction

The UNii is a modular intrusion and access control system that is designed, developed and
manufactured by Alphatronics, the Netherlands. This innovative solution is distributed and
supported via the professional (security) installer and wholesalers.

This library is still in **beta** and **subject to change**. We're looking forward to your
feedback.

## Features

- Status inputs (clear, open, tamper, masking)
- Status sections (armed, disarmed, alarm) 
- Connection status UNii panel

Extra features (arming/disarming, (un)bypassing, outputs and event handling) are added shortly.

## Hardware

Tested with the UNii 32, 128 and 512. No additional UNii license needed.

It is recommended to use the latest possible firmware on your UNii to unlock the full potential of
the UNii and this integration.

## Configuring the UNii

In the UNii API configuration the following options need to be set:

- Type: Basic encryption
- Transmission: TCP
- Input update interval: 0s to have to fastest input response type. (Only for firmware version
  2.17.x and above)
- API version: UNii.

### Shared Key

The UNii uses an encrypted connection with Home Assistant. The shared key has to be entered in the
UNii (API settings) by the installer. Without installer access to the UNii end-users are **NOT**
able to enter this key. Contact your installer if applicable.

## Installation

You can install the Python UNii library using the Python package manager PIP:

`pip3 install unii`

## `unii` CLI

You can use the Python UNii library directly from the command line to read status updates using the
following syntax:

`python3 -m unii <host> <port> <key>`

### Troubleshooting

You can add the `--debug` flag to the CLI command to get a more details on what's going on. Like so:

`python3 -m unii <host> <port> <key> --debug`
