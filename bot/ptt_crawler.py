import json
import os
import re

import requests
from bs4 import BeautifulSoup


class PttCrawler(object):

    def __init__(self, history_list, board_name, keywords):
        self.history_list = history_list
        self.board_name = board_name
        self.keywords = keywords

    def crawling(self, page=1):

        id_regex = re.compile(r'.*\/\w+\/M\.(\S+)\.html')
        request = requests.session()
        res = request.post(url="https://www.ptt.cc/ask/over18",
                           data={'from': f"/bbs/{self.board_name}/index.html", 'yes': "yes"})
        res = request.get(url=f"https://www.ptt.cc/bbs/{self.board_name}/index.html")
        soup = BeautifulSoup(res.text, "html.parser")

        new_articles = list()

        for _ in range(page):

            next_page = soup.select('.btn-group-paging .wide')[1].get('href')
            articles = soup.select('.r-list-container .r-ent .title a')

            for article in articles:
                # Article title.
                title = str(article.string)

                if any([keyword in title for keyword in self.keywords]):
                    # Article link & id.
                    link = f"https://www.ptt.cc{article.get('href')}"
                    article_id = id_regex.match(link).group(1)

                    if article_id not in self.history_list:
                        # Get article content.
                        res = request.get(link)
                        soup = BeautifulSoup(res.text, "html.parser")
                        author = soup.select('.article-meta-value')[0].string
                        date = soup.select('.article-meta-value')[3].string

                        # Get article main content.
                        main_content = soup.find(id='main-content')
                        filtered = list()
                        for sub_string in main_content.stripped_strings:
                            if "發信站" in sub_string or "Sent from" in sub_string:
                                break
                            if not(sub_string[0] == "※" or sub_string[0] == ":"):
                                if "http" in sub_string:
                                    sub_string = f" {sub_string} "
                                filtered.append(sub_string.replace('\n', ''))
                        main_content = ''.join(filtered[8:])

                        if len(main_content) > 70:
                            main_content = f"{main_content[:70]}..."

                        content = {
                            'id': article_id,
                            'board': self.board_name,
                            'title': title,
                            'link': link,
                            'author': author,
                            'date': date,
                            'content': main_content
                        }

                        new_articles.append(content)
                        print(f"{date}: New Article: {title} {link}")

            # Crawl next page.
            res = request.get(f"https://www.ptt.cc{next_page}", verify=False)
            soup = BeautifulSoup(res.text, "html.parser")

        return new_articles[::-1]
