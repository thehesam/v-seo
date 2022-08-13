import requests
import pandas as pd
import time

#config
rootQuery = ['بازی کامپیوتر']
region = 'fa'
lang = 'ir'
loop_depth = 3
alphabet = ['ض','ص','ث','ق','ف','غ','ع','ه','خ','ح','ج','چ','پ','ش','س','ی','ب','ل','ا','ت','ن','م','ک','گ','ظ','ط','ز','ر','ذ','د','و','.',' ','چرا','چطور','چگونه','از کجا','کدام','روش','نحوه','آموزش','چیست']


kwdataframe = pd.DataFrame(columns=['Keywords'])

def apicall(query='', cp=None, hl='fa', gl='ir'):
    url = f"https://www.google.com/complete/search?q={query}&cp={cp}&client=chrome&hl={hl}-{gl}"
    res = requests.get(url=url)
    return res
    
def apicallUrl(url):
    res = requests.get(url=url)
    return res     


#thread options
import concurrent
from concurrent.futures import ThreadPoolExecutor
threads = 20

#main keywords fetch based on depth
query_dict = [{'queries':rootQuery, 'suggests':[], 'depth': 0}]
for i in range(0,loop_depth):
    keywords = query_dict[i]['queries']
    mainList = [] 
    for kw in keywords:
        suggestlist = []
        cp_number = len(kw)
        indices = [key for key, value in enumerate(kw) if value == ' ']
        spaces = [0,cp_number] + indices
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(apicall, kw,item,lang,region) for item in spaces}
            for future in concurrent.futures.as_completed(future_to_url):
                response = future.result()
                try:
                    response = future.result()
                    results = response.json()[1]
                    tdf = pd.DataFrame(results, columns=['Keywords'])
                    kwdataframe = pd.concat([kwdataframe, tdf], ignore_index=True, sort=False)
                    kwdataframe = kwdataframe.drop_duplicates(subset=['Keywords'])
                    kwdataframe.to_csv('final.csv')
                    for res in results:
                        mainList.append(res)

                except Exception as e:
                    if response.status_code != 200:
                        print('error! your ip probably blocked')
                        exit()
                    else:
                        print('Looks like something went wrong:', e)
        #suggest links generate
        urllist = []
        for atoz in alphabet:
            #pre
            suggestQuery = atoz + ' ' + kw
            for tcp in [0,1,2]:
                tempurl = f"https://www.google.com/complete/search?q={suggestQuery}&cp={tcp}&client=chrome&hl={lang}-{region}"
                urllist.append(tempurl)
            #post
            suggestQuery = kw + ' ' + atoz
            for tcp in [len(suggestQuery), len(suggestQuery) - 1]:
                tempurl = f"https://www.google.com/complete/search?q={suggestQuery}&cp={tcp}&client=chrome&hl={lang}-{region}"
                urllist.append(tempurl)
            #mid
            for item in spaces:
                suggestQuery = kw[:item] + ' ' + atoz + ' ' + kw[item:]
                for tcp in [item + 1, item + 2, item + 3]:
                        tempurl = f"https://www.google.com/complete/search?q={suggestQuery}&cp={tcp}&client=chrome&hl={lang}-{region}"
                        urllist.append(tempurl)
        #suggest fetch
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(apicallUrl, urltoget) for urltoget in urllist}
            for future in concurrent.futures.as_completed(future_to_url):
                response = future.result()
                try:
                    results = response.json()[1]
                    tdf = pd.DataFrame(results, columns=['Keywords'])
                    kwdataframe = pd.concat([kwdataframe, tdf], ignore_index=True, sort=False)
                    kwdataframe = kwdataframe.drop_duplicates(subset=['Keywords'])
                    kwdataframe.to_csv('final.csv')
                    for res in results:
                        mainList.append(res)

                except Exception as e:
                     if response.status_code != 200:
                         print('error! your ip probably blocked')
                         exit()
                     else:
                         print('Looks like something went wrong:', e)
        print('sleeping')
        time.sleep(20)
    query_dict[i]['suggests'] = suggestlist
    query_dict.append({'queries':mainList,'depth':i+1})