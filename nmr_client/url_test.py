"""
Created by Michal Kononenko
Tests the TopChef server connectivity by pulling JSON from the root endpoint of the TopChef API
"""
import java.net
import java.io

url = java.net.URL('http://192.168.1.39')

conn = url.openConnection()

reader = java.io.BufferedReader(java.io.InputStreamReader(conn.getInputStream()))

input_line = reader.readLine()
data = []

while input_line is not None:
	data.append(str(input_line))
	input_line = reader.readLine()

datadict = eval(''.join(data)) # This is evil. We will replace this with simplejson

MSG(str(datadict))
