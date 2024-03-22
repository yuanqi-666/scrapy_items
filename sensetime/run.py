from scrapy import cmdline

cmdline.execute("scrapy crawl zhiwutong -o 1.jsonl --nolog".split())
