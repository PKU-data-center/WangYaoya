# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import Tool
import MysqlHelper

#慕课爬虫类
class IMooc:

	def __init__(self,baseUrl):
		self.baseUrl = baseUrl
		self.tool = Tool.Tool()
		
	def getViewPage(self,viewId):
		try:
			url = self.baseUrl + 'view/' + str(viewId)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			#print response.read()
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接慕课失败，错误原因",e.reason
				return None
				
	def getLearnPage(self,viewId):
		try:
			url = self.baseUrl + 'learn/' + str(viewId)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			#print response.read()
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接慕课失败，错误原因",e.reason
				return None
	
	def getContent(self,pageIndex):
		try:
			url = 'http://www.imooc.com/course/list?page=' + str(pageIndex)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read().decode('utf-8')
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接慕课失败，错误原因",e.reason
				return None
				
	def getTitle(self,page):
		#url = self.baseUrl + str(9)
		#request = urllib2.Request(url)
		#response = urllib2.urlopen(request)
		pattern = re.compile('<title>(.*?)</title>',re.S)
		result = re.search(pattern,page)
		#print result.group(1).strip())
		if result:
			return result.group(1).strip()
		else:
			return None
			
	def getBrief(self,page):
		pattern = re.compile('<h3 class="ctit">.*?>.*?>(.*?)</p>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
			
	# def getOutline(self,page):
		# pattern = re.compile('<div class="chapter-bd l">.*?>(.*?)</h5>.*?>(.*?)</p>',re.S)
		# result = re.findall(pattern,page)
		# if result:
			# return result
		# else:
			# return None
			
	def getOutline(self,page):
		pattern = re.compile('<div class="chapter.*?<strong>(.*?)</strong>.*?<ul class="video">(.*?)</ul>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
			
	def getLevelTimeAndCount(self,page):
		pattern = re.compile('<span class="meta-value">(.*?)</span>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result[0:3]
		else:
			return None
				
	def getPageNum(self,page):
		pattern = re.compile(u'下一页' +'</a><a href="/course/list\?page=(.*?)">',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None
	
	def getViewsId(self,page):
		pattern = re.compile('<li class="course-one".*?<a href="/view/(.*?)"',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
	
	def start(self):
		indexPage = self.getContent(1)
		pageNum = self.getPageNum(indexPage)
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		cur.execute('drop table if exists imooc')
		cur.execute('create table imooc(id int(11) primary key auto_increment,title varchar(255),difficulty varchar(255),time varchar(255),learn_count varchar(255),short_desc text,outline text)')
		sql = 'insert into imooc(title,difficulty,time,learn_count,short_desc,outline) values(%s,%s,%s,%s,%s,%s)'
		for i in range(1,int(pageNum)+1):
			indexPage = self.getContent(i)
			ViewsId = self.getViewsId(indexPage)
			for item in ViewsId:
				value = []
				learnpage = self.getLearnPage(item)
				viewpage = self.getViewPage(item)
				title = self.getTitle(learnpage)
				value.append(title)
				info = self.getLevelTimeAndCount(learnpage)
				infos = []
				for item in info:
					item = self.tool.replace(item)
					infos.append(item)
				value.append(infos[0])
				value.append(infos[1])
				value.append(infos[2])
				brief = self.getBrief(viewpage)
				value.append(brief)
				outline = self.getOutline(learnpage)
				str = ""
				for item in outline:
					str = str + self.tool.replace(item[0]) + '\n'
					pattern = re.compile('<li>(.*?)</li>',re.S)
					result = re.findall(pattern,item[1])
					if result:
						for item in result:
							item = re.sub(self.tool.removeAddr,"",item)
							item = re.sub(self.tool.replaceLT,"<",item)
							item = re.sub(self.tool.replaceGT,">",item)
							str = str + item.strip() + '\n'
				value.append(str)
				MysqlHelper.insert_one(cur,sql,value)
		MysqlHelper.finish(conn)
							
						
					# for item in outline:
						# file.write(item[0] + '\n')
						# file.write(item[1] + '\n')
		
		# page = self.getPage(9)
		# info = self.getLevelTimeAndCount(page)
		# for item in info:
			# item = self.tool.replace(item)
			# print item
		#print page
		# outline = self.getOutline(page)
		# for item in outline:
			# print self.tool.replace(item[0]),'\n'
			# pattern = re.compile('<li>(.*?)</li>',re.S)
			# result = re.findall(pattern,item[1])
			# if result:
				# for item in result:
					# item = re.sub(self.tool.removeAddr,"",item)
					# item = re.sub(self.tool.replaceLT,"<",item)
					# item = re.sub(self.tool.replaceGT,">",item)
					# print item.strip(),'\n'
		
baseUrl = "http://www.imooc.com/"
imooc = IMooc(baseUrl)
imooc.start()