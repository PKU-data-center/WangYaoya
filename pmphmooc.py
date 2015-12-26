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
		self.description = ""
		self.chapter = ""
		self.course_begin = ""
		self.course_end = ""
		self.course_totaltime = ""
		self.course_load = ""
		self.teacher = ""
		self.block = ""
		self.url = ""

#人卫慕课爬虫类
class pmphmooc:
	def __init__(self):
		self.tool = Tool.Tool()
		
	def getJson(self):
		try:
			url = 'http://www.pmphmooc.com/web/courselists'
			value = {'type':0}
			data = urllib.urlencode(value)
			request = urllib2.Request(url,data)
			response = urllib2.urlopen(request)
			content = json.loads(response.read())
			totalCount = content["page"]["totalCount"]
			values = {'type':0,'pageSize':totalCount}
			data = urllib.urlencode(values)
			request = urllib2.Request(url,data)
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接失败，错误原因",e.reason
				return None
				
	def getPage(self,viewIndex):
		try:
			url = "http://www.pmphmooc.com/web/scholl/" + str(viewIndex)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接失败，错误原因",e.reason
				return None

	def getDescription(self,page):
		pattern = re.compile('<h3 class="title">.*?</h3>(.*?)<!--',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getBeginAndEnd(self,page):
		pattern = re.compile('<div class="class_time">.*?开课：(.*?)</p>.*?结课：(.*?)</p>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	def getTotalAndLoad(self,page):
		pattern = re.compile('<span class="cor_red">(.*?)</span>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	def getTeacher(self,page):
		pattern = re.compile('<div class="cnt f-fl">.*?<h3>(.*?)</h3>.*?<p>(.*?)</p>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	#获取内容所在的区块
	def getBlock(self,page):
		pattern = re.compile('<div class="inner-wrapper">(.*?)</div>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	#content为需要获取的内容
	def getInfo(self,page,content):
		pattern = re.compile('<strong>.*?' + content + '.*?</strong>(.*?)<strong>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getText(self,page,words):
		for item in words:
			result = self.getInfo(page,item)
			if result:
				return result
		return None
				
	def start(self):
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		cur.execute('drop table if exists pmphmooc')
		cur.execute('create table pmphmooc(id int(11) primary key auto_increment,title varchar(255),description text,chapter text,course_begin varchar(255),course_end varchar(255),course_totaltime varchar(255),course_load varchar(255),teacher text,block text,url varchar(255))')
		sql = 'insert into pmphmooc(title,description,chapter,course_begin,course_end,course_totaltime,course_load,teacher,block,url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		content = json.loads(self.getJson())
		for item in content["rows"]:
			oneline = Item()
			# print item["name"],item["id"]
			oneline.title = item["name"]
			oneline.url = 'http://www.pmphmooc.com/web/scholl/' + str(item["id"])
			page = self.getPage(item["id"])
			# print page
			description = self.getDescription(page)
			oneline.description = self.tool.replace(description)
			beginAndEnd = self.getBeginAndEnd(page)
			for item in beginAndEnd:
				oneline.course_begin = item[0]
				oneline.course_end = item[1]
			totalAndLoad = self.getTotalAndLoad(page)
			oneline.course_totaltime = totalAndLoad[0]
			oneline.course_load = totalAndLoad[1]
			teacher = self.getTeacher(page)
			teastr = ""
			for item in teacher:
				teastr = teastr + item[0] + '\n' + item[1] + '\n'
			oneline.teacher = teastr
			block = self.getBlock(page)
			oneline.block = block
			chapterWords = ["授课大纲","课程章节"]
			chapter = self.getText(block,chapterWords)
			if chapter:
				oneline.chapter = re.sub(self.tool.replaceNBSP,"",self.tool.replace(chapter))

			value = []
			value.append(oneline.title)
			value.append(oneline.description)
			value.append(oneline.chapter)
			value.append(oneline.course_begin)
			value.append(oneline.course_end)
			value.append(oneline.course_totaltime)
			value.append(oneline.course_load)
			value.append(oneline.teacher)
			value.append(oneline.block)
			value.append(oneline.url)
			MysqlHelper.insert_one(cur,sql,value)
		MysqlHelper.finish(conn)
		
		
pmphmooc = pmphmooc()
pmphmooc.start()