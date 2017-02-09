import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.options
from tornado import gen
import os,sys,re
from stat import *
from tornado.options import define, options
from os.path import getsize

GB = 1024 * 1024 * 1024

#@gen.coroutine
class UploadRequestHandler(tornado.web.RequestHandler):
    async def post(self):
        total_received = 0
        filepath = self.get_argument('targetpath')
        print("filepath",filepath)
        if os.path.exists(filepath):
             pass
        else:
            os.makedirs(filepath)
        f = open_file(filepath,'w')
        chunk = self.get_body_argument('body')
        print("sent",len(chunk))
        write_data(f,chunk) 
        put(f)

@gen.coroutine
def open_file(self, path):
    fd = os.open(path, (os.O_RDWR | os.O_CREAT))
    f = os.fdopen(fd, 'rb+')
      #  if pos is not None:
       #     f.seek(pos)
    return f
    print("open_file")


@gen.coroutine
def write_data(self, file, chunk):
        yield file.write(chunk)
        print("write_data")


def put(self, file):
        self.file.close()
        self.write('OK')
        print ("put")

def read_in_chunks(infile, chunk_size=1024*1024):
   chunk = infile.read(chunk_size)
   while chunk:
       yield chunk
       chunk = infile.read(chunk_size)

def read_in_chunks_pos(base_dir, pos, size, chunk_size=1024*1024):
  realsize = getsize(base_dir)
  if(int(size)>=realsize):
   with open(base_dir, 'rb') as infile:
     infile.seek(int(pos))
     no = (realsize-int(pos)) // chunk_size
     i = 0
     while i<no:
        chunk = infile.read(chunk_size)
        yield chunk
        i = i+1
     if ((realsize-int(pos)) % chunk_size) != 0:
        last = (realsize-int(pos)) % chunk_size
        chunk = infile.read(last)
        yield chunk
   infile.close()
  else:   
   with open(base_dir, 'rb') as infile:
     infile.seek(int(pos))
     no = int(size) // chunk_size
     i = 0
     #chunk = infile.read(chunk_size)
     #while chunk and i<no:
     while i<no:
        chunk = infile.read(chunk_size)
        yield chunk
        i = i+1
     if (int(size) % chunk_size) != 0:
        last = int(size) % chunk_size
        chunk = infile.read(last)
        yield chunk
   infile.close()

class ReadRequestHandler(tornado.web.RequestHandler):
  # @gen.coroutine
   async def get(self):
        total_sent = 0
        uid = self.get_argument('uid')
        gid = self.get_argument('gid')
        base_dir = self.get_argument('filepath')
        pos = self.get_argument('pos')
        size = self.get_argument('size')
        # Python protocol does not require () on it's if statements like you are

        if base_dir==None or uid==None or gid==None or pos==None or size==None:
            self.write("Invalid argument!You caused a %d error."%status_code)
            exit(1)
        if os.path.exists(base_dir):
          statinfo = os.stat(base_dir)
          if(int(uid)==statinfo.st_uid and int(gid)==statinfo.st_gid):
              mode = statinfo.st_mode
          else:
              self.write("Permission denied.")
              exit(1)
        else:
            self.write("File or directory doesn't exist!You caused a %d error."%status_code)
            exit(1)
        if (S_ISDIR(mode)):
            self.write("This is not a file!You caused a %d error."%status_code)
            exit(1)
        else:
          #  with open(base_dir, 'rb') as infile:
                for chunk in read_in_chunks_pos(base_dir,pos,size):
                    self.write(chunk)
                    await gen.Task(self.flush)
                    total_sent += len(chunk)
                   # print("sent",total_sent)
                #print("sent",total_sent)
                self.finish()
