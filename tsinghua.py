# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import json
import Tool

#清华大学慕课平台
class tsinghua:
	
	def __init__(self,baseUrl):
		self.baseUrl = baseUrl
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
				print u"连接清华大学慕课平台失败，错误原因",e.reason
				return None
				
	def getContent(self):
		try:
			url = 'http://tsinghua.xuetangx.com/courses/microsite'
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read().decode('utf-8')
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接清华大学慕课平台失败，错误原因",e.reason
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
	
	def getTeacher(self,page):
		pattern = re.compile('<figcaption>(.*?)</figcaption>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	def getTeacherDes(self,page):
		pattern = re.compile('<div class="teacher_txt">.*?</a>(.*?)</div>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
	
	def start(self):
		content = json.loads(self.getContent())
		file = open("tsinghua.txt","w+")
		try:
			for item in content["course"]:
				#url = self.getUrl(content)
				#page = self.getPage(urllib.quote_plus("http://tsinghua.xuetangx.com/courses/TSINGHUA/MOOC001/2014_T2/about"))
				page = self.getPage("http://tsinghua.xuetangx.com" + item["about"])
				title = self.getTitle(page)
				file.write('\n' + title + '\n')
				info = self.getInfo1(page)
				for item in info:
					file.write(item[0] + ':' + self.tool.replace(item[1]) + '\n')
				
				info2 = self.getInfo2(page)
				for item in info2:
					#print item[0] + ':' + self.tool.replace(item[1])
					file.write(item[0] + ':' + re.sub(r'[\n\t]+',r'\n', self.tool.replace(item[1]), flags=re.S) + '\n')
				teacher = self.getTeacher(page)
				# print teacher
				file.write('授课老师' + '\n')
				for item in teacher:
					file.write(item + '\n')
				teacherdes = self.getTeacherDes(page)
				file.write(self.tool.replace(teacherdes) + '\n')
				#print lessoncode
		except IOError,e:
			print "写入异常，原因" + e.message
		finally:
			print "写入任务完成"
		
baseUrl = "http://tsinghua.xuetangx.com/?iframe="
tsinghua = tsinghua(baseUrl)
tsinghua.start()