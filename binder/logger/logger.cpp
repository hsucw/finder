#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string>
#include <cstdlib>
#include <sstream>

using namespace std;

#define BUF_SZ 32768

int main(){
	char buffer[BUF_SZ]={0};
	int n;
	int fd=open("/sys/kernel/debug/binder/transaction_log",O_RDONLY);
	int wfd=open("/data/data/log.finder",O_WRONLY|O_CREAT);
	int debug_id,debug_id_record=0;
	if(wfd>0){
		printf("open success\n");
	}else{
		printf("open failed\n");
		exit(1);
	}
	while(1){
		string logs;
		//sleep for 0.01 seconds on nexus 7
		usleep(10000);
		if(fd>0){
			lseek (fd, 0, SEEK_SET);
			while( (n = read(fd,buffer,BUF_SZ-1)) > 0){
				logs.append(buffer);
			}
		}else{
			printf("Error opening file\n");
		}
		stringstream ss(logs);
		string item;

		int log_count=0;
		int round_max=debug_id_record-1;
		while( getline(ss, item, '\n') && log_count < 48) {
			int start,end;
			log_count++;
			start=item.find("debug_id: ");
			end=item.find(", from_proc");
			if(start == -1 or end == -1){
				continue;
			}
			debug_id=atoi(item.substr(start+10,end-start-10).c_str());
			if(debug_id < debug_id_record){
				continue;
			}else{
				//printf("%s\n",item.c_str());
				write(wfd,item.c_str(),item.length());
				write(wfd,"\n",1);
				if(debug_id>round_max){
					round_max=debug_id;
				}
			}
		}
		debug_id_record=round_max+1;
	}

	printf("\n");
	return 0;
}
