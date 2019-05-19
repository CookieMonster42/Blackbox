#MB_KEY="ODY0OTQ5MjAxNTUxNzUzNGFhNzRkMDY1NWFlNmEyMmU.1zSylQ1SMpFxIydMd_pGl2yaHPIRL9swFa_pS8yl1EZG5NkYWQYy-t_ciT9Ace3w4mTETU3Re9BBQav17jsXKQ"
#docker run -p 8080:8080 -e "MB_KEY=ODY0OTQ5MjAxNTUxNzUzNGFhNzRkMDY1NWFlNmEyMmU.1zSylQ1SMpFxIydMd_pGl2yaHPIRL9swFa_pS8yl1EZG5NkYWQYy-t_ciT9Ace3w4mTETU3Re9BBQav17jsXKQ" machinebox/fakebox
import requests
import re
import math

def getPageContent(url):
    url = "http://boilerpipe-web.appspot.com/extract?url=" + url + "&output=json"

    respones = requests.get(url)

    return respones.json()['response']['title'],respones.json()['response']['content']

def log_fun(z):
    # return (1/(1+math.pow(math.e, (z))))
    return (1/(1+math.pow(math.e, -2.6*z))-0.5)*2

def urlify(s):

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '+', s)

    return s

def getPageContent(url):
    # url = "http://boilerpipe-web.appspot.com/extract?url=" + url + "&output=json"

    # respones = requests.get(url)

    # print(respones.json())
    # return respones.json()['response']['title'],respones.json()['response']['content']
    headers = { 
        'X-AYLIEN-TextAPI-Application-Key': 'aeb283d37ce140cf4325c01867e94591',
        'X-AYLIEN-TextAPI-Application-ID': "017a3076",
    } 
    data = {
        'bestimage': False,
        'url': url
    }
    response = requests.post('https://api.aylien.com/api/v1/extract', data=data, headers=headers)

    print(response.status_code)
    print(response.json())

    return response.json()['title'], response.json()['article']

def fnews_detector(url=None, title=None, content=None):

    if url:
        # url = "https://api.fakenewsdetector.org/votes?url=" + url + "&title=" + urlify(title)
        url = "https://api.fakenewsdetector.org/votes?url=" + url + "&title=" + urlify(title)
    else:
        url = "https://api.fakenewsdetector.org/votes_by_content?content=" + content

    headers = {'Content-type': 'application/json'}
    response = requests.get(url, headers=headers) 
    print(response.status_code)

    if response.status_code >= 500:
        print('[!] [{0}] Server Error'.format(response.status_code))
        return None
    elif response.status_code == 404:
        print('[!] [{0}] URL not found: [{1}]'.format(response.status_code,url))
        return None  
    elif response.status_code == 401:
        print('[!] [{0}] Authentication Failed'.format(response.status_code))
        return None
    elif response.status_code == 400:
        print('[!] [{0}] Bad Request'.format(response.status_code))
        return None
    elif response.status_code >= 300:
        print('[!] [{0}] Unexpected Redirect'.format(response.status_code))
        return None
    elif response.status_code == 200:
        return response.json()
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
    return None


def fakebox(url=None, title=None, content=None):
    json={}
    if url:
        json['url'] = url
    if title:
        json['title'] = title
    if content:
        json['content'] = content

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    response = requests.post('http://localhost:8080/fakebox/check', json=json, headers=headers) 

    if response.status_code >= 500:
        print('[!] [{0}] Server Error'.format(response.status_code))
        return None
    elif response.status_code == 404:
        print('[!] [{0}] URL not found: [{1}]'.format(response.status_code,url))
        return None  
    elif response.status_code == 401:
        print('[!] [{0}] Authentication Failed'.format(response.status_code))
        return None
    elif response.status_code == 400:
        print('[!] [{0}] Bad Request'.format(response.status_code))
        return None
    elif response.status_code >= 300:
        print('[!] [{0}] Unexpected Redirect'.format(response.status_code))
        return None
    elif response.status_code == 200:
        return response.json()
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
    return None
    
