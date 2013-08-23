#coding=utf-8
import urllib
import urllib2
import xml.etree.ElementTree as ET
import json
import shutil
import os
import sys
import getopt

def xmlfile(url):
    return 'xml' + os.sep + url[url.rfind('/'):]
def clear():
    shutil.rmtree('xml')
def saveWeatchXML(url, file):
    req = urllib2.Request(url)
    try:
        conn = urllib2.urlopen(req)
    except urllib2.URLError, e:
        print 'URLError:', e
    except urllib2.HTTPError, e:
        print 'HTTP Error:', e
    with open(file, 'wb') as f:
        f.write(conn.read())
        f.close()

def parseCountryXML(xml, province):
    url = 'http://flash.weather.com.cn/wmaps/xml/%s.xml'
    root = ET.fromstring(xml)
    for c in root.getchildren():
        name = c.attrib['quName'].encode('gbk')
        if name == province:
            return (url % c.attrib['pyName'])
def parseProvinceXML(xml, city):
    root = ET.fromstring(xml)
    for c in root.getchildren():
        name = c.attrib['cityname'].encode('gbk')
        if name == city:
            return c.attrib['url']

def reqWeatherInfo(url):
    url = 'http://m.weather.com.cn/data/%s.html' % url
    req = urllib2.Request(url)
    try:
        conn = urllib2.urlopen(req)
    except urllib2.URLError, e:
        print 'URLError:', e
    except urllib2.HTTPError, e:
        print 'HTTP Error:', e
    weather = json.loads(conn.read())
    w = {}
    w['city'] = weather['weatherinfo']['city']
    #weather['weatherinfo']['city_en']
    w['date'] = weather['weatherinfo']['date_y']
    w['week'] = weather['weatherinfo']['week']
    #weather['weatherinfo']['cityid']
    #temp,tempF, weather,wind and fl from 1 to 6 are in the 6 days from now.
    #we need today so that is temp1, weather1, wind1 
    w['temprature'] = weather['weatherinfo']['temp1']
    w['weather'] = weather['weatherinfo']['weather1']
    w['wind'] = weather['weatherinfo']['wind1']
    w['wind_level'] = weather['weatherinfo']['fl1']
    #img1-img6 is the picture to descript the weather
    #img_title1-6 is the image tip.
    #we ignore them
    #index and index_d both are wearing tips.
    #index_d is more than index so we use it!
    w['wear'] = weather['weatherinfo']['index_d']
    #index48 and index48_d are wearing tips in 48 hours.
    #we ignore them.
    w['ultraviolet'] = weather['weatherinfo']['index_uv']
    #index48_uv is ultraviolet tip in 48 hours.
    #we ignore it.
    w['car_washing'] = weather['weatherinfo']['index_xc']
    w['travel'] = weather['weatherinfo']['index_tr']
    w['comfortable'] = weather['weatherinfo']['index_co']
    #st from 1 to 6 are unknow.
    w['morning_exercise'] = weather['weatherinfo']['index_cl']
    w['air'] = weather['weatherinfo']['index_ls']
    w['allergy'] = weather['weatherinfo']['index_ag']
    return w

def help():
    print '''USAGE:
%s [-d|--delete] -p|--province string -c|--city city
--delete clean cache
--province province name
--city city name
''' % sys.argv[0]
def main():
    clean = False
    city = ''
    province = ''
    if len(sys.argv) == 0:
        return

    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:c:dh", ["province", "city", "delete","help"])
        for o, a in opts:
            if o in ('-h', '--help'):
                help()
                return 0
            if o in ('-d', '--delete'):
                clean = True
            if o in ('-p', '--province'):
                province = a
            if o in ('-c', '--city'):
                city = a
    except:
        help()
        return 0

    if clean:
        clear()
    if len(province) == 0 or len(city) == 0:
        help()
        return 0
    try:
        os.mkdir('xml')
    except:
        pass
    url = 'http://flash.weather.com.cn/wmaps/xml/china.xml'
    file = xmlfile(url)
    if os.path.isfile(file) is False:
        saveWeatchXML(url, file)
    with open(file, 'rb') as f:
        url = parseCountryXML(f.read(), province)
        f.close()
    if url is None:
        return 1
    file = xmlfile(url)
    if os.path.isfile(file) is False:
        saveWeatchXML(url, file)
    with open(file, 'rb') as f:
        url = parseProvinceXML(f.read(), city)
        f.close()
    w = reqWeatherInfo(url)
    print w['city'], w['date'], w['week']
    print w['weather'], w['temprature'],w['wind']
    print '紫外线:'.decode('utf8'),w['ultraviolet']
    print '舒适度:'.decode('utf8'),w['comfortable']
    print '晾晒:'.decode('utf8'),w['air']
    print '旅游:'.decode('utf8'),w['travel']
    print '过敏:'.decode('utf8'),w['allergy']
    print '洗车:'.decode('utf8'),w['car_washing']
    print '穿衣:'.decode('utf8'),w['wear']
    print '晨练:'.decode('utf8'),w['morning_exercise']



if __name__ == '__main__':
    exit(main())
