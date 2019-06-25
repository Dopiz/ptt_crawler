import json
import re
import threading

import requests
import slack
import urllib3
from bs4 import BeautifulSoup
from flask import Flask
from linebot import LineBotApi
from linebot.models import (BoxComponent, BubbleContainer, ButtonComponent,
                            CarouselContainer, FlexSendMessage, ImageComponent,
                            MessageAction, SeparatorComponent, SpacerComponent,
                            TextComponent, URIAction)

from crawler import PttCrawler
from gsc import GoogleSheetClient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
sheet_name = "Testing"


class SlackBot(object):

    def __init__(self, token):
        self.slack_bot_api = slack.WebClient(token)

    def notify(self, channels, article):

        content = f"{article['title']}\n{article['link']}"

        for channel in channels:
            self.slack_bot_api.chat_postMessage(
                channel=channel, text=content)


class LineBot(object):

    def __init__(self, token):
        self.line_bot_api = LineBotApi(token)

    def flex_message_builder(self, articles):

        contents = list()

        for article in articles:
            # Line Flex Message
            bubble = BubbleContainer(direction='ltr',
                                     header=BoxComponent(
                                         layout='vertical',
                                         contents=[
                                             TextComponent(text="➤ 批踢踢評論來囉！",
                                                           weight='bold', size='md', color='#E00512')
                                         ]
                                     ),
                                     hero=ImageComponent(
                                         url='https://d.rimg.com.tw/s2/b/65/c8/21842830853576_926_m.png',
                                         size='full',
                                         aspect_ratio='5:3',
                                         aspect_mode='cover'
                                     ),
                                     body=BoxComponent(
                                         layout='vertical',
                                         contents=[
                                             TextComponent(
                                                 text=article['title'], wrap=True, weight='bold', size='lg'),
                                             BoxComponent(
                                                 layout='vertical',
                                                 margin='lg',
                                                 spacing='sm',
                                                 contents=[
                                                     BoxComponent(layout='baseline', spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text='Board', color='#aaaaaa', size='sm', flex=1),
                                                                      TextComponent(
                                                                          text=article['board'], wrap=True, color='#666666', size='sm', flex=0)
                                                                  ],
                                                                  ),
                                                     BoxComponent(layout='baseline', spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text='Author', color='#aaaaaa', size='sm', flex=1),
                                                                      TextComponent(
                                                                          text=article['author'], wrap=False, color='#666666', size='sm', flex=0),
                                                                  ],
                                                                  ),
                                                     BoxComponent(layout='baseline', spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text='Date', color='#aaaaaa', size='sm', flex=1),
                                                                      TextComponent(
                                                                          text=article['date'], wrap=True, color='#666666', size='sm', flex=0),
                                                                  ],
                                                                  ),
                                                     SeparatorComponent(),
                                                     BoxComponent(layout='baseline', spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text=article['content'], wrap=True, color='#666666', size='sm', flex=1),
                                                                  ],
                                                                  ),
                                                 ],
                                             )
                                         ],
                                     ),
                                     footer=BoxComponent(
                                         layout='vertical',
                                         spacing='sm',
                                         contents=[
                                             SpacerComponent(size='sm'),
                                             ButtonComponent(
                                                 style='primary',
                                                 height='sm',
                                                 action=MessageAction(
                                                     label='罵個幹！', text='幹！'),
                                             ),
                                             # SeparatorComponent(),
                                             ButtonComponent(
                                                 style='secondary',
                                                 height='sm',
                                                 action=URIAction(
                                                     label='來去看一下～', uri=article['link'])
                                             )
                                         ]
                                     ),
                                     )
            contents.append(bubble)

        return contents

    def notify(self, channels, articles):

        for idx in range(0, len(articles), 10):
            contents = self.flex_message_builder(articles[idx:idx + 10])

            message = FlexSendMessage(
                alt_text="➤ 批踢踢評論來囉！", contents=CarouselContainer(contents=contents))

            for channel in channels:
                self.line_bot_api.push_message(to=channel, messages=message)


class Bot:

    def __init__(self):
        self.gsc = GoogleSheetClient()
        self.history_list = list()

    def notify(self, articles):
        token = self.gsc.load_token()
        line_bot = LineBot(token['line_token'])
        slack_bot = SlackBot(token['slack_token'])
        line_channels, slack_channels = self.gsc.load_notify_list(sheet_name)
        new_articles = list()

        line_bot.notify(line_channels, articles)

        for article in articles:
            try:
                slack_bot.notify(slack_channels, article)
                new_articles.insert(0, article['id'])
            except Exception as e:
                print(f"Slack notify error: [{article['id']}] - {e}")

        self.crawler.save_history(self.board_name, new_articles)

    def ptt_crawling(self, board_name, page, keywords):

        self.board_name = board_name
        self.crawler = PttCrawler()
        articles = self.crawler.crawling(
            board_name=board_name, page=page, keywords=keywords)

        if articles:
            self.notify(articles)


def crawler(board_name, page, keywords):
    Bot().ptt_crawling(board_name, page, keywords)
    print(f'[ {board_name} ] 爬起來～爬起來～(づ｡◕‿‿◕｡)づ')


@app.route('/CrAwlInG')
def crawling():

    gsc = GoogleSheetClient()
    board_list = gsc.load_ptt_board(sheet_name)
    keywords = gsc.load_keyword(sheet_name)
    page = 2

    threads = list()

    for board_name in board_list:
        thread = threading.Thread(
            target=crawler, args=(board_name, page, keywords,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return "Ptt Crawling Done ."


if __name__ == '__main__':
    crawling()
