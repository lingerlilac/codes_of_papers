#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/types.h>
#include <linux/types.h>
#include <mysql/mysql.h>
#include <pthread.h>
#include <unistd.h> 
#include <time.h>
#include "thread1.h"
#include "hash_lin.h"
#include "newstructures.h"

#define SEND_SIZE 1024
#define SIZE 1024
/**
 * fp is the file pointer to write information in.
 */
FILE *fp = NULL;

/**
 * tail is the tail point of buffer_pool, i.e., where the new data wroten.
 * head is the head of buffer_pool, where next data to read.
 */
int tail = 0;
int head = 0;
int count1 = 0;
int count2 = 0;

void *receive(void *arg);
void process(char *str);
void decode_winsize(char *buf);
void decode_drops(char *buf);
void decode_iw(char *buf);
void decode_queue(char *buf);
void decode_beacon(char *buf);
void decode_survey(char *buf);
void decode_kiw(char *buf);
void decode_kib(char *buf);
void destroy_iwlist(struct data_iw_mac *);
void destroy_bcnlist(struct data_beacon *);
void iw_new_2_old(struct data_iw *, struct data_iw_new *);
void beacon_new_2_old(struct data_beacon *, struct data_beacon_new *);
struct data_iw *find_keep_iw(char *, char *mac);
struct data_beacon *find_keep_beacon(char *bssid, char *mac);
void iw_old_2_new(struct data_iw_new *old, struct data_iw *new);
void beacon_old_2_new(struct data_beacon_new *old, struct data_beacon *new);
static struct data_iw_mac *find_iw(struct data_iw_new *t, enum found_results *ret, char *mac);
static struct data_beacon_mac *find_beacon(struct data_beacon_new *t, enum found_results *ret, char *mac);
void print_iw_list(void);
void print_beacon(void);
void iw_mac_to_iw(struct data_iw_mac *p, struct data_iw *q);
void iw_to_iw_mac(struct data_iw *p, struct data_iw_mac *q, char *mac);
void dp_to_dpnew(struct dp_packet *s, struct dp_packet_new *t);
void dpnew_to_dp(struct dp_packet_new *s, struct dp_packet *t);
void beacon_to_beacon_mac(struct data_beacon *p, struct data_beacon_mac *q, char *mac);
void beacon_mac_to_beacon(struct data_beacon_mac *p, struct data_beacon *q);
static enum found_results find_flow_drop(struct dp_packet *t, struct flow_and_dropped_c *cur, char *mac);
void survey_mac_to_survey(struct data_survey_c *p, struct data_survey *q);
void survey_to_survey_mac(struct data_survey *p, struct data_survey_c *q, char *mac);
static struct data_survey_c *find_survey(struct data_survey *t, enum found_results *res, char *mac);
void print_mac(char *addr);
void print_string(char *str, int length);
void f_print_string(char *str, int length);
int strcmp_linger(char *s, char *t);
void *g_mes_tn_process(void *arg);
void f_write_string(char *str, int length);
/*
Here is the schedule APIs.
 */
int get_attatched_aps(char **mac_list);
int get_all_aps(char **mac_list);
int get_neighbour_py(char *ap, struct aplist_py *neibours);
int get_neighbour(char *ap, struct aplist *neibours);
int get_clients(char *ap, struct aplist *clients);
int get_clients_py(char *ap, struct aplist_py *clients);
int get_flows(char *ap, struct flowlist *flowlists);
// void *get_flow_drops(char *ap, struct flow_drop_ap_array *flow_drops);
void get_wireless_info(char *ap, struct data_survey *clients);
// bool get_wireless_info(char *ap, struct wireless_information_ap *clients);
/*
End of the APIs.
 */
/**
 * flow_and_dropped_c *fd: Used to maintain a flows and their corresponding packets dropping information list.
 * "last_fd" points to the last member of list.
 */
struct flow_and_dropped_c *fd = NULL, *last_fd = NULL;

/**
 * sur_list: maintain a "iw dev wlan0 survey dmump" fresh information list.
 * indexed by input ap mac address.
 * last_sur is the last member, (i.e., appendix pointer).
 */
struct data_survey_c *sur_list = NULL, *last_sur = NULL;
/**
 * iwlist is used to maintain a fresh link wireless information that APIs are built on.
 */
struct data_iw_mac *iwlist = NULL, *last_iw = NULL;
/**
 * maintain a fresh information of neibour APs, and APIs can be built on it.
 */
struct data_beacon_mac *bcnlist = NULL, *last_beacon = NULL;
/**
 * mutex_data is used to lock the information list, to seperate the update processes and reading processes.
 */
// pthread_mutex_t mutex_data;

/**
 * a switch function to process different messages. The receive function receive 1024 bits message and 
 * send to process function, this function first scan the message type by memcpy a u16 value, based on 
 * this value, the message types can be derived, then corresponding function are called to process this
 * message.
 * @author linger 2018-04-13
 * @param  str [description]
 */
void process(char *str)
{
	char buffer[SEND_SIZE];
	__u16 value;
    enum data_category value_enum;
	int offset = 0;
    struct timeval start, end;
    time_t interval = 0;
    
    gettimeofday(&start, NULL);

	memset(buffer, 0, SEND_SIZE);
	memcpy(buffer, str, SEND_SIZE);
	offset = 0;
	while(offset < SEND_SIZE)
	{
		int out = 0;
		memcpy(&value, buffer+offset, sizeof(__u16));
		offset = offset + 2;
		reversebytes_uint16t(&value);
		// if((value == 5) || (value == 8))
		// 	printf("value is %u %02x\n", value, value);
        value_enum = (enum data_category)value;
		switch(value_enum)
		{
			case WINSIZE:
				decode_winsize(buffer + offset);
				offset += sizeof(struct data_winsize) + 6;
				break;
			case DROPS:
				decode_drops(buffer + offset);
				offset += sizeof(struct dp_packet_new) + 6;
				break;
			case IW:
				decode_iw(buffer + offset);
				offset += sizeof(struct data_iw_new) + 6;
				break;
			case QUEUE:
				decode_queue(buffer + offset);
				offset += sizeof(struct data_queue) + 6;
				break;
			case BEACON:
				decode_beacon(buffer + offset);
				offset += sizeof(struct data_beacon_new) + 6;
				break;
			case SURVEY:
				decode_survey(buffer + offset);
				offset += sizeof(struct data_survey) + 6;
				break;
			case KEEP_IW:
				// decode_kiw(buffer + offset);
				offset += sizeof(struct keep_iw) -2;
				break;
			case KEEP_BEACON:
				// decode_kib(buffer + offset);
				offset += sizeof(struct keep_beacon) -2;
				break;
			default:
				out = 1;
				break;
		}
		if(out == 1)
			break;
	}
    gettimeofday(&end, NULL);
    interval = end.tv_usec - start.tv_usec;
    printf("Time consuming %u %d \n", interval, value_enum);
}
/**
 * [decode_winsize description]
 * After the packet informations are decoded from buffer, A TCP state-machine are mantained by a hash
 * structure, a tcp flow with no updates of two minutes are deleted.
 * @author linger 2018-04-13
 * @param  buf [buffer that cantains winsize data]
 */
