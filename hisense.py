#!/usr/bin/env python3

from socket import *
from select import select
from time import sleep
import sys
from getopt import getopt, GetoptError

class CM(object):
	def __init__(self, host, inputs, outputs):
		self.host = host
		self.inputs = inputs
		self.outputs = outputs
		print('cm_open_connection: ', host)
		self.sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self.sock.setblocking(0)
		self.inputs.append(self)
		self.outputs.append(self)
		self.state = 0

	def write(self):
		if self.state == 0:
			print('cm_send: ', b'CTCREATE\r\nID: 93901743\r\n\r\n\0')
			self.sock.sendto(b'CTCREATE\r\nID: 93901743\r\n\r\n\0', self.host)
			self.outputs.remove(self)
			self.state += 1

	def read(self):
		try:
			data,server = self.sock.recvfrom(1024)
			print('cm_read: ', data)
		except timeout:
			print('cm_timeout')
		else:
			if self.state == 1:
				ctportnum = int(data.rstrip('\0\r\n').split('\r\n')[1].split(':')[1].strip(' '))
				CT((self.host[0], ctportnum), self.inputs, self.outputs)
				self.state += 1

	def fileno(self):
		return self.sock.fileno()

class CT(object):
	def __init__(self, host, inputs, outputs):
		self.host = host
		self.inputs = inputs
		self.outputs = outputs
		print('ct_open_connection: ', host)
		self.sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self.sock.setblocking(0)
		self.inputs.append(self)
		self.outputs.append(self)
		self.state = 0

	def write(self):
		if self.state == 0:
			print('ct_send: ', b'SUS\0')
			self.sock.sendto(b'SUS\0', self.host)
			self.state += 1
		elif self.state == 1:
			print('ct_send: ', b'CTCREATE\r\nMAC: appmac_appmac_app\r\nVERSION: 0001\r\n\r\n\0')
			self.sock.sendto(b'CTCREATE\r\nMAC: appmac_appmac_app\r\nVERSION: 0001\r\n\r\n\0', self.host)
			self.outputs.remove(self)
			self.state += 1
		elif self.state == 3:
			print('ct_send: ', b'CCCREATE\r\nID: 93901743\r\n\r\n\0')
			self.sock.sendto(b'CCCREATE\r\nID: 93901743\r\n\r\n\0', self.host)
			self.outputs.remove(self)
			self.state += 1

	def read(self):
		try:
			data,server = self.sock.recvfrom(1024)
			print('ct_read: ', data)
		except timeout:
			print('ct_timeout')
		else:
			if self.state == 2:
				self.outputs.append(self)
				self.state += 1
			elif self.state == 4:
				ccportnum = int(data.rstrip('\0\r\n').split('\r\n')[1].split(':')[1].strip(' '))
				CC((self.host[0], ccportnum), self.inputs, self.outputs)
				self.state += 1

	def fileno(self):
		return self.sock.fileno()

class CC(object):
	keyloop = 0
	# keylist = (
	# 	b'KEY_VOLUMEUP', \
	# 	b'KEY_INPUT', \
	# 	b'KEY_INPUT1', \
	# 	b'KEY_INPUT_1', \
	# 	b'KEY_INPUT2', \
	# 	b'KEY_INPUT_2', \
	# 	b'KEY_MODE', \
	# 	b'KEY_MODE1', \
	# 	b'KEY_MODE_1', \
	# 	b'KEY_MODE2', \
	# 	b'KEY_MODE_2', \
	# 	b'KEY_SOURCE', \
	# 	b'KEY_SOURCE1', \
	# 	b'KEY_SOURCE_1', \
	# 	b'KEY_SOURCE2', \
	# 	b'KEY_SOURCE_2', \
	# 	b'KEY_HDMI', \
	# 	b'KEY_HDMI1', \
	# 	b'KEY_HDMI_1', \
	# 	b'KEY_HDMI2', \
	# 	b'KEY_HDMI_2', \
	# 	b'KEY_LIVETV', \
	# 	b'KEY_LIVE_TV', \
	# 	b'KEY_LIVE', \
	# 	b'KEY_TVLIVE', \
	# 	b'KEY_TV_LIVE', \
	# 	b'KEY_MUTE', \
	# 	b'KEY_MUTING', \
	# 	b'KEY_SLEEPTIMER', \
	# 	b'KEY_TIMER', \
	# 	b'KEY_TIMEOUT', \
	# 	b'KEY_TIMEOFF', \
	# 	b'KEY_APP', \
	# 	b'KEY_APPS', \
	# 	b'KEY_APPLICATIONS', \
	# 	b'KEY_PROG', \
	# 	b'KEY_PROGS', \
	# 	b'KEY_PROGRAMS', \
	# 	b'KEY_FN')


	def __init__(self, host, inputs, outputs):
		self.host = host
		self.inputs = inputs
		self.outputs = outputs
		print('cc_open_connection:', host)
		self.sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self.sock.setblocking(0)
		self.inputs.append(self)
		self.outputs.append(self)
		self.state = 0

	def write(self):
		if self.state == 0:
			print ('cc_send: ', b'SUS\0')
			self.sock.sendto(b'SUS\0', self.host)
			self.state += 1
		elif self.state == 1:

			# This should be handled more gracefully...
			opts, args = getopt(sys.argv[1:], "ld:", ["list", "device="])

			if (self.keyloop >= len(args)):
				print('no further input, exiting')
				sys.exit(0)
			key = args[self.keyloop]
			mylen = len(key) + 129
			mylenstr = str(mylen).zfill(6).encode()
			print('cc_send: ', b'CMD %s\r\n1\r\n1HISENSE_DELIMITER2HISENSE_DELIMITER2HISENSE_DELIMITER%sHISENSE_DELIMITER10HISENSE_DELIMITER0HISENSE_DELIMITER0\r\n\r\n\0' % (mylenstr, key))
			self.sock.sendto(b'CMD %s\r\n1\r\n1HISENSE_DELIMITER2HISENSE_DELIMITER2HISENSE_DELIMITER%sHISENSE_DELIMITER10HISENSE_DELIMITER0HISENSE_DELIMITER0\r\n\r\n\0' % (mylenstr, key), self.host)

			self.keyloop += 1
			# sleep(0.5)
			# self.outputs.remove(self)
			# self.state += 1
		elif self.state == 3:
			self.sock.sendto(b'END 0000\r\n', self.host)
			self.outputs.remove(self)
			self.state += 1

	def read(self):
		try:
			data,server = self.sock.recvfrom(1024)
			print('cc_read: ', data)
		except timeout:
			print('cc_timeout')
		else:
			if self.state == 2:
				self.outputs.append(self)
				self.state += 1
			elif self.state == 4:
				exit()

	def fileno(self):
		return self.sock.fileno()

