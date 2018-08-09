#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-10-15 10:22:35
# Project: qq_friends

from pyspider.libs.base_handler import *
from mymodule.public import getHeaders
import time

scroll = """
        function () {
            var check = function(){
                var text=$("#feed_friend_tips > div > p").text();
                var flag="没有更多动态显示";
                if(flag==text){
                    return true;
                }else{
                    return false;
                }
            };
            var scroll=function () {
                window.scrollTo(0,document.body.scrollHeight);
                if(check()){
                    clearInterval(interval);
                }
            };
            var interval=setInterval(scroll,200)
        }
        """


class Handler(BaseHandler):
    crawl_config = {
        "cookies": {}
    }

    def on_start(self):
        self.crawl('https://user.qzone.qq.com/111111111/infocenter', headers=getHeaders(), callback=self.index_page,
                   validate_cert=False, fetch_type='js', js_script=scroll, itag=str(time.time()))

    def index_page(self, response):
        #with open(r"result.html", "w+", encoding="utf-8") as file:
            #file.write(response.content)
        print(response.url)

    def detail_page(self, response):
        pass