void decode_winsize(char *buf)
{
	struct data_winsize rdata;

	int length = sizeof(struct data_winsize);
	int res, kind, wscale, cal_windowsize;
	__u64 time;

	__u32 wanip;
    // char insert_data[600];
    char mac[6];
    int condition = 0;

	char mac_addr[18], mac_addr_origin[6], eth_src[18], eth_dst[18];
	unsigned char *ptr_uc = NULL;
	char ip_src[20];
	char ip_dst[20];

	char *str = NULL;  	

  	str = malloc(sizeof((unsigned char *)&wanip) + sizeof((unsigned char *)&rdata.ip_src) + sizeof((unsigned char *)&rdata.ip_dst) + sizeof((unsigned char *)&rdata.sourceaddr) + sizeof((unsigned char *)&rdata.destination));
	

    memset(ip_src, 0, 20);
    memset(ip_dst, 0, 20);
    memset(mac, 0, 6);
	memset(&rdata, 0, length);
    memcpy(mac, buf, 6);
	memcpy(&rdata, buf + 6, length);
	
	condition =(int)mac[0] + (int)mac[1] + (int)mac[2] + (int)mac[3] + (int)mac[4] + (int)mac[5];
	if(condition == 0)
	{
		printf("condition is zero\n");
		print_mac(mac);
	}

	// ptr_uc = (unsigned char *)malloc(sizeof(unsigned char));

	reversebytes_uint32t(&rdata.datalength);
	reversebytes_uint32t(&rdata.ip_src);
	reversebytes_uint32t(&rdata.ip_dst);
	reversebytes_uint16t(&rdata.sourceaddr);
	reversebytes_uint16t(&rdata.destination);
	reversebytes_uint32t(&rdata.sequence);
	reversebytes_uint32t(&rdata.ack_sequence);
	reversebytes_uint16t(&rdata.flags);
	reversebytes_uint16t(&rdata.windowsize);
	reversebytes_uint64t(&rdata.systime);

    memset(mac_addr, 0, sizeof(mac_addr));
    memset(mac_addr_origin, 0, 6);
    mac_tranADDR_toString_r(mac, mac_addr, 18);
    memcpy(mac_addr_origin, mac, 6);

	mac_tranADDR_toString_r(rdata.eth_src, eth_src, 18);  
	mac_tranADDR_toString_r(rdata.eth_dst, eth_dst, 18);
	ptr_uc = (unsigned char *)&rdata.ip_src;
	sprintf(ip_src,"%u.%u.%u.%u", ptr_uc[3], ptr_uc[2], ptr_uc[1], ptr_uc[0]);
	ptr_uc = (unsigned char *)&rdata.ip_dst;
	sprintf(ip_dst,"%u.%u.%u.%u", ptr_uc[3], ptr_uc[2], ptr_uc[1], ptr_uc[0]);
	kind = (int)(rdata.wscale[0]);
	length = (int) rdata.wscale[1];
	wscale = (int) rdata.wscale[2];
	rdata.flags = rdata.flags & 0x0017;
	cal_windowsize = rdata.windowsize;
	
	     
	if (rdata.flags == 2 || rdata.flags == 18)
	{
	  sprintf(str, "%s%u%u%u%u", mac_addr_origin, rdata.ip_src, rdata.ip_dst, rdata.sourceaddr, rdata.destination);
	  // memcpy(str, mac_addr_origin, 6);
	  // memcpy(str + 6, &rdata.ip_src, 4);
	  // memcpy(str + 10, &rdata.ip_dst, 4);
	  // memcpy(str + 14, &rdata.sourceaddr, 2);
	  // memcpy(str + 16, &rdata.destination, 2);
	  time = getcurrenttime();
	  hash_table_insert(str, wscale, time);
	}
	else if (rdata.flags == 17 || rdata.flags & 0x0004 == 1)
	{
	  sprintf(str, "%s%u%u%u%u", mac_addr_origin, rdata.ip_src, rdata.ip_dst, rdata.sourceaddr, rdata.destination);
	  // memcpy(str, mac_addr_origin, 6);
	  // memcpy(str + 6, &rdata.ip_src, 4);
	  // memcpy(str + 10, &rdata.ip_dst, 4);
	  // memcpy(str + 14, &rdata.sourceaddr, 2);
	  // memcpy(str + 16, &rdata.destination, 2);
	  if (hash_table_lookup(str) != NULL)
	  {
	      hash_table_remove(str);
	  }
	  sprintf(str, "%s%u%u%u%u", mac_addr_origin, rdata.ip_dst, rdata.ip_src, rdata.destination, rdata.sourceaddr);
	  // memcpy(str, mac_addr_origin, 6);
	  // memcpy(str + 6, &rdata.ip_dst, 4);
	  // memcpy(str + 10, &rdata.ip_src, 4);
	  // memcpy(str + 14, &rdata.destination, 2);
	  // memcpy(str + 16, &rdata.sourceaddr, 2);
	  if (hash_table_lookup(str) != NULL)
	  {
	      hash_table_remove(str);
	  }
	}

	else if (rdata.flags == 16)
	{
	  time = getcurrenttime();
	  sprintf(str, "%s%u%u%u%u", mac_addr_origin, rdata.ip_src, rdata.ip_dst, rdata.sourceaddr, rdata.destination);
	  // memcpy(str, mac_addr_origin, 6);
	  // memcpy(str + 6, &rdata.ip_dst, 4);
	  // memcpy(str + 10, &rdata.ip_src, 4);
	  // memcpy(str + 14, &rdata.destination, 2);
	  // memcpy(str + 16, &rdata.sourceaddr, 2);
	  if (hash_table_lookup(str) != NULL)
	  {
	      cal_windowsize = rdata.windowsize << hash_table_lookup(str)->nValue;
	      hash_table_lookup(str)->time = time;
	  } 
	  else
	  {
	      time = getcurrenttime();
	      hash_table_insert(str, wscale, time);
	  }               
	}
    fprintf(fp, "%.18s, %.18s, %.18s, %s, %s, %u, %u, %u, %u, %u, %u, %llu, %u, %u, %u, %u, %u winsize\n", mac_addr, eth_src, eth_dst, ip_src, ip_dst, rdata.sourceaddr, rdata.destination, rdata.sequence, rdata.ack_sequence, rdata.windowsize, cal_windowsize, rdata.systime,rdata.datalength, rdata.flags, kind, length, wscale);
    // printf("Winsize: %.18s, %.18s, %.18s, %s, %s, %u, %u, %u, %u, %u, %u, %llu, %u, %u, %u, %u, %u\n", mac_addr, eth_src, eth_dst, ip_src, ip_dst, rdata.sourceaddr, rdata.destination, rdata.sequence, rdata.ack_sequence, rdata.windowsize, cal_windowsize, rdata.systime,rdata.datalength, rdata.flags, kind, length, wscale);


	free(str);
	str = NULL;

}

/**
 * [decode_drops description]
 * Processing the dropped packets informations, also informatins based on tcp flow are recorded for
 * further computing, a typical application is "get_flow_drops".
 * @author linger 2018-04-13
 * @param  buf [description]
 */
