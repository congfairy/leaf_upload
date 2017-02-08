from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.simple_httpclient import SimpleAsyncHTTPClient
import tornado.ioloop
import tornado.web
import os,sys
from stat import *
from tornado import gen
from functools import partial
#import time,datatime


total_downloaded = 0
#action = sys.argv[1]
#filepath = sys.argv[2]
#uid = sys.argv[3]
#gid = sys.argv[4]
#pos = sys.argv[5]
def geturl(action,host,filepath,uid,gid,pos,size):
    if action=="read":
        url = "http://"+host+"/read?filepath="+filepath+"&uid="+uid+"&gid="+gid+"&pos="+pos+"&size="+size
        print(url) 
        return url

def geturl1(action,host,targetpath):
    if action=="upload":
        url = "http://"+host+"/upload?targetpath="+targetpath
        print(url) 
        return url

def chunky(path, chunk):
#   print("self._max_body_size",self._max_body_size)
   global total_downloaded
   total_downloaded += len(chunk)
  # print("chunk size",len(chunk))
   # the OS blocks on file reads + writes -- beware how big the chunks is as it could effect things
   with open(path, 'ab') as f:
       f.write(chunk)

@gen.coroutine
def writer(host,filepath,targetdir,uid,gid,pos,size):
   print("writer function")
#   tornado.ioloop.IOLoop.instance().start()
   file_name = targetdir+os.path.basename(filepath)
   if os.path.exists(targetdir):
       pass
   else:
       os.makedirs(targetdir)
   f = open(file_name,'w')
   f.close()
   request = HTTPRequest(geturl("read",host,filepath,uid,gid,pos,size), streaming_callback=partial(chunky, file_name))
   AsyncHTTPClient.configure('tornado.simple_httpclient.SimpleAsyncHTTPClient', max_body_size=512*1024*1024)
   http_client = AsyncHTTPClient(force_instance=True)
   #http_client.configure("tornado.simple_httpclient.SimpleAsyncHTTPClient",max_body_size=524288000)
   response = yield http_client.fetch(request)
   tornado.ioloop.IOLoop.instance().stop()
   print("total bytes downloaded was", total_downloaded)

def upload_in_chunks(filepath, chunk_size=1024*1024):
  with open(filepath, 'rb') as infile: 
     chunk = infile.read(chunk_size)
     while chunk:
         yield chunk
         chunk = infile.read(chunk_size)
  infile.close()   

@gen.coroutine
def upload(host,filepath,targetpath):
   print("upload function")
   if os.path.exists(filepath):
     statinfo = os.stat(filepath)
     mode = statinfo.st_mode
     if (S_ISDIR(mode)):
        print("This is not a file!")
        exit(1)
     else:
#        AsyncHTTPClient.configure('tornado.simple_httpclient.SimpleAsyncHTTPClient', max_body_size=512*1024*1024)
        http_client = AsyncHTTPClient(force_instance=True)  
        for chunk in upload_in_chunks(filepath):
              print("firstsent",len(chunk))
              request = HTTPRequest(geturl1("upload",host,targetpath), 'POST', body=chunk)
              response = yield http_client.fetch(request)
              #await gen.Task(self.flush)
              total_sent += len(chunk)
              print("sent",total_sent)
        #self.finish()
        tornado.ioloop.IOLoop.instance().stop()
          
   else:
      print("file or directory doesn't exit!")
      tornado.ioloop.IOLoop.instance().stop()
      exit(1)

#def push_resp(self,resp):
#   print("Successfully sent data",repr(resp.body))

def readentrance(host,filepath,targetdir,uid,gid,pos,size):
      writer(host,filepath,targetdir,uid,gid,pos,size)
      tornado.ioloop.IOLoop.instance().start()

def uploadentrance(host,filepath,targetpath):
      upload(host,filepath,targetpath)
      tornado.ioloop.IOLoop.instance().start()
