# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/8/31 10:27
"""
import urllib.request
import urllib.parse
import urllib3


#发送给微服务端

url="http://39.104.132.224/member/state"

postdata =urllib.parse.urlencode({
"Logon_Password":"sunmin",
"Logon_PostCode":"fghc",
"Logon_RememberMe":"false",
"Logon_UserEmail":"sun121@qq.com"
}).encode('utf-8')
# print(postdata)
req=urllib.request.Request(url=url,data=postdata,method='POST')
res = urllib.request.urlopen(req)
res_data = res.read().decode('utf-8')
print(res_data)