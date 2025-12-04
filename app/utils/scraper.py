import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_baidu_generator(keyword, pages=1, limit=None):
    """
    Scrape Baidu search results for a given keyword with pagination and progress updates.
    Yields progress status or results.
    
    Args:
        keyword (str): The search keyword.
        pages (int): Number of pages to scrape.
        limit (int): Maximum number of results to collect (optional).
        
    Yields:
        dict: Progress update or final result.
    """
    results = []
    total_collected = 0
    
    for page in range(pages):
        if limit and total_collected >= limit:
            break
            
        # Yield progress
        yield {'type': 'progress', 'current': page + 1, 'total': pages, 'msg': f'正在采集第 {page+1}/{pages} 页...'}
        
        pn = page * 10
        url = f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd={keyword}&pn={pn}"
        
        # Headers provided by user (modified to ensure compatibility)
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9",
            "connection": "keep-alive",
            "cookie": "BIDUPSID=9F5E32DCF4C42649287BD46CE38C9F30; PSTM=1752326629; BAIDUID=9F5E32DCF4C426498C7580C1849BE156:FG=1; BAIDUID_BFESS=9F5E32DCF4C426498C7580C1849BE156:FG=1; H_PS_PSSID=60277_63148_66101_66120_66231_66201_66162_66384_66279_66268_66393_66516_66529_66547_66585_66579_66592_66601_66615_66655_66663_66682_66673_66691_66688_66743_66622_66772_66783_66790_66796_66803_66599; BD_HOME=1; BD_UPN=12314753; BA_HECTOR=a58g250ha1ag040lah84a5000g018i1kj00s925; ZFY=z4FQHye5NlJGyid32ACOK4rPhVR18AEWw50KB5k55kk:C; BD_CK_SAM=1; PSINO=7; delPer=0; COOKIE_SESSION=0_0_1_1_0_1_1_0_1_1_2_0_0_0_0_0_0_0_1764754343%7C1%230_0_1764754343%7C1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_645EC=346a6l%2FxQT95ApPuz3YJfMm0V8u6jvmxmuuVM9nx0Wik2f1rB8jMyn74dAE; H_WISE_SIDS=60277_63148_66101_66120_66231_66201_66162_66384_66279_66268_66393_66516_66529_66547_66585_66579_66592_66601_66615_66655_66663_66682_66673_66691_66688_66743_66622_66772_66783_66790_66796_66803_66599; channel=google; baikeVisitId=552613c1-1b43-4940-ab9f-d735ccb9b502",
            "host": "www.baidu.com",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            try:
                soup = BeautifulSoup(response.text, 'lxml')
            except:
                soup = BeautifulSoup(response.text, 'html.parser')
                
            # Baidu results are typically in div containers with class 'result c-container' or similar
            containers = soup.find_all('div', class_=lambda x: x and 'result' in x and 'c-container' in x)
            
            if not containers:
                 containers = soup.find_all('div', class_='result')
                 
            page_results = []
            for container in containers:
                try:
                    item = {}
                    
                    # 1. Title
                    title_tag = container.find('h3')
                    if title_tag:
                        item['title'] = title_tag.get_text(strip=True)
                        link_tag = title_tag.find('a')
                        if link_tag:
                            item['url'] = link_tag.get('href')
                        else:
                            item['url'] = ''
                    else:
                        continue # Skip if no title
                    
                    # 2. Summary (Abstract) - REMOVED for optimization
                    item['summary'] = ''

                    # 3. Cover (Image)
                    img_tag = container.find('img')
                    if img_tag and img_tag.get('src'):
                         item['cover'] = img_tag.get('src')
                    else:
                         item['cover'] = ''

                    # 4. Source
                    source_tag = container.find(class_=lambda x: x and ('c-showurl' in x or 'c-source' in x))
                    if source_tag:
                        item['source'] = source_tag.get_text(strip=True)
                    else:
                        user_source = container.find(class_='c-gap-right')
                        if user_source:
                             item['source'] = user_source.get_text(strip=True)
                        else:
                             item['source'] = 'Baidu Search'

                    # 5. Original URL
                    if item['url'].startswith('/'):
                         item['url'] = "https://www.baidu.com" + item['url']
                         item['original_url'] = item['url']
                    else:
                         item['original_url'] = resolve_baidu_link(item['url'])
                    
                    page_results.append(item)
                    
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
            
            if not page_results:
                # No more results or blocked
                break
                
            results.extend(page_results)
            total_collected += len(page_results)
            
            # Sleep to avoid block
            if page < pages - 1:
                time.sleep(random.uniform(1, 2))
                
        except Exception as e:
            print(f"Error scraping Baidu page {page}: {e}")
            yield {'type': 'error', 'msg': str(e)}
            break
            
    if limit:
        results = results[:limit]
        
    yield {'type': 'result', 'data': results}

# Keep the original function for backward compatibility if needed, or redirect it
def scrape_baidu(keyword):
    """Legacy wrapper."""
    gen = scrape_baidu_generator(keyword, pages=1)
    final_data = []
    for item in gen:
        if item['type'] == 'result':
            final_data = item['data']
    return final_data

def resolve_baidu_link(baidu_url):
    """
    Resolves the actual URL from a Baidu redirect link.
    """
    if not baidu_url:
        return ""
    try:
        headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }
        try:
            r = requests.head(baidu_url, headers=headers, allow_redirects=True, timeout=3)
            return r.url
        except:
            r = requests.get(baidu_url, headers=headers, allow_redirects=True, timeout=5, stream=True)
            return r.url
    except:
        return baidu_url

def scrape_content(url):
    """
    Deep crawl the content of a given URL.
    """
    if not url:
        return ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        response.encoding = response.apparent_encoding
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
        except:
            soup = BeautifulSoup(response.text, 'html.parser')
            
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator='\n')
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"Error deep scraping {url}: {e}")
        return ""

if __name__ == "__main__":
    keyword = "宜宾"
    print(f"Scraping for keyword: {keyword}...")
    gen = scrape_baidu_generator(keyword, pages=2)
    for item in gen:
        if item['type'] == 'progress':
            print(item['msg'])
        elif item['type'] == 'result':
            print(f"Found {len(item['data'])} results.")
