#! /usr/bin/env python

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import subprocess

class CowtalkProtocol(LineReceiver):
    def __init__(self, users):
        self.users = users
        self.name = None
        # the state determines how dataReceived is handled
        # the exception is quit which overrides current state
        self.state = "GETNAME"

    def connectionMade(self):
        self.sendLine("Detective at keyboard, please enter your name.")

    def connectionLost(self, reason):
        self.sendLine("Goodbye!")
        if self.users.has_key(self.name):
            del self.users[self.name]
        for name, protocol in self.users.iteritems():
            protocol.sendLine("%s has disconnected" % self.name)

    def dataReceived(self, line):
        # we don't want to evaluate the newline
        line = line.rstrip()
        # in either case, we want to allow quitting:
        if line == 'q':
            self.transport.loseConnection() 
            return
        # we handle data differently depending on our state
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
        if self.users.has_key(name):
            self.sendLine("Name taken, please choose another.")
            return
        for other_name, protocol in self.users.iteritems():
            protocol.sendLine("%s has connected!" % name)
        self.name = name
        self.users[name] = self
        self.state = "CHAT"
        self.sendLine("Welcome, %s!" % name)

    def handle_CHAT(self, message):
        message = self.cowtalkify(message)
        message = "---%s---\n%s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)
                #for line in message:
                #    protocol.sendLine(line)

    def cowtalkify(self, message):
        # note: returns multiple lines
        outstr = subprocess.Popen(
                ["cowsay", message], stdout=subprocess.PIPE).communicate()
        return outstr[0]


class CowtalkFactory(Factory):
    protocol = CowtalkProtocol
    def __init__(self, greeting='Welcome!'):
        self.greeting = greeting
        self.users = {} 
    def buildProtocol(self, addr):
        return CowtalkProtocol(self.users)

# looks like a sideways M for MOOO
reactor.listenTCP(3000, CowtalkFactory())
reactor.run()
