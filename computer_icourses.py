# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import Tool
import MysqlHelper

#数据库一条记录内容
class Item:
    def __init__(self):
		self.title = ""
		self.short_desc = ""
		self.description = ""
		self.requirement = ""
		self.pre_knowledge = ""
		self.chapter = ""
		self.reference = ""
		self.common_prob = ""
		self.teacher = ""
		self.url = ""

#爬虫类
class computer_icourses:
	def __init__(self):
		self.tool = Tool.Tool()
				
	def getPage(self,url):
		try:
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接MOOC失败，错误原因",e.reason
				return None
	
	def getURL(self,page):
		pattern = re.compile('<div class="col-md-4 col-sm-6">.*?<a class="" href="(.*?)"',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	def getTitle(self,page):
		pattern = re.compile('<h2 class="f-fl">(.*?)<span',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getShortDesc(self,page):
		pattern = re.compile('<p class="f-fc6" id="j-rectxt".*?>spContent=(.*?)</p>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getInfo(self,page):
		pattern = re.compile('<div class="top f-f0".*?>(.*?)</div>.*?<div.*?>(.*?)</div>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	def getTeacher(self,page):
		pattern = re.compile('<a class="u-tchcard f-cb".*?>.*?<div class="cnt f-fl">.*?<h3 class="f-fc3">(.*?)</h3>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None	
				
	def start(self):
		indexPage = self.getPage('http://computer.icourses.cn/')
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		cur.execute('drop table if exists computer_icourses')
		cur.execute('create table computer_icourses(id int(11) primary key auto_increment,title varchar(255),short_desc text,description text,requirement text,pre_knowledge text,chapter text,reference text,common_prob text,teacher text,url varchar(255))')
		sql = 'insert into computer_icourses(title,short_desc,description,requirement,pre_knowledge,chapter,reference,common_prob,teacher,url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		url = self.getURL(indexPage)
		for item in url:
			oneline = Item()
			oneline.url = item
			page = self.getPage(item)
			title = self.getTitle(page)
			oneline.title = title
			shortDesc = self.getShortDesc(page)
			oneline.short_desc = shortDesc
			info = self.getInfo(page)
			for item in info:
				if item[0] == '课程概述':
					oneline.description = re.sub(self.tool.replaceNBSP," ",self.tool.replace(item[1]))
				if item[0] == '证书要求':
					oneline.requirement = re.sub(self.tool.replaceNBSP," ",self.tool.replace(item[1]))
				if item[0] == '预备知识':
					oneline.pre_knowledge = re.sub(self.tool.replaceNBSP," ",self.tool.replace(item[1]))
				if item[0] == '授课大纲':
					oneline.chapter = re.sub(self.tool.replaceNBSP," ",self.tool.replace(item[1]))
				if item[0] == '参考资料':
					oneline.reference = re.sub(self.tool.replaceNBSP," ",self.tool.replace(item[1]))
				if item[0] == '常见问题':
					oneline.common_prob = re.sub(self.tool.replaceNBSP," ",self.tool.replace(item[1]))
			teacher = self.getTeacher(page)
			teacherstr = ""
			for item in teacher:
				teacherstr = teacherstr + item + '\n'
			oneline.teacher = teacherstr

			value = []
			value.append(oneline.title)
			value.append(oneline.short_desc)
			value.append(oneline.description)
			value.append(oneline.requirement)
			value.append(oneline.pre_knowledge)
			value.append(oneline.chapter)
			value.append(oneline.reference)
			value.append(oneline.common_prob)
			value.append(oneline.teacher)
			value.append(oneline.url)
			MysqlHelper.insert_one(cur,sql,value)
		MysqlHelper.finish(conn)
		
		
computer_icourses = computer_icourses()
computer_icourses.start()