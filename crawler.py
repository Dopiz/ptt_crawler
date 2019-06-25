import json
import re

import requests
import urllib3
from bs4 import BeautifulSoup


class PttCrawler(object):

    def __init__(self):
        self.history_list = list()
        self.re_id = re.compile(r'.*\/\w+\/M\.(\S+)\.html')

    def load_history(self, board_name):
        with open(f'history/{board_name}.json', 'r+') as f:
            self.history_list = json.load(f)

    def save_history(self, board_name, new_articles):
        self.history_list = new_articles + self.history_list
        with open(f'history/{board_name}.json', 'r+') as f:
            json.dump(self.history_list, f)

    def crawling(self, board_name, keywords, page=1):

        self.load_history(board_name)

        request = requests.session()
        rs = request.post(
            'https://www.ptt.cc/ask/over18', verify=False,
            data={'from': f"/bbs/{board_name}/index.html", 'yes': "yes"})
        rs = request.get(
            f"https://www.ptt.cc/bbs/{board_name}/index.html", verify=False)
        soup = BeautifulSoup(rs.text, "html.parser")

        new_articles = list()

        for _ in range(page):
            next_page = soup.select('.btn-group-paging .wide')[1].get('href')
            for article in soup.select('.r-list-container .r-ent .title a'):
                # Article title.
                title = str(article.string)
                if any([keyword in title for keyword in keywords]):
                    # Article link & id.
                    link = 'https://www.ptt.cc' + article.get('href')
                    article_id = self.re_id.match(link).group(1)
                    if article_id not in self.history_list:
                        # Get article content.
                        rs = request.get(link)
                        soup = BeautifulSoup(rs.text, "html.parser")
                        author = soup.select('.article-meta-value')[0].string
                        date = soup.select('.article-meta-value')[3].string
                        # Get article main content.
                        main_content = soup.find(id='main-content')
                        filtered = list()
                        for v in main_content.stripped_strings:
                            if v == '--' or v[0:4] == u'※ 發信站':
                                break
                            filtered.append(v.replace('\n', ''))
                        main_content = ''.join(filtered[8:])
                        main_content.replace('html', 'html ')
                        if len(main_content) > 70:
                            main_content = main_content[:70] + '...'

                        content = {'board': board_name, 'title': title, 'link': link, 'author': author,
                                   'date': date, 'content': main_content, 'id': article_id}

                        new_articles.append(content)
                        print(f'{date}: New Article: {title} {link}')

            # Crawl next page.
            rs = request.get('https://www.ptt.cc' + next_page, verify=False)
            soup = BeautifulSoup(rs.text, "html.parser")

        return new_articles[::-1]