def eval_fn_detector_json(json):
    api_json = {}
    api_json['name'] = "fakenewsdetector.org"

    print("json: ", json)
    scores = list(json['robot'].values())
    
    score = 1 - log_fun(sum(scores) + scores[0])
    score = int(score * 100)


    api_json['score'] = score
    

    keywords = json['keywords']

    msg = ""
    print(keywords)

    if len(keywords) > 0:
        msg += "- keywords: "

    for index, keyword in enumerate(keywords):
        if index > 0:
            msg += ", "
        msg += keyword

        if index == len(keywords) - 1:
            msg += "\n"

    if json['domain']:
        domain = json['domain']
        msg += "\n- is in category " + domain['category'].upper()

    print(msg)
    api_json['info'] = msg

    return score, api_json

def eval_fakebox_json(json):
    api_json = {}
    api_json['name'] = "Fakebox"
    if json['success'] == False:
        api_json['score'] = -1
        api_json['info'] = "Failure!"
        return -1, api_json
    
    score = 1 - json['title']['score']
    score = int(score * 100)


    api_json['score'] = score
    

    keywords = list(json['content']['keywords'])

    msg = ""
    print(keywords)

    if len(keywords) > 0:
        msg += "- keywords: "

    for index, keyword in enumerate(keywords):
        if index > 0:
            msg += ", "
        msg += keyword['keyword']

        if index == len(keywords) - 1:
            msg += "\n"

    if 'domain' in json:
        domain = json['domain']
        msg += "\n- " + domain['domain']
        msg += " is in category " + domain['category'].upper()

    print(msg)
    api_json['info'] = msg

    return score, api_json

def evaluate_style(rID, text, url):
    score = -1
    count = 0
    style_json = {}
    style_json['apis'] = []
    title, content = "", ""
    
    if url:
        title, content = getPageContent(url)
    
        text=None


    #### Fakebox ####
    fakebox_eval = None
    if text:
        fakebox_eval = fakebox(content=text)
    else:
        fakebox_eval = fakebox(url=url, title=title, content=content)

    
    print(fakebox_eval)

    if fakebox_eval:
        box_score, api_json = eval_fakebox_json(fakebox_eval)

        if box_score != -1:
            score = box_score
            count += 1

        style_json['apis'].append(api_json)

    style_json['score'] = score

    return score, style_json
    


    #### fakenewsdetector.org ####
    fndetector_eval = None
    if text:
        fndetector_eval = fnews_detector(content=text)
    else:
        fndetector_eval = fnews_detector(url=url, title=title, content=content)

    print(fndetector_eval)

    if fakebox_eval:
        detector_score, api_json = eval_fn_detector_json(fndetector_eval)

        if count == 0:
            score = detector_score
            count += 1
        else:
            score += detector_score
            count += 1

        style_json['apis'].append(api_json)

    score //= count
    style_json['score'] = score

    return style_json
    




# class StyleChecker():
#     def __init__(self, url=None, content=None, title=None):
#         if content is None and url is not None:
#             self.title, self.content = self.getPageContent(url)
#         else:
#             self.

#     def getPageContent():
#         pass

answer = {'success': True, 'title': {'decision': 'impartial', 'score': 0.8350648283958435, 'entities': [{'text': 'Five Years', 'start': 0, 'end': 9, 'type': 'date'}, {'text': 'The Twilight Zone', 'start': 71, 'end': 87, 'type': 'organization'}]}, 'content': {'decision': 'bias',
'score': 0.2320660501718521, 'entities': [{'text': 'weekly', 'start': 8, 'end': 13, 'type': 'date'}, {'text': 'Asian', 'start': 60, 'end': 64, 'type': 'group'}, {'text': 'SAT', 'start': 89, 'end': 91, 'type': 'organization'}, {'text': '1926', 'start': 113, 'end': 116, 'type': 'date'}, {'text': 'this week', 'start': 266, 'end': 274, 'type': 'date'}, {'text': 'SAT', 'start': 337, 'end': 339, 'type': 'organization'}, {'text': 'Asian', 'start': 564, 'end': 568, 'type': 'group'}, {'text': 'SAT', 'start': 622, 'end': 624, 'type': 'organization'}, {'text': '1223', 'start': 635, 'end': 638, 'type': 'date'}, {'text': 'Asians', 'start': 641, 'end': 646, 'type': 'group'}, {'text': 'SAT', 'start': 713, 'end': 715, 'type': 'organization'}, {'text': 'Asian', 'start': 748, 'end': 752, 'type': 'group'}], 'keywords': [{'keyword': 'asian test taker'}, {'keyword': 'average sat score'}, {'keyword': 'low income household'}, {'keyword': 'poor high school'}, {'keyword': 'new sat scoring'}, {'keyword': 'university entrance exam'}, {'keyword': 'high crime neighborhood'}, {'keyword': 'poor test result'}, {'keyword': 'weekly absurdity begin'}, {'keyword': 'high school'}]}, 'domain': {'domain': 'activistpost.com', 'category': 'conspiracy'}}

