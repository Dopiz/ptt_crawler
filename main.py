import os
import threading

import click

from bot.crawler import PttCrawler
from bot.notify_bot import LineNotify, SlackNotify
from history.history import History

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
LINE_TOKEN = os.environ.get('LINE_TOKEN')
LINE_PER_MSG = 10


def worker(board_name: str, keywords: list, pages: int = 1, slack_channel: list = [], line_channel: list = []):
    history = History(file_name=board_name)
    crawler = PttCrawler(board_name, keywords, ignore_list=history.history)
    articles = []

    slack_bot = SlackNotify(SLACK_TOKEN)
    for article in crawler.crawling(pages):
        slack_bot.notify(slack_channel, article)
        history.insert(article.id)
        # articles.append(article)

    # line_bot = LineNotify(LINE_TOKEN)
    # for idx in range(len(articles), LINE_PER_MSG):
    #     line_bot.notify(line_channel, articles[idx:idx + LINE_PER_MSG])

    history.save()


@click.command()
@click.option('-b', '--board', required=True, help='PTT Board Name List (comma-separated)')
@click.option('-k', '--keywords', required=True, help='Keywords List (comma-separated)')
@click.option('-p', '--pages', default=1, help='Page')
@click.option('-sc', '--slack-channel', default="", help='Notify Slack Channel List (comma-separated)')
@click.option('-lc', '--line-channel', default="", help='Notify Line Channel List (comma-separated)')
def crawler(board, keywords, pages, slack_channel, line_channel):

    board = set(board.split(","))
    keywords = set(keywords.split(","))
    slack_channel = set(slack_channel.split(","))
    line_channel = set(line_channel.split(","))

    threads = []
    for board_name in board:
        thread = threading.Thread(
            target=worker,
            args=(board_name, keywords, pages, slack_channel, line_channel,)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


crawler()
