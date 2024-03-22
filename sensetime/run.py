from scrapy import cmdline

cmdline.execute("scrapy crawl zhiwutong-baike -o baike.jsonl --nolog".split())
