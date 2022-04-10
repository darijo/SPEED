#!/usr/bin/env python
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301, USA.

import numpy as np
from scipy.stats import weibull_min
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
import json
import os
import re



def getNumMainObj(numWeb):
    res = np.round(np.random.lognormal(0.473844, 0.688471, numWeb), decimals=0)
    return list(map(lambda n: max(1,n), res)) 


def getMainObjSize(numMainObj):
    res = np.round(weibull_min.rvs(0.814944, loc=0, scale=28242.8, size=numMainObj), decimals=0)
    return res


def getNumInlineObj(numMainObj):
    res = np.round(np.random.exponential(scale=31.9291, size=numMainObj), decimals=0)
    return res


def getInlineObjSize(numInlineObj):
    res = np.round(np.random.lognormal(9.17979, 1.24646, numInlineObj), decimals=0)
    return res

def getReadingTimes(numWeb):
    res = np.round(np.random.lognormal(-0.495204, 2.7731, numWeb), decimals=3)
    return res

def generateHTTPModelParametersForUsers(numUsers, numRuns, numPages):
    http_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for cl in range(1, numUsers+1):
        cl_name = "Client_" + str(cl)
        for run in range(1, numRuns+1):
            run_name = "Run_" + str(run)
            # get the number of main objects for each web page and reading times
            list_main_objects = getNumMainObj(numPages)
            reading_times = getReadingTimes(numPages)
     
           
            
            
            
            for web in range(1, numPages+1):
                web_name = "Page_" + str(web)
                num_main_objects = list_main_objects[web-1]
                http_stats[cl_name][run_name][web_name]["num_main_objects"] = num_main_objects
                http_stats[cl_name][run_name][web_name]["reading_time"] = reading_times[web-1] 
                # get size for each main object
                size_main_objects = getMainObjSize(int(num_main_objects))
                main_counter = 1
                for size_main in size_main_objects:
                    http_stats[cl_name][run_name][web_name]["main_"+str(main_counter)] = size_main
                    main_counter+=1
                
                # get number of inline objects per main object
                list_inline_objects = getNumInlineObj(int(num_main_objects))
                main_counter = 1
                for num_inline_object in list_inline_objects:
                    http_stats[cl_name][run_name][web_name]["num_inline_for_main_"+str(main_counter)] = num_inline_object
                    # get number of inline objects per main object
                    size_inline_objects = getInlineObjSize(int(num_inline_object))
                    inline_counter = 1
                    for size_inline in size_inline_objects:
                        http_stats[cl_name][run_name][web_name]["inline_"+str(main_counter)+"_"+str(inline_counter)] = size_inline
                        inline_counter+=1
                    main_counter+=1
    return http_stats

def generateObjects(client_data, client_name):
    for run in client_data:
        run_path = os.path.join(args.out_path, client_name+"/"+run+"/")
        os.system("mkdir -p %s"%run_path)
        for page in client_data[run]:
                 
            page_path = os.path.join(run_path, page)
            os.system("mkdir -p %s"%page_path)
            print (page)
            for content in client_data[run][page]:
                patterns = [r"^main_[0-9]+", r"^inline_[0-9]+_[0-9]+"]
                pattern = "|".join(patterns)
                match_content = re.search(pattern, content) 
                if match_content:
                    obj_path = os.path.join(page_path, content)
                    
                    os.system("fallocate -l %d %s"%(int(client_data[run][page][content]), obj_path))
                else:
                    print (content)

def generateContentForUser(path_to_meta):
    # HTTP_per_client_model_Client_1_R10_W25
    REG_FILENAME = re.compile(r'HTTP_(Client_[0-9]+)_(R[0-9]+)_(W[0-9]+)')
    match = REG_FILENAME.findall(path_to_meta)
    if len(match) == 0:
        return
    print (match[0][0])
    with open(path_to_meta, 'r') as f:
        client_data = json.load(f)
        generateObjects(client_data, match[0][0])
                
parser = ArgumentParser(description="Script for generating HTTP model Parameters (number of main and inline objects, size, reading times, followed by generating Web content including main and inline objects.", epilog="Script expects number of users, runs per user, web pages per run. It will then generate parameters for each user across multiple runs with each run containing multiple web page parameters. Result will be saved to json format. Json file is used for dummy webpages generation.")

parser.add_argument('--save_json', '-p',
					dest="save_json",
					action="store",
					help="Directory where to store parameters",
					required=True)
parser.add_argument('--numClients', '-nc',
					dest="numClients",
					action="store",
					default=1,
					help="Number of Clients"
					)
parser.add_argument('--numRuns',
					dest="numRuns",
					action="store",
					default=1,
					help="Numbr of runs per client")
parser.add_argument('--webPages',
					dest="webPages",
					action="store",
					default=1,
					help="Number of web pages per run")
parser.add_argument('--save_content', '-sp',
					dest="out_path",
					action="store",
					help="Directory where to store files",
					required=True)



if __name__ == "__main__" :
    # Expt parameters
    args = parser.parse_args()
    
    total_num_clients = int(args.numClients)
    total_num_runs = int(args.numRuns)
    total_num_pages = int(args.webPages)
    generated_dict = generateHTTPModelParametersForUsers(total_num_clients, total_num_runs, total_num_pages)
    os.system("mkdir -p %s"%args.save_json)
    with open(os.path.join(args.save_json,"HTTP_fullmodel_C%d_R%d_W%d.json"%(total_num_clients, total_num_runs, total_num_pages)), 'w') as json_file:
        json.dump(generated_dict, json_file, indent=4)
    for client_num in generated_dict:
        with open(os.path.join(args.save_json, "HTTP_%s_R%d_W%d.json"%(client_num, total_num_runs, total_num_pages)), 'w') as json_file:
            json.dump(generated_dict[client_num], json_file, indent=4)
            
    print ("Generating dummy webpages...")
    pathlist = Path(args.save_json).glob('**/*.json')
    for path in pathlist:
     
        path_in_str = str(path)
        generateContentForUser(path_in_str)
