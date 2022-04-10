import asyncio
#import uvloop
import time
import aiohttp
import logging
import json
import re
import socket
import numpy as np
from argparse import ArgumentParser

async def download_site(session, url):
     #print (url)
     
     response = await session.request(method="GET", url=url[0], params=url[1], ssl=False, expect100=False)
     async with response:
         stat = response.status 
         logging.debug('Status '+ stat)
         response.release()
         return stat
     
sem = asyncio.Semaphore(3)

async def safe_download(url, session):
    with sem as sem:  
        return await download_site(session, url)

def initilizeLink(interface):
    os.system("ethtool -K %s sg off"%interface)
    os.system("ethtool -K %s tso off"%interface)
    os.system("ethtool -K %s gso off"%interface)
    os.system("ethtool -K %s gro off"%interface)

async def download_all_sites(sites, session):
    
        tasks = []
        for url in sites:
            #print ("SSSS")
            task = asyncio.ensure_future(download_site(session, url))
            tasks.append(task)
        return await asyncio.gather(*tasks, return_exceptions=False)



async def retrieve_page(json_file, server_ip_addr, page, run, **kwargs):

    headers = {"Connection": "keep-alive"}
    #conn = aiohttp.TCPConnector(limit=6)
    #session = aiohttp.ClientSession()
    
    async with aiohttp.ClientSession(headers=headers, version=(1,1), connector=aiohttp.TCPConnector(limit=6, family=socket.AF_INET), raise_for_status=True) as session:
        start_time = time.time()
        num_main_obj = int(json_file["Run_"+str(run)]["Page_"+str(page)]["num_main_objects"])        
     
        list_obj = list(json_file["Run_"+str(run)]["Page_"+str(page)])
        for main_obj in range(1, num_main_obj+1):
                    
                regex = re.compile(r'inline_%d_[0-9]+'%main_obj)
                inline_objs = [[server_ip_addr, {'user': kwargs["client_num"], 'page': str(page), 'run':str(run), 'obj':i}] for i in list_obj if  regex.search(i)]
                
                    
                # download main object
                main_list = [[server_ip_addr, {'user': kwargs["client_num"], 'page': str(page), 'run':str(run), 'obj':"main_%d"%main_obj}]]
                tasks = []
                for url in main_list:
                    task = asyncio.ensure_future(download_site(session, url))
                    tasks.append(task)
                res = await asyncio.gather(*tasks, return_exceptions=True)
                logging.debug("main obj: " + str(res))
                #res = await download_all_sites(main_list, session)

                logging.info('PLT main object_%d: %d'%(main_obj, int(1000*(time.time() - start_time))))
                #res = await download_all_sites(inline_objs, session)
                tasks = []
                for url in inline_objs:
                    task = asyncio.ensure_future(download_site(session, url))
                    tasks.append(task)
                res = await asyncio.gather(*tasks, return_exceptions=True)
                logging.debug("inline objs: " + str(res))
                                        
        duration = int(1000*(time.time() - start_time))
        logging.info('PLT Page_%d: %d Reading Time: %.3f'%(page, duration, float(json_file["Run_"+str(run)]["Page_"+str(page)]["reading_time"])))
        await asyncio.sleep(0.001)

async def wrap(json_file, server_ip_addr, page, run, **kwargs):
    try:
        await asyncio.wait_for(retrieve_page(json_file, server_ip_addr, page, run, client_num=kwargs["client_num"]), timeout=15.0)
    except asyncio.TimeoutError:
        logging.info('PLT Page_%d: TIMEOUT'%(page))
     

def main(json_file, server_ip_addr, **kwargs):
    
    
    
    run = int(kwargs["run_num"])
    payload = {'user': str(kwargs["client_num"]), 'run':str(run)}
    for page in range(1, int(kwargs["page_num"])+1):
        print ("Page: " + str(page))
        # create session
        #uvloop.install()
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        loop.run_until_complete(wrap(json_file, server_ip_addr, page, run, client_num=kwargs["client_num"]))
        #asyncio.run(wrap(json_file, server_ip_addr, page, run, client_num=kwargs["client_num"]), debug=True)
        time.sleep(min(70,float(json_file["Run_"+str(run)]["Page_"+str(page)]["reading_time"])))
            
            

                    
                
                   
            

parser = ArgumentParser(description="Behavioural web browsing emulator", epilog="")

parser.add_argument('--file', '-f',
					dest="JSON_file",
					action="store",
					help="JSON file with all metadata for browsing",
					required=True)
parser.add_argument('--server_ip_addr', '-sip',
					dest="server_ip",
					action="store",
                    required=True,
					help="IP address of web server"
					)
parser.add_argument('--run_num', '-rn',
					dest="current_run",
					action="store",
                    required=True,
					help="Retrieve page for specific run"
					)
parser.add_argument('--out_path',
					dest="out_path",
					action="store",
					required=True,
					help="Output path where to save log file")

# Expt parameters
args = parser.parse_args()


if __name__ == "__main__":

    # set logging level
    logging.basicConfig(filename=args.out_path, filemode='w', format='%(name)s - %(levelname)s - %(created)f -%(funcName)s - %(lineno)d - %(process)d - %(message)s', level=logging.INFO)
    # parse json file
    _file =  open(args.JSON_file, 'r')
    json_file = json.load(_file)

    match_content = re.search(r'.*_Client_([0-9]+)_R([0-9]+)_W([0-9]+)', args.JSON_file)
    main(json_file, args.server_ip, client_num=match_content.group(1), run_num=int(args.current_run), page_num=match_content.group(3))
    
   
