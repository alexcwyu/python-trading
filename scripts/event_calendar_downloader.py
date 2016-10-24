# This will later become a provider of event
# TODO: move to provider
import urllib2
import datetime

# orig_link = 'https://www.dailyfx.com/files/Calendar-10-16-2016.xls'
template = 'https://www.dailyfx.com/files/Calendar-%s-%s-%s.xls'


last_date = datetime.date(2016,10,16)
missing_dates = []


curr_date = last_date




def download(date):
    date_str = date.isoformat()
    url = template % (date_str[5:7], date_str[8:10], date_str[:4])
    try:
        xls_file = urllib2.urlopen(url)
        print "downloaded %s" % date
        to_file = '/Volumes/Transcend/data/RawCalendar/%s.xls' % date
        with open(to_file, 'wb') as outfile:
            outfile.write(xls_file.read())
    except:
        print "404, can't download for %s" % date
        missing_dates.append(date)


while curr_date > datetime.date(2000,1,1):
    download(curr_date)
    curr_date = curr_date + datetime.timedelta(days=-7)
