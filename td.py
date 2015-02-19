import requests, json, os, argparse, sys, time

reload(sys)
sys.setdefaultencoding("UTF8")

parser = argparse.ArgumentParser()
parser.add_argument('--offset', dest='offset', metavar='OFFSET',
                    action='store') 
parser.add_argument('--day', dest='day', metavar='DAY',
                    action='store')
parser.add_argument('--month', dest='month', metavar='MONTH',
                    action='store')
args = parser.parse_args()

day = 0
month = 1

if args.day :
	day = int(args.day) - 1
if args.month :
	month = int(args.month)
if args.offset :
	argoffset = int(args.offset)

while month < 13 :
	
	offset = 0
	
	if args.offset :
		offset = offset + argoffset
		argoffset = 0
	
	day = day + 1
	if day > 31 :
		day = 1
		month = month + 1

	td = '/Users/Dominic/GitHub/Dominic-MP.github.io/td' + str(month) + '-' + str(day) + '.html'
	
	geturl = 'https://catalog.archives.gov/api/v1/?resultTypes=item,fileUnit&description.item.productionDateArray.proposableQualifiableDate.month=' + str(month) + '&description.item.productionDateArray.proposableQualifiableDate.day=' + str(day) + '&resultFields=description.item.productionDateArray.proposableQualifiableDate.day,description.item.productionDateArray.proposableQualifiableDate.month,description.item.productionDateArray.proposableQualifiableDate.year,description.item.title,naId,objects&rows=1'

	y = requests.get(geturl)
	parsed = json.loads(y.text)
	
	results = parsed['opaResponse']['results']['total']
	if results > 500 :
		results = 500
	
	print 'There are ' + str(parsed['opaResponse']['results']['total']) + ' anniversary records for ' + str(month) + '-' + str(day) + '.'
	
	while int(offset) < int(results) :
	
		if int(offset) == 0 :
			writefile = open(td, 'w')
			writefile.write( ('<html>\n<head>\n<title>NARA records with anniversaries</title>\n</head>\n<body>\n<p><a href="td.html">return<a></p>\n\n<h1 align="center">NARA records with anniversaries</h1>\n\n<table style="width:100%" border="1">\n  <tr style="text-align:center">\n    <td>Date</td>\n    <td>Year</td>\n    <td>Thumbnail</td>\n    <td>NAID</td>\n    <td>Title</td>\n  </tr>') )
			writefile.close()

		url = 'https://catalog.archives.gov/api/v1/?resultTypes=item,fileUnit&description.item.productionDateArray.proposableQualifiableDate.month=' + str(month) + '&description.item.productionDateArray.proposableQualifiableDate.day=' + str(day) + '&resultFields=description.item.productionDateArray.proposableQualifiableDate.day,description.item.productionDateArray.proposableQualifiableDate.month,description.item.productionDateArray.proposableQualifiableDate.year,description.item.title,naId,objects&rows=1&sort=naId asc&offset=' + str(offset)
						
		try :	
			z = requests.get(url)
			parse = json.loads(z.text)
		except requests.exceptions.ConnectionError :
			print requests.get(url).status_code
			print requests.get(url).headers
		except ValueError :
			print 'Received 500 error! Sleeping...'
			time.sleep(1205)
			z = requests.get(url)
			parse = json.loads(z.text)
		
		print '\n----\n' + str(offset)
		print url
		
		try :
			NAID = parse['opaResponse']['results']['result'][0]['naId']
			title = parse['opaResponse']['results']['result'][0]['description']['item']['title']
			year = parse['opaResponse']['results']['result'][0]['description']['item']['productionDateArray']['proposableQualifiableDate']['year']
		except :
			print z.text
			pass
		try :
			fileurl = parse['opaResponse']['results']['result'][0]['objects']['object']['thumbnail']['@url'].replace('govOpaAPI', 'gov/OpaAPI')
#			filename = parse['opaResponse']['results']['result'][0]['objects']['object']['file']['@name']
		except TypeError :
			try:
				fileurl = parse['opaResponse']['results']['result'][0]['objects']['object'][0]['thumbnail']['@url'].replace('govOpaAPI', 'gov/OpaAPI')
#			filename = parse['opaResponse']['results']['result'][0]['objects']['object'][0]['file']['@name']
				print fileurl
			
			except KeyError :
				print 'No thumbnail found!\n----'
				offset = offset + 1
				continue
				
		except KeyError :
			print 'No thumbnail found!\n----'
			offset = offset + 1
			continue
		
		print '\n' + str(month) + '-' + str(day) + '\n' + str(year) + '\n' + str(NAID) + '\n' + title.encode('utf-8') + '\n' + fileurl
		
		if int(year[-1:]) == 0 or int(year[-1:]) == 5 :
			print 'Match found!\n'
			writefile = open(td, 'a')
			writefile.write( ('\n  <tr style="text-align:center">\n    <td>' + str(month) + '-' + str(day) + '</td>\n    <td>' + str(year) + '</td>\n    <td><img src="' + fileurl + '"/></td>\n    <td><a href="https://catalog.archives.gov/id/' + str(NAID) + '">' + str(NAID) + '</a></td>\n    <td style="text-align:left">' + title.encode('utf-8') + '</td>\n  </tr>') )

		print '----'
		offset = offset + 1
	
	writefile = open(td, 'a')
	writefile.write( ('</table>\n</body>\n</html>') )
	writefile.close()
