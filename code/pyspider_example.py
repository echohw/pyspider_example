#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 组名改为delete后如果状态为stop状态，24小时后项目会被系统删除
# rate是每秒爬取页面数,burst是并发数．如1/3是三个并发,每秒爬取一个页面
# TODO是新建项目后的默认状态,不会运行项目．
# STOP状态是停止状态,也不会运行．
# CHECHING是修改项目代码后自动变的状态．
# DEBUG是调试模式,遇到错误信息会停止继续运行，
# RUNNING是运行状态,遇到错误会自动尝试,如果还是错误会跳过错误的任务继续运行
# 解决ssl问题:self.crawl(url, callback=self.index_page, validate_cert=False)
# 任务调度:
    # 当新请求已经在队列中(即任务状态是 active 时),会忽略新的请求,即使它们的参数不一致,可以通过force_update参数强制更新处于active状态的任务,self.crawl(url,force_update=True, callback=self.index_page)
    # 当任务状态是success或failed时,参数age会检测上次抓取时间+age是否大于当前时间,若大于,则会重启任务,或者,可以通过设置itag(例如前链中提取的更新时间)参数,当本次请求的 itag与上次不同时,会重启任务
from pyspider.libs.base_handler import *
# Handler(BaseHandler)是脚本的主体,每个必须继承自BaseHandler
class Handler(BaseHandler):
    crawl_config = { # 类属性,对象也可访问
        'proxy': 'http://188.226.141.217:8080',  # http # 设置代理服务器,整个项目有效
        'proxy': 'https://182.253.32.65:3128'  # https
    }
    # @every(minutes=24*60,seconds=0)这个设置是告诉scheduler(调度器)on_start方法每天执行一次
    @every(minutes=24 * 60)
    # def on_start(self)方法是入口代码,当在web控制台点击run按钮时会执行此方法
    def on_start(self):
        # self.crawl用于控制链接抓取,使用callback=self.index_page指定用哪个函数解析抓取到的页面
        # self.crawl(url,callback=self.index_page)这个方法是调用API生成一个新的爬取任务,这个任务被添加到待抓取队列
        self.crawl('http://www.qiushibaike.com/',callback=self.index_page,save={},validate_cert=False,fetch_type='js') # 使用save传递数据,关闭ssl验证,使用phantomjs抓取动态页面
    # @config(age=10 * 24 * 60 * 60)这个设置告诉scheduler(调度器)这个request(请求)过期时间是10天,10天内再遇到这个请求直接忽略,这个参数也可以在self.crawl(url,age=10*24*60*60)和crawl_config中设置
    @config(age=10 * 24 * 60 * 60)
    # def index_page(self,response)回调函数可以通过访问response访问抓取到的数据。
    def index_page(self, response):
        # response.doc 返回一个PyQuery类型的对象
        # response.json 用于解析json数据
        # response.etree 返回的是lxml对象
        # response.text 返回的是unicode文本
        # response.content 返回的是二进制数据
        for each in response.doc('a[href^="http"]').items(): # xxx.items():<class 'generator'>
            self.crawl(each.attr.href, callback=self.detail_page,save=response.save, validate_cert=False,js_script="function(){};") # 通过response.save获取传递过来的数据,页面加载结束后会执行js_script中的代码
    # @config(priority=2) 这个是优先级设置,数字越小越先执行
    @config(priority=2)
    # 返回一个结果集对象,这个结果默认会被添加到数据库resultdb(默认sqlite),重载on_result(self,result)函数可以修改这个行为
    def detail_page(self, response):
        # response.status_code 请求返回的状态码
        # response.url 请求的url(当发生跳转时,为跳转后的url)
        # response.orig_url 原请求的url
        # response.headers 响应头
        # response.cookies 返回的cookies
        # response.error 请求错误信息,string类型
        # response.time 请求用时
        # response.ok 请求是否成功
        # response.encoding 页面的编码,会根据header,content自动检测;当检测错误时,可以手动设定编码覆盖
        # response.text 页面经过转码成为 unicode 的数据
        # response.content 页面未转码内容
        # response.save 从上一个任务中传下来的数据
        # response.json 尝试解析json
        # response.doc 将页面建树,返回一个 pyquery 对象
        # response.raise_for_status() 尝试抛出抓取异常
        return {
            "url": response.url,
            "title": response.doc('title').text(),
        }
    def on_result(self, result): # 可在此处操作返回的数据
        pass
# crawl()方法中的参数设置:
    # url:需要被抓取的url或url列表
    # callback:指定回调函数
    # age:指定任务的有效期(s),有效期内不会重复抓取,优先于方法上面设置的参数,默认为-1(永不过期,只抓一次)
    # priority:指定任务的优先级,数值越大越先被执行,默认为0
    # exetime:定时抓取(time.time()+30*60:页面将在30分钟后被抓取)
    # retries:任务执行失败后重试次数
    # itag:任务标记值,会在抓取时进行对比,如果值发生改变,即使未过期,也会进行重爬,默认为None(也可在配置为全局参数,重新执行所有任务)
    # auto_recrawl:自动重爬,默认为False,与age配合使用时意为每隔age时间重新爬取
    # method:请求方式,默认为GET
    # params:请求时会将字典中的参数拼接到url中
    # data:要提交的数据,当method为POST时使用,字典中的参数会自动进行编码
    # headers:自定义的请求头(字典类型)
    # cookies:自定义请求的cookies(字典类型)
    # connect_timeout:指定请求超时(s),默认20s
    # allow_redirects:遇到30x状态码是否跟随,默认为True
    # validate_cert:遇到https类型的url是否验证证书,默认为True
    # proxy:设置代理服务器,格式:username:password@hostname:port(暂时只支持http代理)
    # fetch_type:是否启用JavaScript解析引擎
    # js_script:页面加载前或之后运行的js代码,格式:function(){};
    # js_run_at:指定js代码的执行时间,默认:document-end
    # save:传递一个对象给任务,在任务解析时可以通过response.save来获取传递的值