void decode_drops(char *buf)
{

	struct dp_packet_new rdata;
	struct dp_packet rd;
	int offset = 0;
	int length = sizeof(struct dp_packet_new);

	unsigned char *ptr_uc = NULL;
	char ip_src[20];
	char ip_dst[20];
    char srcip[20];
	char mac_addr[18];
    char mac[6];

    memset(ip_src, 0, 20);
    memset(ip_dst, 0, 20);
    memset(srcip, 0, 20);
    memset(mac, 0, 6);
    memset(mac_addr, 0, 18);
	memset(&rdata, 0, length);
	memset(&rd, 0, sizeof(struct dp_packet));
    memcpy(mac, buf, 6);
	memcpy(&rdata, buf + 6, length);

	// ptr_uc = malloc(sizeof(__be32));
	reversebytes_uint32t(&rdata.in_time);
	reversebytes_uint32t(&rdata.sequence);
	reversebytes_uint32t(&rdata.ack_sequence);
	reversebytes_uint32t(&rdata.ip_src);
	reversebytes_uint32t(&rdata.ip_dst);
	reversebytes_uint16t(&rdata.port_src);
	reversebytes_uint16t(&rdata.port_dst);
	reversebytes_uint16t(&rdata.dpl);
	dpnew_to_dp(&rdata, &rd);
    mac_tranADDR_toString_r(mac, mac_addr, 18);
	ptr_uc = (unsigned char *)&rdata.ip_src;
	sprintf(ip_src,"%u.%u.%u.%u", ptr_uc[3], ptr_uc[2], ptr_uc[1], ptr_uc[0]);
    memcpy(srcip, ip_src, 20);
    // ptr_uc = NULL;
	ptr_uc = (unsigned char *)&rdata.ip_dst;
	sprintf(ip_src,"%u.%u.%u.%u", ptr_uc[3], ptr_uc[2], ptr_uc[1], ptr_uc[0]);
    fprintf(fp, "%.18s, %s, %s, %u, %u, %u, %u, %u, %u drops\n", mac_addr, srcip, ip_src, rdata.port_src, rdata.port_dst, rdata.sequence, rdata.ack_sequence, rdata.in_time, rdata.dpl);
    // printf("Drops: %d, %d, %u, %u, %u, %u, %u\n", rdata.ip_src, rdata.ip_dst, rdata.port_src, rdata.port_dst, rdata.sequence, rdata.ack_sequence, rdata.in_time);
    // if(fd == NULL)
    // {
    // 	fd = (struct flow_and_dropped_c *)malloc(sizeof(struct flow_and_dropped_c));
    // 	memset(fd, 0, sizeof(struct flow_and_dropped_c));

    // 	memcpy(fd->dataflow.mac, mac, 6);
    // 	fd->dataflow.ip_src 		= rdata.ip_src;
    // 	fd->dataflow.ip_dst 		= rdata.ip_dst;
    // 	fd->dataflow.port_src 		= rdata.port_src;
    // 	fd->dataflow.port_dst 		= rdata.port_dst;
    // 	fd->next = NULL;
    // 	last_fd = fd;
    // }
    // else
    // {
    // 	int tmp = 0;
    // 	struct flow_and_dropped_c *cur = NULL;
    // 	tmp = find_flow_drop(&rd, cur, mac);
    // 	if(tmp == NOT_FOUND)
    // 	{
	   //  	struct flow_and_dropped_c *new = NULL;
	   //  	new = (struct flow_and_dropped_c *)malloc(sizeof(struct flow_and_dropped_c));
	   //  	memset(new, 0, sizeof(struct flow_and_dropped_c));

	   //  	memcpy(new->dataflow.mac, mac, 6);
	   //  	new->dataflow.ip_src 		= rdata.ip_src;
	   //  	new->dataflow.ip_dst 		= rdata.ip_dst;
	   //  	new->dataflow.port_src 		= rdata.port_src;
	   //  	new->dataflow.port_dst 		= rdata.port_dst;
	   //  	new->next = NULL;
	   //  	last_fd->next = new;
	   //  	last_fd = new;
    // 	}
    // 	else if(tmp == FOUND_DIFF)
	   //  {	
	   //  	if(!cur)
	   //  		printf("impossible drops\n");
	   //  	else
	   //  	{
		  //   	struct flow_and_dropped_c *new = NULL, *tmp = NULL;
		  //   	new = (struct flow_and_dropped_c *)malloc(sizeof(struct flow_and_dropped_c));
		  //   	memset(new, 0, sizeof(struct flow_and_dropped_c));

		  //   	memcpy(new->dataflow.mac, mac, 6);
		  //   	new->dataflow.ip_src 		= rdata.ip_src;
		  //   	new->dataflow.ip_dst 		= rdata.ip_dst;
		  //   	new->dataflow.port_src 		= rdata.port_src;
		  //   	new->dataflow.port_dst 		= rdata.port_dst;
		  //   	new->next = NULL;
		  //   	tmp = cur->next;
	   //  		*cur = *new;
	   //  		cur->next = tmp;
	   //  	}
	   //  }
    // }

}
/**
 * [decode_iw description]
 * Decoding wireless information of data links from buffer. Also, a list of received links informations
 * are stored. Based on this list, the information of links can be derived.
 * @author linger 2018-04-13
 * @param  buf [description]
 */
void decode_iw(char *buf)
{
	struct data_iw_new rdata;

	int length = sizeof(struct data_iw_new);
	__u32 expected_throughput_tmp;
	float expected_throughput;
	char station[18];
    char mac_addr[18];
    char mac[6];
    struct data_iw old;

    memset(mac, 0, 6);
    memset(&old, 0, sizeof(struct data_iw));
	memset(&rdata, 0, length);
    memcpy(mac, buf, 6);
	memcpy(&rdata, buf + 6, length);
	memset(station, 0, 18);
    memset(mac_addr, 0, 18);
    // print_mac(rdata.station);
    iw_new_2_old(&old, &rdata);
    // pthread_mutex_lock(&mutex_data);
    // if(!iwlist)
    // {
    //     iwlist = (struct data_iw_mac *)malloc(sizeof(struct data_iw_mac));
    //     memset(iwlist, 0, sizeof(struct data_iw_mac));
    //     // *iwlist = old;
    //     iw_to_iw_mac(&old, iwlist, mac);
    //     last_iw = iwlist;
    // }
    // else
    // {
    // 	enum found_results tmp = NOT_FOUND;
    // 	struct data_iw_mac *cur = NULL;
    // 	cur = find_iw(&rdata, &tmp, mac);
    // 	if(tmp == NOT_FOUND)
    // 	{
	   //      struct data_iw_mac *new = NULL;
	   //      new = (struct data_iw_mac *)malloc(sizeof(struct data_iw_mac));
	   //      memset(new, 0, sizeof(struct data_iw_mac));
	   //      iw_to_iw_mac(&old, new, mac);
	   //      last_iw->next = new;
	   //      last_iw = new;
	   //  }
	   //  else if(tmp == FOUND_DIFF)
	   //  {	
	   //  	if(!cur)
	   //  		printf("impossible iw\n");
	   //  	else
	   //  	{
	   //  		struct data_iw_mac new, *tmp = NULL;
	   //  		iw_to_iw_mac(&old, &new, mac);
	   //  		tmp = cur->next;
	   //  		*cur = new;
	   //  		cur->next = tmp;
	   //  	}
	   //  }
    // }
     // pthread_mutex_unlock(&mutex_data);
    reversebytes_uint16t(&rdata.device);
	reversebytes_uint32t(&rdata.inactive_time);
	reversebytes_uint32t(&rdata.rx_bytes);
	reversebytes_uint32t(&rdata.rx_packets);
	reversebytes_uint32t(&rdata.tx_bytes);
	reversebytes_uint32t(&rdata.tx_packets);
	reversebytes_uint32t(&rdata.tx_retries);
	reversebytes_uint32t(&rdata.tx_failed);
	reversebytes_uint32t(&rdata.signal);
	reversebytes_uint32t(&rdata.signal_avg);
	reversebytes_uint32t(&rdata.expected_throughput);
	expected_throughput_tmp = rdata.expected_throughput;
	expected_throughput = (float)expected_throughput_tmp / 1000.0;
	mac_tranADDR_toString_r(rdata.station, station, 18);

    mac_tranADDR_toString_r(mac, mac_addr, 18);
    fprintf(fp, "%.18s, %.18s, %u, %u, %u, %u, %u, %u, %u, %u, %d, %d, %f iw\n",mac_addr, station, rdata.device, rdata.inactive_time, rdata.rx_bytes, rdata.rx_packets, rdata.tx_bytes, rdata.tx_packets, rdata.tx_retries, rdata.tx_failed, rdata.signal, rdata.signal_avg, expected_throughput);
	// printf("IW: %.18s, %u, %u, %u, %u, %u, %u, %u, %u, %d, %d, %f\n",station, rdata.device, rdata.inactive_time, rdata.rx_bytes, rdata.rx_packets, rdata.tx_bytes, rdata.tx_packets, rdata.tx_retries, rdata.tx_failed, rdata.signal, rdata.signal_avg, expected_throughput);
}