if __name__ == "__main__":
    score, json = evaluate_style(0, None,"https://www.activistpost.com/2019/05/five-years-in-prison-for-offending-someone-online-and-other-news-from-the-twilight-zone.html")
    
    print(score)
    print(json)

# curl -XPOST -H "Content-Type: application/json" -d '{"title":"Article title goes here","content":"The article content goes here","url":"http://www.bbc.co.uk/news/uk-39657382"}' "http://localhost:8080/fakebox/check

if __name__ == "__main__":
    json = evaluate_style(0, None,"https://www.activistpost.com/2019/05/five-years-in-prison-for-offending-someone-online-and-other-news-from-the-twilight-zone.html")
    
    print(json)
    

    # title = "Five Years in Prison for Offending Someone Online (And Other News From The Twilight Zone)"
    # url = "https://www.activistpost.com/2019/05/five-years-in-prison-for-offending-someone-online-and-other-news-from-the-twilight-zone.html"
    # url = "https://api.fakenewsdetector.org/votes?url=" + url + "&title=" + urlify(title)

    # print("\n" + url + "\n")
    # headers = {'Content-type': 'application/json'}
    # r = requests.get(url, headers=headers)

    # print(r.status_code)
    # print(r.json())
    # json = r.json()
    # print(list(json['robot']))
    # values = list(json['robot'].values())
    # print(values)
    # print(log_fun(sum(values)+values[0]))
    # print(log_fun(0.5))
    # print(log_fun(1))
    # print(log_fun(0))
    # print(log_fun(2))

    # {'key1': 'test', 'key2': 'test2'}.values()

    # for key in list(json['robot']):
    #     print(json['robot'][key])

    # url = "https://api.fakenewsdetector.org/votes_by_content?content=" + "Trump is just such a dump person, it hurts!"
    # r = requests.get(url, headers=headers)

    # print(r.status_code)
    # print(r.json())

    # title = "Trojan Name New Ultra-Thin Skin Condom after Donald Trump"
    # url = "http://nationalreport.net/trojan-name-new-ultra-thin-skin-condom-donald-trump/"
    # url = "https://api.fakenewsdetector.org/votes?url=" + url + "&title=" + title
    # r = requests.get(url, headers=headers)

    # print(r.status_code)
    # print(r.json())

# curl -XPOST -H "Content-Type: application/json" -d '{"title":"Article title goes here","content":"The article content goes here","url":"http://www.bbc.co.uk/news/uk-39657382"}' "http://localhost:8080/fakebox/check"

#"https://www.activistpost.com/2019/05/five-years-in-prison-for-offending-someone-online-and-other-news-from-the-twilight-zone.html"
#"http://nationalreport.net/trojan-name-new-ultra-thin-skin-condom-donald-trump/"

# curl https://api.aylien.com/api/v1/extract \
#    -H "X-AYLIEN-TextAPI-Application-Key: aeb283d37ce140cf4325c01867e94591" \
#    -H "X-AYLIEN-TextAPI-Application-ID: 017a3076" \
#    -d best_image=true \
#    -d url="http://techcrunch.com/2015/04/06/john-oliver-just-changed-the-surveillance-reform-debate"
