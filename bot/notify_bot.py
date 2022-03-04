from typing import List

import slack
from linebot import LineBotApi
from linebot.models import (BoxComponent, BubbleContainer, ButtonComponent,
                            CarouselContainer, FlexSendMessage, ImageComponent,
                            SeparatorComponent, TextComponent, URIAction)

from bot.crawler import Article


class LineNotify:

    def __init__(self, token: str):
        self._bot_api = LineBotApi(channel_access_token=token)

    def notify(self, channels: list, articles: List[Article]):
        contents = [self._message_builder(article) for article in articles]
        message = FlexSendMessage(
            alt_text="➤ 批踢踢評論來囉！",
            contents=CarouselContainer(contents=contents)
        )
        for channel in channels:
            try:
                self._bot_api.push_message(to=channel, messages=message)
            except Exception as e:
                print("Notify Error:", e)

    def _message_builder(self, article: Article):
        return BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text="➤ 批踢踢評論來囉！", weight='bold', size='md', color='#E00512')
                ]
            ),
            hero=ImageComponent(
                url='https://i.imgur.com/0TZLoye.png',
                size='full',
                aspect_ratio='5:3',
                aspect_mode='cover'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=article.title, wrap=True, weight='bold', size='lg'),
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(text='Board', color='#aaaaaa', size='sm', flex=1),
                                        TextComponent(text=article.board, wrap=True, color='#666666', size='sm', flex=0)
                                    ],
                                ),
                            BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(text='Author', color='#aaaaaa', size='sm', flex=1),
                                        TextComponent(text=article.author, wrap=False,
                                                      color='#666666', size='sm', flex=0),
                                    ],
                                ),
                            BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(text='Date', color='#aaaaaa', size='sm', flex=1),
                                        TextComponent(text=article.date, wrap=True, color='#666666', size='sm', flex=0),
                                    ],
                                ),
                            SeparatorComponent(),
                            BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(text=article.content, wrap=True,
                                                      color='#666666', size='sm', flex=1),
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
                        ButtonComponent(
                            style='secondary',
                            height='sm',
                            action=URIAction(label='Link', uri=article.link)
                        )
                ]
            ),
        )


class SlackNotify:

    def __init__(self, token: str):
        self._bot_api = slack.WebClient(token=token)

    def notify(self, channels: list, article: Article):
        for channel in channels:
            try:
                self._bot_api.chat_postMessage(
                    channel=channel,
                    blocks=self._message_builder(article),
                    unfurl_links=False
                )
            except Exception as e:
                print("Notify Error:", e)

    def _message_builder(self, article: Article):
        return [
            {
                "type": "section",
                "block_id": article.id,
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📢  {article.title}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*>Link:*\t{article.link}\n"
                        f"*>Content:*\t{article.content}"
                    )
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://i.imgur.com/YBsmpaw.png",
                    "alt_text": "PTT"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Author:* _{article.author}_"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Board:* _{article.board}_"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Date:* _{article.date}_"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]
