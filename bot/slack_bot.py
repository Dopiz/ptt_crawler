import slack


class SlackBot(object):

    def __init__(self, token):
        self.__slack_bot_api = slack.WebClient(token)

    def notify(self, channels, articles):

        for idx in range(0, len(articles), 5):
            blocks = self.__interactive_message_builder(articles=articles[idx:idx+5])
            for channel in channels:
                try:
                    self.__slack_bot_api.chat_postMessage(channel=channel, blocks=blocks)
                except Exception as e:
                    print(f"Slack-bot Notify ERROR: {e}")

    def __interactive_message_builder(self, articles):

        blocks = list()

        for article in articles:

            block = [
                {
                    "type": "section",
                    "block_id": article['id'],
                    "text": {
                        "type": "mrkdwn",
                        "text": (f"\n*➤ {article['title']}* \n"
                                 f"> *Board:* {article['board']} \n"
                                 f"> *Author:* {article['author']} \n"
                                 f"> *Date:* {article['date']} \n"
                                 f"> *Link:* {article['link']} \n"
                                 f"{article['content']}")
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "https://i.imgur.com/0TZLoye.png",
                        "alt_text": "JKOPay Ptt"
                    }
                },
                {
                    "type": "divider"
                }
            ]

            blocks.extend(block)

        return blocks
