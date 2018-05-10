import logging
import socket

import channelsimulator
import utils
import sys
import sender
import receiver


se = sender.Sender()
re = receiver.Receiver()
se.send('Hello Karol')
re.receive()