class HisenseDataObject:
	def __init__(self, method=None, version=None, redundantip=None, tvdescriptor=None, extra=None):
		self.method = method
		self.version = version
		self.redundantip = redundantip
		self.tvdescriptor = tvdescriptor
		self.extra = extra

	def __repr__(self):
		return "<HisenseDataObject method:%s version:%s redundantip:%s tvdescriptor:%s extra:%s>" % (
			self.method, self.version, self.redundantip, self.tvdescriptor, self.extra)

	@staticmethod
	def fromString(input):
		hdo = HisenseDataObject()
		hdo.method, hdo.version, hdo.redundantip, hdo.tvdescriptor, hdo.extra = (input.split('#',4) + [None]*4)[:5]
		hdo.version = hdo.version if hdo.version != '' else None
		return hdo

	def __str__(self):
		return "%s#%s%s%s%s" % (self.method, \
			self.version if self.version != None else '', \
			'#'+self.redundantip if self.redundantip != None else '', \
			'#'+self.tvdescriptor if self.tvdescriptor != None else '', \
			'#'+self.extra if self.extra != None else '')

	def encode(self):
		return (str(self)).encode()

class HisenseTV(object):
	@staticmethod
	def discover():
		tvlist = {}
		s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		s.settimeout(0.2)
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		s.bind(('', 54321))
		s.sendto(HisenseDataObject('DISCOVERY').encode(), ('<broadcast>', 50000))
		while True:
			try:
				data,server = s.recvfrom(1024)
				tvlist[server[0]] = HisenseDataObject.fromString(str(data))
			except timeout:
				break
		return tvlist

# tvlist = HisenseTV.discover()
# print(tvlist)

def usage():
	print ("-l (--list):	Send a broadcast to discover available devices\n")
	print ("-d (--device):	[INCOMPLETE] Pass specific device IP address (useful if more than one on the network)\n")
	print ("any other input(s) are considered commands to send to the TV\n")
	sys.exit()

def main(argv):
	device = None
	try:
		opts, args = getopt(argv, "ld:", ["list", "device="])
	except GetoptError:
		usage()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-l", "--list"):
			print(HisenseTV.discover())
			sys.exit()
		elif opt in ("-d", "--device"):
			device = args
	if device == None:
		devices = HisenseTV.discover()
		if (len(devices) == 0):
			print("No devices found!")
			sys.exit(2)
		elif (len(devices) > 1):
			print("Multiple devices found, please use -d to specify which one")
			sys.exit(2)
		device = next(iter(devices))

	inputs = []
	outputs = []
	CM((device, 60030), inputs, outputs)

	while inputs:
		readable, writable, exceptional = select(inputs, outputs, inputs)
		for s in readable:
			# print('readable', s)
			s.read()
		for s in writable:
			# print ('writable', s)
			s.write()
		for s in exceptional:
			print ('exceptional', s)








if __name__ == "__main__":
	main(sys.argv[1:])
