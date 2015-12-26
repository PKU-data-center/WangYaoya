# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import Tool
import json
import sys
import MysqlHelper

reload(sys)
sys.setdefaultencoding('utf-8')

#数据库一条记录内容
class Item:
    def __init__(self):
		self.title = ""
		self.school = ""
		self.teacher = ""
		self.touxian = ""
		self.resume = ""
		self.hitcount = ""
		self.url = ""

#人卫慕课_公开课爬虫类
class pmphmooc:
	def __init__(self):
		self.tool = Tool.Tool()
		
	def getJson(self):
		try:
			url = 'http://www.pmphmooc.com/web/courselists'
			value = {'type':1}
			data = urllib.urlencode(value)
			request = urllib2.Request(url,data)
			response = urllib2.urlopen(request)
			content = json.loads(response.read())
			totalCount = content["page"]["totalCount"]
			values = {'type':1,'pageSize':totalCount}
			data = urllib.urlencode(values)
			request = urllib2.Request(url,data)
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接失败，错误原因",e.reason
				return None
				
	def start(self):
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		cur.execute('drop table if exists pmphmooc_open')
		cur.execute('create table pmphmooc_open(id int(11) primary key auto_increment,title varchar(255),school varchar(255),teacher varchar(255),touxian varchar(255),resume text,hitcount varchar(255),url varchar(255))')
		sql = 'insert into pmphmooc_open(title,school,teacher,touxian,resume,hitcount,url) values(%s,%s,%s,%s,%s,%s,%s)'
		content = json.loads(self.getJson())
		for item in content["rows"]:
			oneline = Item()
			oneline.title = item["name"]
			oneline.url = 'http://www.pmphmooc.com/web/opencoursedetail?courseid=' + str(item["id"])
			oneline.school = item["agencyname"]
			oneline.hitcount = item["hitcount"]
			if item.has_key("username"):
				oneline.teacher = item["username"]
			if item.has_key("touxian"):
				oneline.touxian = item["touxian"]
			if item.has_key("resume"):
				oneline.resume = item["resume"]
				
			value = []
			value.append(oneline.title)
			value.append(oneline.school)
			value.append(oneline.teacher)
			value.append(oneline.touxian)
			value.append(oneline.resume)
			value.append(oneline.hitcount)
			value.append(oneline.url)
			MysqlHelper.insert_one(cur,sql,value)
		MysqlHelper.finish(conn)
		
		
pmphmooc = pmphmooc()
pmphmooc.start()