/**
 * [decode_queue description]
 * Decoding queue informations.
 * @author linger 2018-04-13
 * @param  buf [description]
 */
void decode_queue(char *buf)
{

	// int queue_id;

	struct data_queue rdata;
	int length = sizeof(struct data_queue);
	char mac_addr[18];
    char mac[6];

	memset(&rdata, 0, length);
    memset(mac, 0, 6);
	memset(mac_addr, 0, 18);
    memcpy(mac, buf, 6);
	memcpy(&rdata, buf + 6, length);

	reversebytes_uint64t(&rdata.bytes);   
	reversebytes_uint32t(&rdata.queue_id);
	reversebytes_uint32t(&rdata.packets);
	reversebytes_uint32t(&rdata.qlen);
	reversebytes_uint32t(&rdata.backlog);
	reversebytes_uint32t(&rdata.drops);
	reversebytes_uint32t(&rdata.requeues);
	reversebytes_uint32t(&rdata.overlimits);
    mac_tranADDR_toString_r(mac, mac_addr, 18);
    fprintf(fp, "%.18s, %u, %llu, %u, %u, %u, %u, %u, %u queue\n", mac_addr, rdata.queue_id, rdata.bytes, rdata.packets, rdata.qlen, rdata.backlog, rdata.drops, rdata.requeues, rdata.overlimits);
	// printf("Queue: %u, %llu, %u, %u, %u, %u, %u, %u\n", rdata.queue_id, rdata.bytes, rdata.packets, rdata.qlen, rdata.backlog, rdata.drops, rdata.requeues, rdata.overlimits);
}
/**
 * [decode_beacon description]
 * Based on beacon information, the informaiton of neighbours can be derived: how many neighbours, their interferences,
 * the frequency usage informations and so on.
 * @author linger 2018-04-13
 * @param  buf [description]
 */
void decode_beacon(char *buf)
{
	int signal;
	char channel_type[] = "802.11a";
	struct data_beacon_new beacon; 
	int length = sizeof(struct data_beacon_new);
	char bssid[18];
    char mac_addr[18];
    char mac[6];
    struct data_beacon old;

	memset(&beacon, 0, length);
	memset(bssid, 0, 18);
    memset(mac_addr, 0, 18);
    memset(mac, 0, 18);
	memcpy(&beacon, buf + 6, length);

    beacon_new_2_old(&old, &beacon);

	// reversebytes_uint16t(&beacon.signal);
	// reversebytes_uint16t(&beacon.data_rate);
	reversebytes_uint16t(&beacon.freq);
	mac_tranADDR_toString_r(beacon.bssid, bssid, 18);
    mac_tranADDR_toString_r(mac, mac_addr, 18);
	// printf("%s %d %d %d\n", bssid, &beacon.freq, &beacon.signal, &beacon.data_rate);
	// pthread_mutex_lock(&mutex_data);
    // if(!bcnlist)
    // {
    //     bcnlist = (struct data_beacon_mac *)malloc(sizeof(struct data_beacon_mac));
    //     memset(bcnlist, 0, sizeof(struct data_beacon_mac));

    //     beacon_to_beacon_mac(&old, bcnlist, mac);
    //     last_beacon = bcnlist;
    // }
    // else
    // {
    // 	enum found_results tmp = NOT_FOUND;
    // 	struct data_beacon_mac *cur = NULL;
    // 	cur = find_beacon(&beacon, &tmp, mac);
    //     if(tmp == NOT_FOUND)
    //     {
	   //      struct data_beacon_mac *new;
	   //     	new = (struct data_beacon_mac *)malloc(sizeof(struct data_beacon_mac));
	   //      memset(new, 0, sizeof(struct data_beacon_mac));

	   //      beacon_to_beacon_mac(&old, new, mac);

	   //      last_beacon->next = new;
	   //      last_beacon = new;

    //     }
    //     else if(tmp == FOUND_DIFF)
    //     {
	   //  	if(!cur)
	   //  	{
	   //  		print_mac(beacon.bssid);
	   //  		printf("impossible beacon\n");
	   //  	}
	   //  	else
	   //  	{
	   //  		struct data_beacon_mac new, *tmp = NULL;
	   //  		beacon_to_beacon_mac(&old, &new, mac);

	   //  		tmp = cur->next;
	   //  		*cur = new;
	   //  		cur->next = tmp;
	   //  		// printf("after\n");
	   //  		// print_beacon();

	   //  	}        	
    //     }
    // }
    // pthread_mutex_unlock(&mutex_data);
    fprintf(fp, "%.18s, %u, %u, %d, %.18s beacon\n", mac_addr, beacon.data_rate, beacon.freq, beacon.signal, bssid);
    // printf("Beacon origin: %u, %u, %d, %.18s\n", beacon.data_rate, beacon.freq, beacon.signal, bssid);
    // print_mac(beacon.bssid);
    // printf("begin\n");
    // print_beacon();
    // printf("end\n");
}

/**
 * [decode_survey description]
 * Processing wireless information of ap, also, the information of received aps are stored in a list, based on this list, 
 * wireless information of ap can be derived.
 * @author linger 2018-04-13
 * @param  buf [description]
 */
void decode_survey(char *buf)
{
	struct data_survey rdata;
	int length = sizeof(struct data_survey);
    char mac[6];
    char mac_addr[18];

    memset(mac, 0, 6);
    memset(mac_addr, 0, 18);
    memcpy(mac, buf, 6);
	memset(&rdata, 0, length);
	memcpy(&rdata, buf + 6, length);

	reversebytes_uint64t(&rdata.time);
	reversebytes_uint64t(&rdata.time_busy);
	reversebytes_uint64t(&rdata.time_ext_busy);
	reversebytes_uint64t(&rdata.time_rx);
	reversebytes_uint64t(&rdata.time_tx);
	reversebytes_uint64t(&rdata.time_scan);
	reversebytes_uint32t(&rdata.filled);
	reversebytes_uint16t(&rdata.center_freq);
    mac_tranADDR_toString_r(mac, mac_addr, 18);
    fprintf(fp, "%.18s, %llu, %llu, %llu, %llu, %llu, %llu, %u, %d survey\n", mac_addr, rdata.time, rdata.time_busy, rdata.time_ext_busy, rdata.time_rx, rdata.time_tx, rdata.time_scan, rdata.center_freq, rdata.noise);
	// printf("Survey: %llu, %llu, %llu, %llu, %llu, %llu %u %d \n", rdata.time, rdata.time_busy, rdata.time_ext_busy, rdata.time_rx, rdata.time_tx, rdata.time_scan, rdata.center_freq, rdata.noise);
	// pthread_mutex_lock(&mutex_data);
    // if(!sur_list)
    // {
    //     sur_list = (struct data_survey_c *)malloc(sizeof(struct data_survey_c));
    //     memset(sur_list, 0, sizeof(struct data_survey_c));

    //     survey_to_survey_mac(&rdata, sur_list, mac);
    //     last_sur = sur_list;
    // }
    // else
    // {
    // 	enum found_results tmp = 0;
    // 	struct data_survey_c *cur = NULL;
    // 	cur = find_survey(&rdata, &tmp, mac);
    //     if(tmp == NOT_FOUND)
    //     {
	   //      struct data_survey_c *new;
	   //     	new = (struct data_survey_c *)malloc(sizeof(struct data_survey_c));
	   //      memset(new, 0, sizeof(struct data_survey_c));

	   //      survey_to_survey_mac(&rdata, new, mac);
	   //      last_sur->next = new;
	   //      last_sur = new;
    //     }
    //     else if(tmp == FOUND_DIFF)
    //     {
	   //  	if(!cur)
	   //  		printf("impossible survey\n");
	   //  	else
	   //  	{
	   //  		struct data_survey_c new;
	   //  		survey_to_survey_mac(&rdata, &new, mac);
	   //  		// printf("%llu abc, %llu def, %llu jkm, %llu lsr, %llu deb, %llu xx, %u yy\n", new.time, new.time_busy, new.time_ext_busy, new.time_rx, new.time_tx, new.time_scan, new.center_freq);
	   //  		*cur = new;
	   //  	}        	
    //     }
    // }
	
    // pthread_mutex_unlock(&mutex_data);   	
}

