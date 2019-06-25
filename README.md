# PTT Crawler
- 由 Google Sheet 抓取要爬的 PTT 看板
- Page 決定要爬的頁數
- 透過 threading，同時多個執行緒爬行多個看板
- 由 Google Sheet 抓取 Line & Slack Push Token、Notify Channel
- 將爬行結果組裝成 Line Flex Message & Carousel Container 推送給使用者
