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
		self.teacher = ""
		self.school = ""
		self.type = ""

#中国教师慕课网
class mooccollege:
	def __init__(self):
		self.tool = Tool.Tool()
		
	def getPage(self,viewId):
		try:
			url = 'http://www.mooccollege.cn/lesson/' + str(viewId) + '.html'
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.URLError, e:
			if hasattr(e,"reason"):
				print u"连接中国教师慕课网失败，错误原因",e.reason
				return None
	
	#获取题目、教师、学校信息
	def getInfo(self,page):
		pattern = re.compile('<p class="KmkshowNam">(.*?)</p>.*?<span class="KmkteaNam">(.*?)</span>(.*?)</p>',re.S)
		result = re.findall(pattern,page)
		if result:
			return result
		else:
			return None
		
	def start(self):
		conn = MysqlHelper.connect()
		cur = conn.cursor()
		cur.execute('drop table if exists mooccollege')
		cur.execute('create table mooccollege(id int(11) primary key auto_increment,title varchar(255),teacher varchar(255),school varchar(255),type varchar(255))')
		sql = 'insert into mooccollege(title,teacher,school,type) values(%s,%s,%s,%s)'
		for i in range(1,5):
			oneline = Item()
			page = self.getPage(i)
			info = self.getInfo(page)
			for item in info:
				# print item[0],item[1],item[2]
				oneline.title = item[0]
				oneline.teacher = item[1]
				oneline.school = item[2]
				if i == 1:
					oneline.type = "冲刺专题"
				elif i == 2:
					oneline.type = "考题解析"
				elif i == 3:
					oneline.type = "同步教材"
				else:
					oneline.type = "知识模块"
				value = []
				value.append(oneline.title)
				value.append(oneline.teacher)
				value.append(oneline.school)
				value.append(oneline.type)
				MysqlHelper.insert_one(cur,sql,value)
		MysqlHelper.finish(conn)
		
mooccollege = mooccollege()
mooccollege.start()