class ListRequestHandler(tornado.web.RequestHandler):
   @tornado.web.asynchronous
   @gen.coroutine
   def get(self):
        uid = self.get_argument('uid')
        gid = self.get_argument('gid')
        base_dir = self.get_argument('path')
        if (base_dir==None or uid==None or gid==None):
            self.write("Invalid argument!You caused a %d error."%status_code)
            exit(1)
        if(os.path.exists(base_dir)):
          statinfo = os.stat(base_dir)
          self.write('{'+'"father_node"'+':')
          statdict = {'path':base_dir,'mode':str(statinfo.st_mode),'ino':str(statinfo.st_ino),'dev':str(statinfo.st_dev),'nlink':str(statinfo.st_nlink),'uid':str(statinfo.st_uid),'gid':str(statinfo.st_gid),'size':str(statinfo.st_size),'atime':str(statinfo.st_atime),'mtime':str(statinfo.st_mtime),'ctime':str(statinfo.st_ctime)}
          if(int(uid)==statinfo.st_uid and int(gid)==statinfo.st_gid):
              self.write(statdict)
              mode = statinfo.st_mode
          else:
              self.write("Permission denied.")
              exit(1)
        else:
            self.write("File or directory doesn't exist!You caused a %d error."%status_code)
            exit(1)
        if (S_ISDIR(mode)==None):
                self.write("This is not a directory!You caused a %d error."%status_code)
                exit(1)
        else:
                files = os.listdir(base_dir)
                for f in files:
                    statinfo = os.stat(base_dir + '/' +f)
                    self.write(',"'+f+'":')
                    statdict = {'path':(base_dir + '/' +f),'mode':str(statinfo.st_mode),'ino':str(statinfo.st_ino),'dev':str(statinfo.st_dev),'nlink':str(statinfo.st_nlink),'uid':str(statinfo.st_uid),'gid':str(statinfo.st_gid),'size':str(statinfo.st_size),'atime':str(statinfo.st_atime),'mtime':str(statinfo.st_mtime),'ctime':str(statinfo.st_ctime)}
              #      print ("statdict",statdict)
                    self.write(statdict)
                self.write("}")
   def write_error(self,status_code,**kwargs):
                self.write("Gosh darnit,user!You caused a %d error."%status_code)

class StreamingRequestHandler(tornado.web.RequestHandler):
   @tornado.web.asynchronous
   @gen.coroutine
   def get(self):
       # back as right now this is limited to what is hard coded in
        total_sent = 0
        uid = self.get_argument('uid')
        gid = self.get_argument('gid')
        base_dir = self.get_argument('filepath')
        if (base_dir==None or uid==None or gid==None):
            self.write("Invalid argument!You caused a %d error."%status_code)
            exit(1)
        if(os.path.exists(base_dir)):
          statinfo = os.stat(base_dir)
          if(int(uid)==statinfo.st_uid and int(gid)==statinfo.st_gid):
              mode = statinfo.st_mode
          else:
              self.write("Permission denied.")
              exit(1)
        else:
            self.write("File or directory doesn't exist!You caused a %d error."%status_code)
            exit(1)
        if (S_ISDIR(mode)):
            self.write("This is not a file!You caused a %d error."%status_code)
            exit(1)
        else:
            with open(base_dir, 'rb') as infile:
                for chunk in read_in_chunks(infile):
                    self.write(chunk)
                    yield gen.Task(self.flush)
                    total_sent += len(chunk)
                    print("sent",total_sent)

            self.finish()

if __name__ == "__main__":
   # this was connected to the pyCurl call and as far as I know now not
   # beng used so try without to insure it's no longer needed
   tornado.options.parse_command_line()
   #print (tornado.version)
   application = tornado.web.Application([
    (r"/download", StreamingRequestHandler),
    (r"/list",ListRequestHandler),
    (r"/read",ReadRequestHandler),
    (r"/upload", UploadRequestHandler),
    ])
   http_server = tornado.httpserver.HTTPServer(application,xheaders=True)
   application.listen(8880)
   tornado.ioloop.IOLoop.instance().start()

