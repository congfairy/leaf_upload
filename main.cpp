#include "uploadclient.h"
int main()
{
   transupload("192.168.83.218:8880","/dev/shm/500M.file","/root/leaf/pytoc/upload/500M.file");
   //transread("192.168.83.218:8800","/dev/shm/500M.file","/root/leaf/pytoc/download/","0","0","0","20000");
   return 0;

}
