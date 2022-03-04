import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Article:
    id: str
    board: str
    title: str
    link: str
    author: str
    date: str
    content: str


class PttCrawler:

    domain = "https://www.ptt.cc"
    article_id_regex = re.compile(r'.*\/\w+\/M\.(\S+)\.html')

    def __init__(self, board_name: str, keywords: list, ignore_list: list = None):
        self.board_name = board_name
        self.keywords = keywords
        self.ignore_list = ignore_list or []

    def crawling(self, pages: int = 1):
        req = requests.session()
        over_18 = req.request(
            method="POST",
            url=urljoin(self.domain, "ask/over18"),
            data={
                'from': f"/bbs/{self.board_name}/index.html",
                'yes': "yes"
            }
        )
        next_page = f"bbs/{self.board_name}/index.html"

        for page in range(pages):
            article_list = req.request(
                method="GET",
                url=urljoin(self.domain, next_page),
                verify=False
            )
            soup = BeautifulSoup(article_list.text, "html.parser")
            next_page = soup.select('.btn-group-paging .wide')[1].get('href')
            articles = soup.select('.r-list-container .r-ent .title a')
            for article in articles:
                title = article.string
                link = urljoin(self.domain, article.get('href'))
                article_id = self.article_id_regex.match(link).group(1)

                if article_id in self.ignore_list or not any([keyword in title for keyword in self.keywords]):
                    continue

                article = req.request(method="GET", url=link)
                soup = BeautifulSoup(article.text, "html.parser")
                content = soup.find(id='main-content')

                filtered = []
                for sub_string in content.stripped_strings:
                    if "發信站" in sub_string or "Sent from" in sub_string:
                        break
                    if not (sub_string[0] == "※" or sub_string[0] == ":"):
                        if "http" in sub_string:
                            sub_string = f" {sub_string} "
                        filtered.append(sub_string.replace('\n', ''))
                content = "".join(filtered[8:])
                if len(content) > 100:
                    content = f"{content[:100]}..."

                yield Article(
                    id=article_id,
                    board=self.board_name,
                    title=title,
                    link=link,
                    author=soup.select('.article-meta-value')[0].string,
                    date=soup.select('.article-meta-value')[3].string,
                    content=content
                )
