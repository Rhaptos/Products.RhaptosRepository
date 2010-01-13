## Script (Python) "weeklySubmits"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=interval='1 week', end_date="now"
##title=
##
modules = context.getPastSubmits(interval=interval, end_date=end_date)

params = context.parseDateInterval(date=end_date, interval=interval)

print "Modules submitted in past %s (%s - %s)" % (interval,(DateTime(str(params[0].datetime)) - int(params[0].days)).Date(), DateTime(str(params[0].datetime)).Date())
#print "Modules submitted in past %s" % (interval)

if modules:
	maxname=len(modules[0].name)

	for m in modules:
	  if len(m.name) > maxname:
	    namewidth=len(m.name)

	namewidth=maxname;

	if namewidth > 60:
	  namewidth=60

	fmt = "%-6s %4d submits: %-*s %-s"
	fmt2 = "                     %-s"

	current = ''
	for m in modules:
	  if m.moduleid != current:
	    current = m.moduleid
	    print
	    print '-'*80
	    namewidth=len(m.name)
	    if namewidth > 60:
	      namewidth=60
	    print fmt % (m.moduleid, m.count, namewidth, m.name[:60], m.authors)
	    if namewidth==60:
	      i=1
	      while(i*60<len(m.name)):
	        print fmt2 % m.name[60*i:60*(i+1)]
		i+=1
	  print "  %s %s %s" % (m.submitter or '<?>',m.revised,(m.submitlog or "").rstrip())

return printed
