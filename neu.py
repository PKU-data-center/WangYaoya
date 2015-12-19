# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import json
import Tool
import MysqlHelper

#数据库一条记录内容
class Course:
    def __init__(self):
		self.title = ""
		self.lesson_code = ""
		self.start_time = ""
		self.current_sem = ""
		self.spend_time = ""
		self.short_desc = ""
		self.knowledge_res = ""
		self.chapter_info = ""
		self.common_prob = ""
		self.teacher_info = ""
		self.url = ""
		
#数据库一条记录内容
class Lecture:
    def __init__(self):
		self.title = ""
		self.intro = ""
		self.guest = ""
		self.video_info = ""
		self.addr = ""
		self.url = ""

#东北大学慕课平台
class neu:
	
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
				print u"连接慕课平台失败，错误原因",e.reason
				return None
				
	def getContent(self):
		try:
			url = 'http://neu.xuetangx.com/courses/microsite'
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read().decode('utf-8')
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接慕课平台失败，错误原因",e.reason
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
			
	def getLectureTitle(self,page):
		pattern = re.compile("<div class='title'>(.*?)</div>",re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getLectureIntro(self,page):
		pattern = re.compile("详情介绍：</h2>(.*?)<h2>",re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getLectureGuest(self,page):
		pattern = re.compile("嘉宾介绍：</h2>(.*?)<h2>",re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getVideoInfo(self,page):
		pattern = re.compile("精彩视频段点：</h2>(.*?)</section>",re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getLectureInfo(self,page):
		pattern = re.compile("<address>(.*?)</address>",re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
	
	def start(self):
		content = json.loads(self.getContent())
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		cur.execute('drop table if exists neu')
		cur.execute('create table if not exists neu(id int(11) primary key auto_increment,title varchar(255),lesson_code varchar(255),start_time varchar(255),current_sem varchar(255),spend_time varchar(255),short_desc text,knowledge_res text,chapter_info text,common_prob text,teacher_info text,url varchar(255))')
		sql = 'insert into neu(title,lesson_code,start_time,current_sem,spend_time,short_desc,knowledge_res,chapter_info,common_prob,teacher_info,url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		for item in content["course"]:
			oneline = Course()
			url = "http://neu.xuetangx.com" + item["about"]
			page = self.getPage(url)
			title = self.getTitle(page)
			oneline.title = title
			info = self.getInfo1(page)
			for item in info:
				if item[0] == "课程代码":
					oneline.lesson_code = self.tool.replace(item[1])
				if item[0] == "开课时间":
					oneline.start_time = self.tool.replace(item[1])
				if item[0] == "当前学期":
					oneline.current_sem = self.tool.replace(item[1])
				if item[0] == "投入时间":
					oneline.spend_time = self.tool.replace(item[1])
			info2 = self.getInfo2(page)
			for item in info2:
				if item[0] == "课程简介":
					oneline.short_desc = re.sub(r'[\n\t]+',r'\n', self.tool.replace(item[1]), flags=re.S)
				if item[0] == "知识储备":
					oneline.knowledge_res = re.sub(r'[\n\t]+',r'\n', self.tool.replace(item[1]), flags=re.S)
				if item[0] == "章节信息":
					oneline.chapter_info = re.sub(r'[\n\t]+',r'\n', self.tool.replace(item[1]), flags=re.S)
				if item[0] == "常见问题":
					oneline.common_prob = re.sub(r'[\n\t]+',r'\n', self.tool.replace(item[1]), flags=re.S)
			teacherinfo = self.getTeacherInfo(page)
			teacher = ""
			if teacherinfo:
				for item in teacherinfo:
					str = item[0] + '\n' + item[1] + '\n' + self.tool.replace(item[2]) + '\n'
					teacher = teacher + str
			oneline.teacher_info = teacher
			oneline.url = url
			value = []
			value.append(oneline.title)
			value.append(oneline.lesson_code)
			value.append(oneline.start_time)
			value.append(oneline.current_sem)
			value.append(oneline.spend_time)
			value.append(oneline.short_desc)
			value.append(oneline.knowledge_res)
			value.append(oneline.chapter_info)
			value.append(oneline.common_prob)
			value.append(oneline.teacher_info)
			value.append(oneline.url)
			MysqlHelper.insert_one(cur,sql,value)
		if content["lecture"]:
			cur.execute('drop table if exists neu_lecture')
			cur.execute('create table if not exists neu_lecture(id int(11) primary key auto_increment,title varchar(255),intro text,guest text,video_info text,addr text,url varchar(255))')
			sql = 'insert into neu_lecture(title,intro,guest,video_info,addr,url) values(%s,%s,%s,%s,%s,%s)'
			for item in content["lecture"]:
				oneline = Lecture()
				url = "http://neu.xuetangx.com" + item["about"]
				page = self.getPage(url)
				title = self.getLectureTitle(page)
				oneline.title = title
				intro = self.getLectureIntro(page)
				oneline.intro = self.tool.replace(intro)
				guest = self.getLectureGuest(page)
				oneline.guest = self.tool.replace(guest)
				videoInfo = self.getVideoInfo(page)
				oneline.video_info = self.tool.replace(videoInfo)
				addr = self.getLectureInfo(page)
				oneline.addr = self.tool.replace(addr)
				oneline.url = url
				value = []
				value.append(oneline.title)
				value.append(oneline.intro)
				value.append(oneline.guest)
				value.append(oneline.video_info)
				value.append(oneline.addr)
				value.append(oneline.url)
				MysqlHelper.insert_one(cur,sql,value)		
		MysqlHelper.finish(conn)
		
neu = neu()
neu.start()