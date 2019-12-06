import requests
from linebot import LineBotApi
from linebot.models import (BoxComponent, BubbleContainer, ButtonComponent,
                            CarouselContainer, FlexSendMessage, ImageComponent,
                            MessageAction, SeparatorComponent, SpacerComponent,
                            TextComponent, URIAction)


class LineBot(object):

    def __init__(self, token):
        self.__token = token
        self.__line_bot_api = LineBotApi(self.__token)

    def __check_usage(self):

        url = "https://api.line.me/v2/bot/message/quota/consumption"
        header = {
            'Authorization': f"Bearer {self.__token}"
        }

        total_usage = requests.get(url, headers=header).json()['totalUsage']
        return total_usage

    def notify(self, channels, articles):

        if self.__check_usage() > 490:
            print("Line-bot Push Message Usage 已達上限！")
            return False

        for idx in range(0, len(articles), 10):
            contents = self.__flex_message_builder(articles=articles[idx:idx+10])
            message = FlexSendMessage(alt_text="➤ 批踢踢評論來囉！",
                                      contents=CarouselContainer(contents=contents))
            for channel in channels:
                try:
                    self.__line_bot_api.push_message(to=channel, messages=message)
                except Exception as e:
                    print(f"Line-bot Notify ERROR: {e}")

        return True

    def __flex_message_builder(self, articles):

        contents = list()

        for article in articles:
            bubble = BubbleContainer(direction='ltr',
                                     # Notification Title
                                     header=BoxComponent(
                                         layout='vertical',
                                         contents=[
                                             TextComponent(text="➤ 批踢踢評論來囉！", weight='bold',
                                                           size='md', color='#E00512')
                                         ]
                                     ),
                                     # Image
                                     hero=ImageComponent(
                                         url='https://i.imgur.com/0TZLoye.png',
                                         size='full',
                                         aspect_ratio='5:3',
                                         aspect_mode='cover'
                                     ),
                                     # Contents
                                     body=BoxComponent(
                                         layout='vertical',
                                         contents=[
                                             # Acticle Title
                                             TextComponent(
                                                 text=article['title'], wrap=True,
                                                 weight='bold', size='lg'),
                                             BoxComponent(
                                                 layout='vertical',
                                                 margin='lg',
                                                 spacing='sm',
                                                 contents=[
                                                     # Board
                                                     BoxComponent(layout='baseline',
                                                                  spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text='Board',
                                                                          color='#aaaaaa',
                                                                          size='sm', flex=1),
                                                                      TextComponent(
                                                                          text=article['board'],
                                                                          wrap=True,
                                                                          color='#666666',
                                                                          size='sm', flex=0)
                                                                  ],
                                                                  ),
                                                     # Author
                                                     BoxComponent(layout='baseline', spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text='Author',
                                                                          color='#aaaaaa',
                                                                          size='sm', flex=1),
                                                                      TextComponent(
                                                                          text=article['author'],
                                                                          wrap=False,
                                                                          color='#666666',
                                                                          size='sm', flex=0),
                                                                  ],
                                                                  ),
                                                     # Date
                                                     BoxComponent(layout='baseline', spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text='Date',
                                                                          color='#aaaaaa',
                                                                          size='sm', flex=1),
                                                                      TextComponent(
                                                                          text=article['date'],
                                                                          wrap=True,
                                                                          color='#666666',
                                                                          size='sm', flex=0),
                                                                  ],
                                                                  ),
                                                     # Divider
                                                     SeparatorComponent(),
                                                     # Content
                                                     BoxComponent(layout='baseline', spacing='sm',
                                                                  contents=[
                                                                      TextComponent(
                                                                          text=article['content'],
                                                                          wrap=True,
                                                                          color='#666666',
                                                                          size='sm', flex=1),
                                                                  ],
                                                                  ),
                                                 ],
                                             )
                                         ],
                                     ),
                                     # Button Action
                                     footer=BoxComponent(
                                         layout='vertical',
                                         spacing='sm',
                                         contents=[
                                             SpacerComponent(size='sm'),
                                             ButtonComponent(
                                                 style='primary',
                                                 height='sm',
                                                 action=MessageAction(label='罵個幹！', text='幹！'),
                                             ),
                                             ButtonComponent(
                                                 style='secondary',
                                                 height='sm',
                                                 action=URIAction(label='來去看一下～',
                                                                  uri=article['link'])
                                             )
                                         ]
                                     ),
                                     )

            contents.append(bubble)

        return contents
