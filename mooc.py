# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import Tool
import MysqlHelper

#数据库一条记录内容
class Item:
    def __init__(self):
		self.title_chinese = ""
		self.title_english = ""
		self.brief = ""
		self.teacher = ""
		self.chapter = ""
		self.require = ""
		self.form = ""
		self.question = ""
		self.resource = ""
		self.url = ""

#MOOC中国爬虫类
class mooc:
	def __init__(self):
		self.tool = Tool.Tool()
		
	def getContent(self,pageIndex):
		try:
			url = 'http://www.mooc.cn/course/page/' + str(pageIndex)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接MOOC中国失败，错误原因",e.reason
				return None
				
	def getPage(self,url):
		try:
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			#print response.read()
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接MOOC中国失败，错误原因",e.reason
				return None
				
	def getPageNum(self,page):
		pattern = re.compile("<a class='page-numbers' href='http://www.mooc.cn/course/page/(.*?)'.*?</a>",re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
	
	def getURL(self,page):
		pattern = re.compile('<div class="course-list">.*?<div class="course-listimg">.*?<a target="_blank" href="(.*?)"',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	def getTitle_chinese(self,page):
		pattern = re.compile('<h1 class="course-title">(.*?)</h1>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getTitle_english(self,page):
		pattern = re.compile('<div class="course_ennamei">(.*?)</div>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	#获取内容所在的区块
	def getBlock(self,page):
		pattern = re.compile('<div class="content-entry clearfix">(.*?)</div>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	#content为需要获取的内容
	def getInfo(self,page,content):
		pattern = re.compile(content + '</h3>(.*?)<h3>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			pattern = re.compile(content + '</h3>(.*?)</div>',re.S)
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
			
	def wordInText(self,page,words):
		for item in words:
			if not page.find('<h3>' + item + '</h3>') == -1:
				return True
		return False
		
				
	def start(self):
		indexPage = self.getContent(1)
		# print indexPage
		pageNum = self.getPageNum(indexPage)
		# print pageNum[-2]
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		# cur.execute('drop table if exists mooc')
		# cur.execute('create table mooc(id int(11) primary key auto_increment,title_chinese varchar(255),title_english varchar(255),brief text,teacher text,chapter text,requires text,form text,question text,resource text,url varchar(255))')
		sql = 'insert into mooc(title_chinese,title_english,brief,teacher,chapter,requires,form,question,resource,url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		for i in range(78,int(pageNum[-2])+1):
		# for i in range(1,2):
			indexPage = self.getContent(i)
			URL = self.getURL(indexPage)
			for item in URL:
				oneline = Item()
				page = self.getPage(item)
				# print page
				title_chinese = self.getTitle_chinese(page)
				oneline.title_chinese = title_chinese
				title_english = self.getTitle_english(page)
				oneline.title_english = title_english
				# print title_chinese,title_english
				block = self.getBlock(page)
				#添加的</div>用户判断文本结尾
				block = block + '</div>'
				# print block + '\n'
				briefWords = ["课程概述","课程概况","课程简介"]
				if self.wordInText(block,briefWords):
					brief = self.getText(block,briefWords)
					oneline.brief = self.tool.replace(brief)
					# print brief
				teacherWords = ["授课教师","主讲教师"]
				if self.wordInText(block,teacherWords):
					teacher = self.getText(block,teacherWords)
					oneline.teacher = self.tool.replace(teacher)
					# print teacher
				chapterWords = ["授课大纲","课程大纲"]
				if self.wordInText(block,chapterWords):
					chapter = self.getText(block,chapterWords)
					oneline.chapter = self.tool.replace(chapter)
					# print chapter
				requireWords = ["先修要求","先修知识","背景知识"]
				if self.wordInText(block,requireWords):
					require = self.getText(block,requireWords)
					oneline.require = self.tool.replace(require)
					# print require
				formWords = ["授课形式"]
				if self.wordInText(block,formWords):
					form = self.getText(block,formWords)
					oneline.form = self.tool.replace(form)
					# print form
				questionWords = ["常见问题解答","常见问题"]
				if self.wordInText(block,questionWords):
					question = self.getText(block,questionWords)
					oneline.question = self.tool.replace(question)
					# print question
				resourceWords = ["参考资料"]
				if self.wordInText(block,resourceWords):
					resource = self.getText(block,resourceWords)
					oneline.resource = self.tool.replace(resource)
					# print self.tool.replace(resource)
				#url
				oneline.url = item
				value = []
				value.append(oneline.title_chinese)
				value.append(oneline.title_english)
				value.append(oneline.brief)
				value.append(oneline.teacher)
				value.append(oneline.chapter)
				value.append(oneline.require)
				value.append(oneline.form)
				value.append(oneline.question)
				value.append(oneline.resource)
				value.append(oneline.url)
				MysqlHelper.insert_one(cur,sql,value)
		MysqlHelper.finish(conn)
		
		
mooc = mooc()
mooc.start()