/**
 * [decode_kiw description]
 * keep_iw is a substracted version of iw information. It means sampled iw information is the same as last transmitted.
 * Based on mac address of corresponding ap, station mac address, we searched in last-received list and get the real 
 * iw information.
 * @author linger 2018-04-13
 * @param  buf [description]
 */
void decode_kiw(char *buf)
{
    char data[6];
    struct data_iw *tmp = NULL;
    struct data_iw_new rdata;
    char station[18];
    char mac_addr[18];
    char mac[6];
	__u32 expected_throughput_tmp;
	float expected_throughput;

    memset(station, 0, 18);
    memset(mac_addr, 0, 18);
    memset(mac, 0, 6);
    memset(&rdata, 0, sizeof(struct data_iw_new));
    memset(data, 0, 6);
    memcpy(data, buf, 6);
    memcpy(mac, buf + 6, 6);

    tmp = find_keep_iw(data, mac);
    if(tmp)
    {
        iw_old_2_new(&rdata, tmp);
        free(tmp);
        tmp = NULL;
        // printf("eee\n");

	    reversebytes_uint16t(&rdata.device);
		reversebytes_uint32t(&rdata.inactive_time);
		reversebytes_uint32t(&rdata.rx_bytes);
		reversebytes_uint32t(&rdata.rx_packets);
		reversebytes_uint32t(&rdata.tx_bytes);
		reversebytes_uint32t(&rdata.tx_packets);
		reversebytes_uint32t(&rdata.tx_retries);
		reversebytes_uint32t(&rdata.tx_failed);
		reversebytes_uint32t(&rdata.signal);
		reversebytes_uint32t(&rdata.signal_avg);
		reversebytes_uint32t(&rdata.expected_throughput);
		expected_throughput_tmp = rdata.expected_throughput;
		expected_throughput = (float)expected_throughput_tmp / 1000.0;

    	mac_tranADDR_toString_r(rdata.station, station, 18);
        mac_tranADDR_toString_r(mac, mac_addr, 18);
   		fprintf(fp, "%.18s, %.18s, %u, %u, %u, %u, %u, %u, %u, %u, %d, %d, %f kiw\n",mac_addr, station, rdata.device, rdata.inactive_time, rdata.rx_bytes, rdata.rx_packets, rdata.tx_bytes, rdata.tx_packets, rdata.tx_retries, rdata.tx_failed, rdata.signal, rdata.signal_avg, expected_throughput);
    	// printf("Kiw: %.18s, %u, %u, %u, %u, %u, %u, %u, %u, %d, %d, %f kiw\n",station, rdata.device, rdata.inactive_time, rdata.rx_bytes, rdata.rx_packets, rdata.tx_bytes, rdata.tx_packets, rdata.tx_retries, rdata.tx_failed, rdata.signal, rdata.signal_avg, expected_throughput);
    }
    else
        fprintf(fp, "omg, keep_iw can not find the original iw structure\n");
    // else
    // {
    //     // print_mac(data);
    //     // printf("omg, keep_iw can not find the original iw structure\n");
    //     // print_mac(data);
    //     // print_iw_list();
    //     // printf("overoveroverover\n");
    // }

}

/**
 * [decode_kib description]
 * Substracted version of beacon information.
 * @author linger 2018-04-13
 * @param  buf [description]
 */
void decode_kib(char *buf)
{
    char data[6];
    struct data_beacon *tmp = NULL;
    struct data_beacon_new rdata;
    char bssid[18];
    char mac_addr[18];
    char mac[6];

    memset(mac_addr, 0, 18);
    memset(mac, 0, 6);
    memset(bssid, 0, 18);
    memset(&rdata, 0, sizeof(struct data_beacon_new));
    memset(data, 0, 6);
    memcpy(data, buf, 6);
    memcpy(mac, buf + 6, 6);

	tmp = find_keep_beacon(data, mac);
    if(tmp)
    {
    	// printf("nimmmmmm\n");
	    beacon_old_2_new(&rdata, tmp);
	    mac_tranADDR_toString_r(rdata.bssid, bssid, 18);
        mac_tranADDR_toString_r(mac, mac_addr, 18);
	    fprintf(fp, "%.18s, %.18s, %u, %u, %d kib\n", mac_addr, bssid, rdata.data_rate, rdata.freq, rdata.signal);
	    free(tmp);
	    tmp = NULL;
	    // printf("kib: %u, %u, %d, %.18s\n", rdata.data_rate, rdata.freq, rdata.signal, bssid);
	}
	// else
	// {
	// 	printf("omg, keep_beacon can not find the original beacon structure\n");
	// 	print_mac(data);
	// 	// printf("1\n");

	// 	// printf("2\n");
	// 	// print_beacon();
	// }
}

/**
 * [destroy_iwlist description]
 * destroy iwlist.
 * @author linger 2018-04-13
 * @param  str [description]
 */
void destroy_iwlist(struct data_iw_mac *str)
{
    struct data_iw_mac *ptr = NULL;
    ptr = str;
    while(ptr)
    {
        struct data_iw_mac *tmp = NULL;
        tmp = ptr;
        ptr = ptr->next;
        free(tmp);
        tmp = NULL;
    }
    last_iw = NULL;
}

/**
 * [find_iw description]
 * When a new data structre are get, we first search whether there is information for its corresponding
 * links, if there is, update it, insert if not.
 * @author linger 2018-04-13
 * @param  t   [got iw data structure]
 * @param  cur [if the corresponding list node are found, return it, NULL if not.	]
 * @return     [FOUND_SAME if there is and it is the same. FOUND_DIFF, found, not the same, NOT_FOUND if not found.]
 */
static struct data_iw_mac *find_iw(struct data_iw_new *t, enum found_results *ret, char *mac)
{
	struct data_iw_mac *ptr = NULL;
	ptr = iwlist;
	while(ptr)
	{
		int condition = 0;
		if((strcmp_linger(ptr->station, t->station) == 0) && (strcmp_linger(ptr->mac, mac) == 0))
		{
			condition = 
			ptr->rx_bytes 		== t->rx_bytes 			+
			ptr->tx_bytes 		== t->tx_bytes 			+ 	ptr->tx_retries 			== t->tx_retries		   + 
			ptr->tx_failed  	== t->tx_failed			+ 	ptr->signal 				== t->signal 			   +
			ptr->signal_avg 	== t->signal_avg 		+ 	ptr->expected_throughput 	== t->expected_throughput;
			if(condition == 7)
			{
				*ret = FOUND_SAME;
				return ptr;
			}
			else
			{
				// delete_the_node(pre, ptr, ptr->next);
				*ret = FOUND_DIFF;
				return ptr;
			}		
		}
		ptr = ptr->next;
	}
	*ret = NOT_FOUND;
	return NULL;
}

/**
 * [find_flow_drop description]
 * Search found for drop information.
 * @author linger 2018-04-13
 * @param  t   [description]
 * @param  cur [description]
 * @return     [description]
 */
