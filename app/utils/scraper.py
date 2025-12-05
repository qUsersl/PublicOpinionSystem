import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import json
import re
from lxml import html as lxml_html

def is_valid_item(item):
    """
    Check if the item is valid based on user criteria.
    Invalid if 3 or more fields are missing/invalid.
    """
    invalid_count = 0
    
    # 1. Original URL
    url = item.get('original_url', '')
    if not url or not url.strip():
        invalid_count += 1
        
    # 2. Cover
    cover = item.get('cover', '')
    if not cover or not cover.strip():
        invalid_count += 1
        
    # 3. Source
    source = item.get('source', '')
    if not source or '未知来源' in source or not source.strip():
        invalid_count += 1
        
    # 4. Title
    title = item.get('title', '')
    if not title or '无标题' in title or not title.strip():
        invalid_count += 1
        
    # 5. Summary
    summary = item.get('summary', '')
    if not summary or not summary.strip():
        invalid_count += 1
        
    # Filter if 3 or more are invalid
    if invalid_count >= 3:
        return False
    return True


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
        url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={keyword}&pn={pn}"
        
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
                    
                    if is_valid_item(item):
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

def scrape_sohu_generator(keyword, pages=1, limit=None):
    """
    Scrape Sohu content via Sogou Search (proxy) for a given keyword.
    Yields progress status or results.
    """
    results = []
    total_collected = 0
    
    for page in range(pages):
        if limit and total_collected >= limit:
            break
            
        yield {'type': 'progress', 'current': page + 1, 'total': pages, 'msg': f'正在采集搜狐数据(第 {page+1}/{pages} 页)...'}
        
        # Sogou pagination uses 'page' parameter
        url = f"https://www.sohu.com/web?query=site:sohu.com+{keyword}&page={page+1}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": "SUV=1; sct=1;" 
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                 yield {'type': 'error', 'msg': f'Sogou returned status {response.status_code}'}
                 break

            try:
                soup = BeautifulSoup(response.text, 'lxml')
            except:
                soup = BeautifulSoup(response.text, 'html.parser')
                
            # Results usually in .vrwrap or .rb
            containers = soup.find_all(class_='vrwrap')
            if not containers:
                containers = soup.find_all(class_='rb')
                
            page_results = []
            for container in containers:
                try:
                    item = {}
                    
                    # Title
                    h3 = container.find('h3')
                    if not h3:
                        continue
                    item['title'] = h3.get_text(strip=True)
                    
                    # Link
                    a = h3.find('a')
                    if a:
                        item['url'] = a.get('href')
                        if item['url'].startswith('/'):
                             item['url'] = "https://www.sogou.com" + item['url']
                    else:
                        continue
                        
                    # Summary
                    st_div = container.find(class_='st')
                    if not st_div:
                        st_div = container.find(class_='text-layout')
                        
                    if st_div:
                        item['summary'] = st_div.get_text(strip=True)
                    else:
                         item['summary'] = ''

                    # Cover
                    img = container.find('img')
                    if img and img.get('src'):
                         item['cover'] = img.get('src')
                         if item['cover'].startswith('//'):
                             item['cover'] = 'https:' + item['cover']
                    else:
                         item['cover'] = ''
                         
                    # Source / Date
                    fb = container.find(class_='fb')
                    if fb:
                        item['source'] = fb.get_text(strip=True)
                    else:
                        item['source'] = '搜狐新闻'
                        
                    # Resolve original URL
                    # Reuse resolve_baidu_link as it is generic enough for redirects
                    if 'sogou.com/link' in item['url']:
                         item['original_url'] = resolve_baidu_link(item['url'])
                    else:
                         item['original_url'] = item['url']
                         
                    if is_valid_item(item):
                        page_results.append(item)
                    
                except Exception as e:
                    continue
            
            if not page_results:
                break
                
            results.extend(page_results)
            total_collected += len(page_results)
            
            if page < pages - 1:
                time.sleep(random.uniform(1, 2))
                
        except Exception as e:
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
    Deep crawl the content of a given URL with improved noise filtering and formatting.
    """
    if not url:
        return ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Detect encoding
        response.encoding = response.apparent_encoding
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
        except:
            soup = BeautifulSoup(response.text, 'html.parser')
            
        # 1. Remove standard junk tags
        for element in soup(["script", "style", "iframe", "noscript", "header", "footer", "aside", "nav", "form", "svg", "button", "input", "select", "textarea"]):
            element.extract()

        # 2. Remove junk by class/id heuristics
        # Keywords often used in non-content areas
        junk_keywords = ['comment', 'sidebar', 'related', 'recommend', 'ad-', 'ads', 'menu', 'copyright', 'disclaimer', 'share', 'login', 'register', 'search', 'footer', 'header', 'nav']
        
        def is_junk(attr_value):
            if not attr_value:
                return False
            if isinstance(attr_value, list):
                attr_value = " ".join(attr_value)
            return any(keyword in attr_value.lower() for keyword in junk_keywords)

        # Remove elements with junk classes
        for element in soup.find_all(attrs={"class": True}):
             if is_junk(element.get("class")):
                 element.extract()
                 
        # Remove elements with junk ids
        for element in soup.find_all(attrs={"id": True}):
             if is_junk(element.get("id")):
                 element.extract()

        # 3. Try to find the main content area
        # Heuristic: The container with the most text length
        # We prioritize 'article' tag or divs with 'content'/'main' in class
        
        main_content = None
        
        # Priority 1: <article> tag
        article = soup.find('article')
        if article:
            main_content = article
        
        # Priority 2: div with specific class names
        if not main_content:
            candidates = soup.find_all('div', class_=re.compile(r'(content|article|main|post|detail|news_txt)', re.I))
            if candidates:
                # Filter out small candidates
                valid_candidates = [c for c in candidates if len(c.get_text(strip=True)) > 100]
                if valid_candidates:
                    main_content = max(valid_candidates, key=lambda x: len(x.get_text(strip=True)))
        
        # Fallback: Use body
        if not main_content:
            main_content = soup.body or soup

        # 4. Extract text with better spacing
        # Use separator='\n\n' to preserve paragraph structure
        text = main_content.get_text(separator='\n\n')
        
        # 5. Clean up whitespace
        # Split by lines, strip each line
        lines = [line.strip() for line in text.splitlines()]
        
        # Remove empty lines but keep paragraph structure
        # We allow max 1 consecutive empty line, or just join non-empty lines with \n\n
        clean_lines = [line for line in lines if line]
        
        # Join with double newline to clearly separate paragraphs in plain text
        text = '\n\n'.join(clean_lines)
        
        return text
    except Exception as e:
        print(f"Error deep scraping {url}: {e}")
        return ""


def get_smart_xpath(element):
    """
    Generate a smart XPath for an element (ID > Class > Absolute).
    """
    # If element has id, use it
    if element.get('id'):
        return f"//*[@id='{element.get('id')}']"
    
    # If element has class, use it
    cls = element.get('class')
    if cls:
        classes = cls.split()
        if classes:
             c = classes[0] # Pick first class
             return f"//{element.tag}[contains(@class, '{c}')]"
    
    # Fallback to absolute path
    tree = element.getroottree()
    try:
        return tree.getpath(element)
    except:
        return ""

import re

def resolve_sogou_link(url):
    """
    Resolves Sogou intermediate link to actual URL via JS/Meta parsing.
    """
    if 'sogou.com/link' not in url:
        return url
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": "SUV=1; sct=1;",
        "Referer": "https://www.sogou.com/"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Check for window.location.replace
        match = re.search(r'window\.location\.replace\("([^"]+)"\)', r.text)
        if match:
            return match.group(1)
            
        # Check for meta refresh
        match = re.search(r'URL=\'([^\']+)\'', r.text)
        if match:
            return match.group(1)
            
        return url
    except:
        return url

def deep_crawl_content(url, rule_config=None):
    """
    Deep crawl content using specific rules (XPath).
    If rule_config is provided, it uses it.
    If parsing fails with provided rule, it tries to auto-discover and returns updated rule.
    
    Args:
        url (str): URL to crawl.
        rule_config (dict): {'title_xpath': str, 'content_xpath': str, 'headers': str/dict}
        
    Returns:
        tuple: (title, content, new_rule_config)
        new_rule_config is None if no update needed.
    """
    if not url:
        return "", "", None

    # Pre-resolve Sogou links
    if 'sogou.com/link' in url:
        url = resolve_sogou_link(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Merge headers from rule
    if rule_config and rule_config.get('headers'):
        try:
            if isinstance(rule_config['headers'], str):
                custom_headers = json.loads(rule_config['headers'])
            else:
                custom_headers = rule_config['headers']
            if custom_headers:
                headers.update(custom_headers)
        except:
            pass

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Handle encoding
        if response.encoding == 'ISO-8859-1':
             response.encoding = response.apparent_encoding
             
        html_content = response.text
        try:
            tree = lxml_html.fromstring(html_content)
        except:
            # Fallback if lxml fails to parse broken HTML
            return "", "", None
        
        title = ""
        content = ""
        new_rule_config = None
        rule_updated = False
        
        # 1. Try using provided rule
        if rule_config:
            title_xpath = rule_config.get('title_xpath')
            content_xpath = rule_config.get('content_xpath')
            
            if title_xpath:
                try:
                    titles = tree.xpath(title_xpath)
                    if titles:
                        title = titles[0].text_content().strip() if hasattr(titles[0], 'text_content') else str(titles[0]).strip()
                except:
                    pass
            
            if content_xpath:
                try:
                    contents = tree.xpath(content_xpath)
                    if contents:
                        # Join multiple content parts if xpath returns multiple elements
                        content = "\n".join([c.text_content().strip() for c in contents if hasattr(c, 'text_content')])
                except:
                    pass
        
        # 2. If failed (empty title or content), try fallback and update rule
        # We only try to update rule if we had a rule to begin with, or if we want to discover new rules?
        # The prompt says "If you discover rule changes... update". Implies existing rule failed.
        
        if not title or not content:
            # Fallback Title
            if not title:
                possible_titles = tree.xpath('//meta[@property="og:title"]/@content | //title/text() | //h1/text()')
                if possible_titles:
                    title = possible_titles[0].strip()
                    # We don't update title xpath easily as generic ones are fine usually.

            # Fallback Content
            if not content:
                # Simple heuristic: Find the block element (div, article) with the most text
                candidates = tree.xpath('//article | //div[count(p)>3] | //div[string-length(.)>500]')
                best_candidate = None
                max_length = 0
                
                for candidate in candidates:
                    # Remove scripts and styles
                    for bad in candidate.xpath('.//script | .//style'):
                        bad.drop_tree()
                    
                    text = candidate.text_content().strip()
                    if len(text) > max_length:
                        max_length = len(text)
                        best_candidate = candidate
                
                if best_candidate is not None:
                    content = best_candidate.text_content().strip()
                    
                    # AUTOMATIC UPDATE LOGIC
                    if rule_config:
                        # Generate XPath for the best candidate
                        try:
                            new_xpath = get_smart_xpath(best_candidate)
                            if new_xpath:
                                if not new_rule_config:
                                    new_rule_config = rule_config.copy()
                                new_rule_config['content_xpath'] = new_xpath
                                rule_updated = True
                        except:
                            pass

        return title, content, new_rule_config if rule_updated else None

    except Exception as e:
        print(f"Error in deep_crawl_content: {e}")
        return "", "", None


