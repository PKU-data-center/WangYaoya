# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import json
import Tool
import MysqlHelper

#复旦大学慕课平台
class fudan:
	
	def __init__(self):
		self.tool = Tool.Tool()
		
	def getPage(self,param):
		try:
			url = param
			print url
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接复旦大学慕课平台失败，错误原因",e.reason
				return None
				
	def getContent(self):
		try:
			url = 'http://fudan.xuetangx.com/courses/microsite'
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read().decode('utf-8')
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接复旦大学慕课平台失败，错误原因",e.reason
				return None
	
	def getUrl(self,page):
		pattern = re.compile('<li class="col-gg-2.*?">.*?<a href="(.*?)"',re.S)
		result = re.findall(pattern,page)
		for item in result:
			print item
			
	def getTitle(self,page):
		pattern = re.compile('<h1>(.*?)</h1>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
	
	#课程代码、开课时间、当前学期、投入时间
	def getInfo1(self,page):
		pattern = re.compile('<li class="col-gg-3 col-lg-3 col-md-3 col-sm-3 col-xs-6">.*?<p>(.*?)</p>.*?<p>(.*?)</p>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None

	#课程简介、知识储备、章节信息、常见问题
	def getInfo2(self,page):
		pattern = re.compile('<section>.*?<h2>.*?<span.*?</span>(.*?)</h2>.*?<div class="txt">(.*?)</section>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
	
	def getTeacherInfo(self,page):
		pattern = re.compile('<figcaption>(.*?)</figcaption>.*?<figcaption>(.*?)</figcaption>.*?<div class="teacher_txt">.*?</a>(.*?)</div>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
	
	def start(self):
		content = json.loads(self.getContent())
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		cur.execute('drop table if exists fudan')
		cur.execute('create table if not exists fudan(id int(11) primary key auto_increment,title varchar(255),lesson_code varchar(255),start_time varchar(255),current_sem varchar(255),spend_time varchar(255),short_desc text,knowledge_res text,chapter_info text,common_prob text,teacher_info text,url varchar(255))')
		sql = 'insert into fudan(title,lesson_code,start_time,current_sem,spend_time,short_desc,knowledge_res,chapter_info,common_prob,teacher_info,url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		for item in content["course"]:
			if not item["about"].find("lecture") == -1:
				continue
			value = []
			url = "http://fudan.xuetangx.com" + item["about"]
			page = self.getPage(url)
			title = self.getTitle(page)
			value.append(title)
			info = self.getInfo1(page)
			for item in info:
				value.append(item[0] + ':' + self.tool.replace(item[1]))
				
			info2 = self.getInfo2(page)
			for item in info2:
				value.append(item[0] + ':' + re.sub(r'[\n\t]+',r'\n', self.tool.replace(item[1]), flags=re.S))
			for x in range(4 - len(info2)):
				value.append('')
			teacherinfo = self.getTeacherInfo(page)
			teacher = ""
			for item in teacherinfo:
				str = item[0] + '\n' + item[1] + '\n' + self.tool.replace(item[2]) + '\n'
				teacher = teacher + str
			value.append(teacher)
			value.append(url)
			MysqlHelper.insert_one(cur,sql,value)
		MysqlHelper.finish(conn)
		
fudan = fudan()
fudan.start()