static enum found_results find_flow_drop(struct dp_packet *t, struct flow_and_dropped_c *cur, char *mac)
{
	struct flow_and_dropped_c *ptr = NULL;
	ptr = fd;
	while(ptr)
	{
		int condition = 	(strcmp_linger(ptr->dataflow.mac, mac) == 0) 
							&& (ptr->dataflow.ip_src 	== t->ip_src) 
							&& (ptr->dataflow.ip_dst 	== t->ip_dst) 
							&& (ptr->dataflow.port_src 	== t->port_src) 
							&& (ptr->dataflow.port_dst 	== t->port_dst);
		if(condition == 5)
		{
			if(ptr->drops == t->drop_count)
				return FOUND_SAME;
			else
			{
				cur = ptr;
				return FOUND_DIFF;
			}		
		}
		ptr = ptr->next;
	}
	return NOT_FOUND;
}
static struct data_beacon_mac *find_beacon(struct data_beacon_new *t, enum found_results *ret, char *mac)
{
	struct data_beacon_mac *ptr;
	ptr = bcnlist;
	while(ptr)
	{
		int condition = 0;
		if((strcmp_linger(ptr->bssid, t->bssid) == 0) && (strcmp_linger(ptr->mac, mac) == 0))
		{
			condition = 
			ptr->data_rate 		== 	t->data_rate 	+ 
			ptr->freq 			==	t->freq 		+
			ptr->signal 		== 	t->signal;

			if(condition == 3)
			{
				*ret = FOUND_SAME;
				return ptr;
			}

			else
			{
				*ret = FOUND_DIFF;
				return ptr;
			}
		}
		ptr = ptr->next;
	}
	*ret = NOT_FOUND;
	return NULL;
}

static struct data_survey_c  *find_survey(struct data_survey *t, enum found_results *res, char *mac)
{
	struct data_survey_c *ptr;
	ptr = sur_list;
	while(ptr)
	{
		int condition = 0;
		if(strcmp_linger(ptr->mac, mac) == 0)
		{
			*res = FOUND_DIFF;
			return ptr;
		}
		ptr = ptr->next;
	}
	*res = NOT_FOUND;
	return NULL;
}

void destroy_bcnlist(struct data_beacon *str)
{
    struct data_beacon *ptr = NULL;
    ptr = str;
    while(ptr)
    {
        struct data_beacon *tmp = NULL;
        tmp = ptr;
        ptr = ptr->next;
        free(tmp);
        tmp = NULL;
    }
    last_beacon = NULL;
}

/**
 * [iw_new_2_old description]
 * Translate data_iw_new structure to data_iw structure, data_iw_new cantains no "*next" member.
 * @author linger 2018-04-13
 * @param  old [data_iw structure]
 * @param  new [data_iw_new structure]
 */
void iw_new_2_old(struct data_iw *old, struct data_iw_new *new)
{
    memcpy(old->station, new->station, 6);
    old->device                 = new->device;
    old->inactive_time          = new->inactive_time;
    old->rx_bytes               = new->rx_bytes;
    old->rx_packets             = new->rx_packets;
    old->tx_bytes               = new->tx_bytes;
    old->tx_packets             = new->tx_packets;
    old->tx_retries             = new->tx_retries;
    old->tx_failed              = new->tx_failed;
    old->signal                 = new->signal;
    old->signal_avg             = new->signal_avg;
    old->expected_throughput    = new->expected_throughput;
    old->next                   = NULL;
}

void iw_old_2_new(struct data_iw_new *old, struct data_iw *new)
{
    memcpy(old->station, new->station, 6);
    old->device                 = new->device;
    old->inactive_time          = new->inactive_time;
    old->rx_bytes               = new->rx_bytes;
    old->rx_packets             = new->rx_packets;
    old->tx_bytes               = new->tx_bytes;
    old->tx_packets             = new->tx_packets;
    old->tx_retries             = new->tx_retries;
    old->tx_failed              = new->tx_failed;
    old->signal                 = new->signal;
    old->signal_avg             = new->signal_avg;
    old->expected_throughput    = new->expected_throughput;
}

void beacon_new_2_old(struct data_beacon *old, struct data_beacon_new *new)
{
    old->data_rate  = new->data_rate;
    old->freq       = new->freq;
    old->signal     = new->signal;
    memcpy(old->bssid, new->bssid, 6);
    old->next = NULL;
}

void beacon_old_2_new(struct data_beacon_new *old, struct data_beacon *new)
{
    old->data_rate  = new->data_rate;
    old->freq       = new->freq;
    old->signal     = new->signal;
    memcpy(old->bssid, new->bssid, 6);
}


/**
 * [find_keep_iw description]
 * Find the real iw information which corresponding to keep_iw structures, using app address and client 
 * mac address.
 * @author linger 2018-04-13
 * @param  station [description]
 * @return         [description]
 */
struct data_iw *find_keep_iw(char *station, char *mac)
{
    struct data_iw_mac *ptr = NULL;
    struct data_iw *ret = NULL;

    ret = (struct data_iw *)malloc(sizeof(struct data_iw));
    memset(ret, 0, sizeof(struct data_iw));
    ptr = iwlist;
    // print_iw_list();

    while(ptr)
    {
        // print_mac(station);
        // print_mac(ptr->station);
        // print_mac(mac);
        // print_mac(ptr->mac);
        if((strcmp_linger(ptr->station, station) == 0) && (strcmp_linger(ptr->mac, mac) == 0))
        {
            // printf("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n");
        	iw_mac_to_iw(ptr, ret);
            return ret;
        }
        ptr = ptr->next;
    }
    // printf("yyyyyyyyyyyyyyyyyyyyyyyyyyyy\n");
    return NULL;
}

struct data_beacon *find_keep_beacon(char *bssid, char *mac)
{
    struct data_beacon_mac *ptr = NULL;
    struct data_beacon *ret = NULL;

    ret = (struct data_beacon *)malloc(sizeof(struct data_beacon));
    memset(ret, 0, sizeof(struct data_beacon));
    ptr = bcnlist;
    // print_iw_list();
    while(ptr)
    {
        if((strcmp_linger(ptr->bssid, bssid) == 0) && (strcmp_linger(ptr->mac, mac) == 0))
        {
        	beacon_mac_to_beacon(ptr, ret);
            return ret;
        }
        ptr = ptr->next;
    }
    return NULL;
}

/**
 * [print_iw_list description]
 * For debugging.
 * @author linger 2018-04-13
 */
void print_iw_list(void)
{
	struct data_iw_mac *ptr = NULL;
	ptr = iwlist;
	while(ptr)
	{
		print_mac(ptr->station);
		ptr = ptr->next;
	}
}

void print_beacon(void)
{
	struct data_beacon_mac *ptr = NULL;
	ptr = bcnlist;
	while(ptr)
	{
		// printf("ptr->bssid %s\n", ptr->bssid);
		print_mac(ptr->bssid);
		ptr = ptr->next;
	}
}


void iw_mac_to_iw(struct data_iw_mac *p, struct data_iw *q)
{
	if(p && q)
	{
		memcpy(q->station, p->station, 6);
		q->device 					= p->device;
		q->inactive_time 			= p->inactive_time;
		q->rx_bytes 				= p->rx_bytes;
		q->rx_packets 				= p->rx_packets;
		q->tx_bytes 				= p->tx_bytes;
		q->tx_packets 				= p->tx_packets;
		q->tx_retries 				= p->tx_retries;
		q->tx_failed 				= p->tx_failed;
		q->signal 					= p->signal;
		q->signal_avg 				= p->signal_avg;
		q->expected_throughput 		= p->expected_throughput;
		q->next = NULL;
	}	
}

