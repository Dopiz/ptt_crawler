import threading

from options import line_info, slack_info, keywords, board_list, page
from bot.line_bot import LineBot
from bot.ptt_crawler import PttCrawler
from bot.slack_bot import SlackBot
from history.history import History


class Crawler(object):

    def __init__(self, board_name, keywords):
        self.board_name = board_name
        self.keywords = keywords
        self.new_articles = None
        self.history = History(self.board_name)

    def notify(self, token, channel, platform):

        if channel is None:
            return

        if platform == "Line":
            bot = LineBot(token)
        elif platform == "Slack":
            bot = SlackBot(token)

        if bot.notify(channel, self.new_articles):
            self.history.save()

    def crawling(self, page):
        crawler = PttCrawler(self.history.history_list, self.board_name, self.keywords)
        self.new_articles = crawler.crawling(page)
        new_articles_id = [article['id'] for article in self.new_articles]
        self.history.history_list = new_articles_id + self.history.history_list


def worker(board_name, keywords, page=1, line=None, slack=None):
    crawler = Crawler(board_name, keywords)
    crawler.crawling(page)
    print(f'[ {board_name} ] 爬起來～爬起來～(づ｡◕‿‿◕｡)づ')
    crawler.notify(line['token'], line['channel'], "Line")
    crawler.notify(slack['token'], slack['channel'], "Slack")


if __name__ == '__main__':

    threads = list()

    for board_name in board_list:
        thread = threading.Thread(target=worker,
                                  args=(board_name, keywords, page, line_info, slack_info, ))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