void iw_to_iw_mac(struct data_iw *p, struct data_iw_mac *q, char *mac)
{
	if(p && q)
	{
		memcpy(q->station, p->station, 6);
		memcpy(q->mac, mac, 6);
		q->device 					= p->device;
		q->inactive_time 			= p->inactive_time;
		q->rx_bytes 				= p->rx_bytes;
		q->rx_packets 				= p->rx_packets;
		q->tx_bytes 				= p->tx_bytes;
		q->tx_packets 				= p->tx_packets;
		q->tx_retries 				= p->tx_retries;
		q->tx_failed 				= p->tx_failed;
		q->signal 					= p->signal;
		q->signal_avg 				= p->signal_avg;
		q->expected_throughput 		= p->expected_throughput;
		q->next = NULL;
	}
}

void dp_to_dpnew(struct dp_packet *s, struct dp_packet_new *t)
{
	if(s && t)
	{
		t->ip_src 			= s->ip_src;
		t->ip_dst 			= s->ip_dst;
		t->port_src 		= s->port_src;
		t->port_dst 		= s->port_dst;
		t->sequence 		= s->sequence;
		t->ack_sequence 	= s->ack_sequence;
		t->drop_count 		= s->drop_count;
		t->dpl				= s->dpl;
		t->in_time 			= s->in_time;
	}
}

void dpnew_to_dp(struct dp_packet_new *s, struct dp_packet *t)
{
	if(s && t)
	{
		t->ip_src 			= s->ip_src;
		t->ip_dst 			= s->ip_dst;
		t->port_src 		= s->port_src;
		t->port_dst 		= s->port_dst;
		t->sequence 		= s->sequence;
		t->ack_sequence 	= s->ack_sequence;
		t->drop_count 		= s->drop_count;
		t->dpl				= s->dpl;
		t->in_time 			= s->in_time;
		t->next 			= NULL;
	}
}


void beacon_to_beacon_mac(struct data_beacon *p, struct data_beacon_mac *q, char *mac)
{
	if(p && q)
	{
		memcpy(q->bssid, p->bssid, 6);
		memcpy(q->mac, mac, 6);
		q->data_rate 					= p->data_rate;
		q->freq 						= p->freq;
		q->signal 					 	= p->signal;
		q->timein 						= p->timein;
		q->next = NULL;
	}
}

void beacon_mac_to_beacon(struct data_beacon_mac *p, struct data_beacon *q)
{
	if(p && q)
	{
		memcpy(q->bssid, p->bssid, 6);
		q->data_rate 					= p->data_rate;
		q->freq 						= p->freq;
		q->signal 					 	= p->signal;
		q->timein 						= p->timein;
		q->next = NULL;
	}
}

void survey_to_survey_mac(struct data_survey *p, struct data_survey_c *q, char *mac)
{
	if(p && q)
	{
		memcpy(q->mac, mac, 6);
		q->time 					= p->time;
		q->time_busy 				= p->time_busy;
		q->time_ext_busy 			= p->time_ext_busy;
		q->time_rx 					= p->time_rx;
		q->time_tx 					= p->time_tx;
		q->time_scan 				= p->time_scan;
		q->filled 					= p->filled;
		q->noise 					= p->noise;
		q->center_freq 				= p->center_freq;
		q->next = NULL;
	}
}

void survey_mac_to_survey(struct data_survey_c *p, struct data_survey *q)
{
	if(p && q)
	{
		q->time 					= p->time;
		q->time_busy 				= p->time_busy;
		q->time_ext_busy 			= p->time_ext_busy;
		q->time_rx 					= p->time_rx;
		q->time_tx 					= p->time_tx;
		q->time_scan 				= p->time_scan;
		q->filled 					= p->filled;
		q->noise 					= p->noise;
		q->center_freq 				= p->center_freq;
	}
}

/**
 * [get_attatched_aps description]
 * get all the active aps that are connected to sdn platform.
 * @author linger 2018-04-13
 * @param  mac_list [the list of mac addresses of attatched aps.]
 * @return          the number of the attatched aps.
 */
int get_attatched_aps(char **mac_list)
{
	struct data_beacon_mac *ptr;
	int control = 0;
	ptr = bcnlist;
	// pthread_mutex_lock(&mutex_data);
	if(ptr)
	{
		while(ptr)
		{
			if(mac_list[control])
			{
				memcpy(mac_list[control], ptr->mac, 6);
				control += 1;
			}
			ptr = ptr->next;
		}
	}
	// pthread_mutex_unlock(&mutex_data);
  	return control - 1;
}

/**
 * [get_all_aps description]
 * get all the APs of the networks.
 * @author linger 2018-04-13
 * @param  mac_list [description]
 * @return          number of all the aps
 */
int get_all_aps(char **mac_list)
{
	struct data_beacon_mac *ptr;
	int control = 0;
	ptr = bcnlist;
	// pthread_mutex_lock(&mutex_data);
	if(ptr)
	{
		while(ptr)
		{
			if(mac_list[control])
			{
				int i = 0;
				int found = 0;
				while(i < control)
				{
					if(strcmp_linger(mac_list[i], ptr->mac) == 0)
					{
						found = 1;
						break;
					}
					i += 1;
				}
				if(found == 0)
				{
					memcpy(mac_list[control], ptr->mac, 6);
					control += 1;
				}
			}
			ptr = ptr->next;
		}
	}
	// pthread_mutex_unlock(&mutex_data);
  	return control -1;
}

/**
 * [get_neighbour_py description]
 * get neighbours of AP ap.
 * @author linger 2018-04-13
 * @param  ap       AP ap
 * @param  neibours its neighbours
 * @return          number of its neighbours
 */
int get_neighbour_py(char *ap, struct aplist_py *neibours)
{
	struct data_beacon_mac *ptr;
	int control = 0;
	ptr = bcnlist;
	// pthread_mutex_lock(&mutex_data);
	if(ptr)
	{
		while(ptr)
		{
			if(neibours->aplists[control])
			{
				if(strcmp_linger(ptr->mac, ap) == 0)
				{
					memcpy(neibours->aplists[control], ptr->mac, 6);
					control += 1;
				}
			}
			ptr = ptr->next;
		}
	}
	// pthread_mutex_unlock(&mutex_data);
  	return control - 1;	
}

/**
 * [get_neighbour description]
 * @author linger 2018-04-13
 * @param  ap       [description]
 * @param  neibours [description]
 * @return          [description]
 */
int get_neighbour(char *ap, struct aplist *neibours)
{
	struct data_beacon_mac *ptr;
	int control = 0;
	ptr = bcnlist;
	// pthread_mutex_lock(&mutex_data);
	if(ptr)
	{
		while(ptr)
		{
			if(neibours->aplists[control])
			{
				if(strcmp_linger(ptr->mac, ap) == 0)
				{
					memcpy(neibours->aplists[control], ptr->mac, 6);
					control += 1;
				}
			}
			ptr = ptr->next;
		}
	}
	if(neibours)
		neibours->length = control - 1;
	// pthread_mutex_unlock(&mutex_data);
	return control - 1;
}

/**
 * [get_clients description]
 * Get clients of AP ap.
 * @author linger 2018-04-13
 * @param  ap      AP ap
 * @param  clients array to store ap's clients.
 * @return         number of clients of AP ap.
 */
int get_clients(char *ap, struct aplist *clients)
{
	struct data_iw_mac *ptr;
	int control = 0;

	// pthread_mutex_lock(&mutex_data);
	ptr = iwlist;

	while(ptr)
	{
		if(strcmp_linger(ptr->mac, ap) == 0)
		{
			if(clients)
			{
				memcpy(clients->aplists[control], ptr->station, 6);
				control += 1;
			}
		}
		ptr = ptr->next;
	}
	if(clients)
		clients->length = control - 1;
	// pthread_mutex_unlock(&mutex_data);
	return control - 1;
}

int get_clients_py(char *ap, struct aplist_py *clients)
{
	struct data_iw_mac *ptr;
	int control = 0;

	// pthread_mutex_lock(&mutex_data);
	ptr = iwlist;

	while(ptr)
	{
		if(strcmp_linger(ptr->mac, ap) == 0)
		{
			if(clients->aplists[control])
			{
				memcpy(clients->aplists[control], ptr->station, 6);
				control += 1;
			}
		}
		ptr = ptr->next;
	}
	if(clients)
		clients->length = control - 1;
	// pthread_mutex_unlock(&mutex_data);
	return control -1 ;
}

/**
 * [get_flows description]
 * get tcp flow of AP ap.
 * @author linger 2018-04-13
 * @param  ap        [description]
 * @param  flowlists [description]
 * @return           [description]
 */
int get_flows(char *ap, struct flowlist *flowlists)
{
	struct flow_chain *t = NULL, *ptr = NULL;
	int control = 0;

	flows_dump(t);
	ptr = t;
	// pthread_mutex_lock(&mutex_data);
	while(ptr)
	{
		if(strcmp_linger(ptr->mac, ap) == 0)
		{
			if(flowlists)
			{
				memcpy(flowlists->flows[control].mac, ptr->mac, 6);
				flowlists->flows[control].ip_src 		= ptr->ip_src;
				flowlists->flows[control].ip_dst 		= ptr->ip_dst;
				flowlists->flows[control].port_src 	= ptr->port_src;
				flowlists->flows[control].port_dst 	= ptr->port_dst;
				control += 1;
			}
			else
				printf("more structures to store data\n");
		}
		ptr = ptr->next;
		
	}
	// pthread_mutex_unlock(&mutex_data);
	return control - 1;
}

/**
 * [get_flow_drops description]
 * Get the packet dropping information of AP ap. In order to derive this information, 
 * a list is maintained, node of this list stores packet dropping information of tcp flow
 * and update when new dropping information arrives.
 * @author linger 2018-04-13
 * @param  ap         [description]
 * @param  flow_drops [description]
 * @return            [description]
 */
int get_flow_drops(char *ap, struct flow_drop_ap_array *flow_drops)
{
	struct flow_and_dropped_c *t = NULL, *ptr = NULL;
	int control = 0;

	// pthread_mutex_lock(&mutex_data);
	t = fd;
	ptr = t;

	while(ptr)
	{
		if(control < 50)
		{
			memcpy(flow_drops->flowinfo[control].dataflow.mac, ptr->dataflow.mac, 6);
			flow_drops->flowinfo[control].dataflow.ip_src 		= ptr->dataflow.ip_src;
			flow_drops->flowinfo[control].dataflow.ip_dst 		= ptr->dataflow.ip_dst;
			flow_drops->flowinfo[control].dataflow.port_src 	= ptr->dataflow.port_src;
			flow_drops->flowinfo[control].dataflow.port_dst 	= ptr->dataflow.port_dst;
			control += 1;
		}
		else
			printf("more structures to store data\n");
		ptr = ptr->next;
	}
	// pthread_mutex_unlock(&mutex_data);
	return control - 1;
}

/**
 * [get_wireless_info description]
 * Getting wireless information of AP ap.
 * @author linger 2018-04-13
 * @param  ap      [description]
 * @param  clients [description]
 */
void get_wireless_info(char *ap, struct data_survey *clients)
{
	struct data_survey_c *ptr;
	ptr = sur_list;
	// pthread_mutex_lock(&mutex_data);
	if(ptr)
	{
		while(ptr)
		{
			if(strcmp_linger(ptr->mac, ap) == 0)
			{
				if(clients)
				{
					struct data_survey tmp;
					survey_mac_to_survey(ptr, &tmp);
					*clients = tmp;
					break;
				}
			}
			ptr = ptr->next;
		}
	}
	// pthread_mutex_unlock(&mutex_data);
}

int main()
{
	// pthread_t tid1;

    FILE *fp_r  = NULL;
    int read_line = 0;
    int write_line = 0;

    char buffer[SIZE];
    // pthread_mutex_init(&mutex_data, NULL);
    fp_r = fopen("debug1.txt", "rb");
    if(!fp_r)
        return -1;
    fp = fopen("destructeddata.txt", "wb");
    if(!fp)
        return -1;
    memset(buffer, 0, SIZE);
    read_line = fread(buffer, SIZE, 1, fp_r);
    // write_line = fwrite(buffer, SIZE, 1, fp_w);
    while(read_line)
    {
        memset(buffer, 0, SIZE);
        read_line = fread(buffer, SIZE, 1, fp_r);
        process(buffer);
        // write_line = fwrite(buffer, SIZE, 1, fp_w);        
    }

    if(fp_r)
        fclose(fp_r);
    if(fp)
        fclose(fp);

    hash_table_init(); 


   // err = pthread_create(&tid2, NULL, g_mes_tn_process, NULL);
  // if(err != 0)
  // {
  //   printf("g_mes_tn_process creation failed \n");
  //   exit(1);
  // }
  // else
  // {
  //   printf("23\n");
  // }
  // err = pthread_create(&tid3, NULL, receive6683, NULL);
  // if(err != 0)
  // {
  //   printf("receive6683%d creation failed \n", i);
  //   exit(1);
  // }
    // fclose(fp);
    // pthread_mutex_destroy(&mutex_data);
    hash_table_release();
}

void print_mac(char *addr)
{
	int len = 18;
	char str[18];
	mac_tranADDR_toString_r(addr, str, 18);
	printf("%s\n", str);
}
void print_string(char *str, int length)
{
	int i = 0;
	for(i = 0; i < length; i++)
	{
		printf("%2x", str[i]);
	}
	printf("\n");
}

void f_print_string(char *str, int length)
{
	int i = 0, k = 0;
	char buf[100];
	memset(buf, 0, 100);
	i = 0;
    count1 += 1;
    if((count1 % 1000) == 0)
    {
        printf("fprintf is %d\n", count1);
    }
	while(i < length)
	{
		// printf("%02x ", (unsigned char)*(str + i));
		snprintf(buf + k, 10, "%02x ", (unsigned char)*(str + i));
		i = i + 1;
		k = k + 3;
		if((i %16) == 0)
		{
			// i = i + 1;
			// snprintf(buf + i * 2, 10, "\n");
			fprintf(fp, "%s\n", buf);
			// printf("111 %s\n", buf);
			memset(buf, 0, 100);
			k = 0;
		}
	}

	// fprintf("%s\n", buf);
	
}

void f_write_string(char *str, int length)
{
    // int i = 0, k = 0;
    // char buf[100];
    // memset(buf, 0, 100);
    // i = 0;
    // fprintf(fp, "=======================================================\n");

    // while(i < length)
    // {
    //     // printf("%02x ", (unsigned char)*(str + i));
    //     snprintf(buf + k, 10, "%02x ", (unsigned char)*(str + i));
    //     i = i + 1;
    //     k = k + 3;
    //     if((i %16) == 0)
    //     {
    //         // i = i + 1;
    //         // snprintf(buf + i * 2, 10, "\n");
    //         fwrite(str, length, 1, fp);
    //         // printf("111 %s\n", buf);
    //         memset(buf, 0, 100);
    //         k = 0;
    //     }
    // }
    count2 += 1;
    // if((count2 % 1000) == 0)
    // {
    //     // printf("fwrite is %d\n", count2);
    //     if(138000 == count2)
    //     {
    //         fclose(fp);
    //         exit(-1);
    //     }
    // }
     fwrite(str, sizeof(char), length, fp);   
}

int strcmp_linger(char *s, char *t)
{
    int i = 0;
    int condition = 0;
    for(i = 0; i < 6; i++)
    {
        int tmp = 1000;
        tmp = (int)*(s + i) - (int)*(t + i);
        if(tmp == 0)
            condition += 1;
    }
    // printf("%d\n", condition);
    return (condition == 6)? 0:1;
}