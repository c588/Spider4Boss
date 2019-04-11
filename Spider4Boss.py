import requests
from bs4 import BeautifulSoup
import time
import xlwt
import random
import datetime
import selenium


# url:域名+地级市+区/县级市，以 '/' 结尾，例：https://www.zhipin.com/c101210100/b_%E6%BB%A8%E6%B1%9F%E5%8C%BA/
# job:岗位，例 PHP
# cookie:登录后的cookie，F12打开开发者模式，选择Network，点击Doc找到Request Headers下面的cookie，复制字符串
# path:Excel文档保存的路径，以 '/' 结尾
# 返回值  > 0 页面需要人机验证  0 已经到最后一页  -1 爬取成功，准备下一次爬取
def spider4boss(url, job, cookie, path, page_start):
    # header头信息 模拟火狐浏览器，加上自己的 cookie
    headers = {
        'user-agent': 'Mozilla/5.0',
        'cookie': cookie
    }
    # 代理ip  zhipin.com 反爬策略：一个ip一次只能爬取3个页面90条数据，超过100条要求滑块验证
    # proxy1 = {
    #     "http": "http://27.29.44.124:9999",
    #     "https": "https://27.29.44.124:9999",
    # }
    # proxy2 = {
    #     "http": "http://223.111.254.83:80",
    #     "https": "https://223.111.254.83:80",
    # }
    # proxy3 = {
    #     "https": "http://120.198.230.15:8080",
    #     "http": "https://120.198.230.15:8080",
    # }
    # proxy4 = {
    #     "http": "http://39.137.69.6:80",
    #     "https": "https://39.137.69.6:80",
    # }
    # proxies = [proxy1, proxy2, proxy3, proxy4]
    # 打开Excel表 定义sheet 定义表头
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('job_detail')
    head = ['职位名', '薪资', '公司名', '地点', '经验', '学历', '公司行业', '融资阶段', '公司人数', '发布人', '发布时间', '实际经验要求', '岗位网址', 'JD ']
    for h in range(len(head)):
        sheet.write(0, h, head[h])
    row = 1  # 第0行用来写表头

    for page in range(page_start, page_start+10):  # boss每个ip一次只能爬3页
        # 一级url  c101210100：杭州市代号 b_%E6%BB%A8%E6%B1%9F%E5%8C%BA：滨江区转码
        main_url = url + "?query=" + job + "&page=" + str(page) + "&ka=page-" + str(page)
        print('第' + str(page) + '页  ' + main_url)
        hud = ['职位名', '薪资', '公司名', '地点', '经验', '学历', '公司行业', '融资阶段', '公司人数', '发布人', '发布时间', '实际经验要求', '岗位网址', 'JD']
        print('\t'.join(hud))
        # 请求对象
        html = requests.get(main_url, headers=headers)
        # bs对象
        soup = BeautifulSoup(html.text, 'html.parser')
        # 标记 如果ip被反爬限制此行报错，这一步需要进行滑块验证
        # 安装Firefox后不再出现ip限制
        if soup.find('div', 'job-box') is None:
            return page
        # 判断该页是否已经无数据
        is_null = soup.find('div', 'job-box').find('div', 'job-list').find('ul')
        if len(is_null) == 1:  # 当前页面为空值为1说明该页无信息，退出循环
            # return 0  # 此处使用return返回不会进行Excel表保存，所以选择用break结束循环
            break
        for n in soup.find_all('div', 'job-primary'):
            res = []
            pass  # 不写pass上面行会出warning，强迫症必须消除
            res.append(n.find('div', 'job-title').string)  # 添加职位名
            res.append(n.find('span', 'red').string)  # 添加薪资
            res.append(n.find('div', 'company-text').find('a').string)  # 添加公司名
            require = n.find('div', 'info-primary').find('p').contents
            res.append(require[0])  # 添加地区
            res.append(require[2])  # 添加经验
            res.append(require[4])  # 添加学历
            info = n.find('div', 'company-text').find('p').contents
            res.append(info[0])  # 行业
            if 4 > len(info) > 2 and info[2].index('人') != 0:
                res.append('无信息')  # 融资
                res.append(info[2])  # 规模
            else:
                res.append(info[2])  # 融资
                res.append(info[4])  # 规模
            hr = n.find('div', 'info-publis').find('h3', 'name').contents
            res.append(hr[3] + '--' + hr[1])  # 发布者
            if n.find('div', 'info-publis').find('p').string[3:] == '昨天':  # 如果发布时间是 "昨天"，格式化为日期
                res.append(str(datetime.date.today()-datetime.timedelta(days=1))[6:])  # 发布时间
            elif n.find('div', 'info-publis').find('p').string[5:6] == ':':
                res.append(str(datetime.date.today())[6:])  # 发布时间
            else:  # 格式化日期
                res.append(n.find('div', 'info-publis').find('p').string[3:].replace('月', '-').replace('日', ''))
            job_detail = n.find('div', 'info-primary').find('h3', 'name').find('a')
            job_url = 'https://www.zhipin.com/' + job_detail['href']  # 岗位详情url
            # 提取真正的工作经验要求
            html2 = requests.get(job_url, headers=headers)
            soup2 = BeautifulSoup(html2.text, 'html.parser')
            # 标记 如果ip被反爬限制此行报错，下一步需要进行滑块验证
            # 安装Firefox后不再出现ip限制
            if soup2.find('div', 'job-sec') is None:
                return page
            job_sec = soup2.find('div', 'job-sec').find('div', 'text').contents
            exp = 0  # 初始为0 取到一个工作经验要求后置1
            # 将JD保存
            job_description = []
            for i in range(len(job_sec)):
                if i % 2 == 0:  # job_sec中还存了html标签 <br> 不是字符串，用find方法返回None，需要去除
                    job_description.append(job_sec[i])
                    # 确定位置
                    pot = job_sec[i].find('年')
                    if pot != -1 and exp == 0:
                        pot2 = job_sec[i].find('年以上')
                        if pot2 != -1:
                            # 再做一次判断，有的公司在数字后敲了空格
                            if job_sec[i][pot - 1:pot] == ' ':
                                res.append(job_sec[i][pot - 2:pot + 3])
                            else:
                                res.append(job_sec[i][pot - 1:pot + 3])
                        else:
                            if job_sec[i][pot - 1:pot] == ' ':
                                res.append(job_sec[i][pot - 2:pot + 1])
                            else:
                                res.append(job_sec[i][pot - 1:pot + 1])
                        # 只输出一个时间要求 不重复输出，需要用户手动检查岗位描述中的要求
                        exp = 1
            # 如果岗位描述中没有经验要求，填空字符
            if exp == 0:
                res.append('')
            res.append(job_url)  # 岗位描述链接
            job_description = ' '.join(job_description)[33:-29]
            res.append(job_description)  # 岗位描述
            # 写入Excel
            for i in range(len(res)):
                sheet.write(row, i, res[i])
            row += 1
            print(res)
            # quit()
            time.sleep(random.randint(100, 500)/1000)
    workbook.save(path + str(datetime.date.today())[5:] + str(int(page_start/3+1)) + '_boss_job.xls')  # 保存Excel
    print('写入excel成功')
    return 200


def verify_slider():
    from selenium import webdriver
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.by import By
    browser = webdriver.Firefox()
    browser.get('https://www.zhipin.com/verify/slider')
    browser.execute_script("Object.defineProperties(navigator,{webdriver:{get:() => false}});")
    element = browser.find_element_by_id("nc_1__bg")
    pass


def rec_spider(page=1):
    res = spider4boss(url, job, cookie, path, page)
    if -1 == res:
        page += 3
        rec_spider(page)
    elif res > 0:
        print('在第 ' + str(res) + ' 页需要进行人机验证')
        quit()
        # 进行验证
    else:  # 爬取完成
        quit()


if __name__ == "__main__":
    # 此处需要填写自己账号的cookie
    cookie = 'lastCity=101210100; _uab_collina=155391552146954821137608; __c=1554345926; __g=-;' \
             ' __l=l=%2Fwww.zhipin.com%2F&r=; bannerClose_echo20190329=true; t=KP9jOqLS9hUCPH3h;' \
             ' wt=KP9jOqLS9hUCPH3h; JSESSIONID="";' \
             ' Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1553915521,1553915549,1554345926,1554796342;' \
             ' __a=41924534.1553741237.1553915521.1554345926.64.3.48.64;' \
             ' Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1554947693'
    url = 'https://www.zhipin.com/c101210100/b_%E6%BB%A8%E6%B1%9F%E5%8C%BA/'
    job = 'PHP'
    # 此处需要填写Excel表的保存路径，以 "/" 结尾
    path = 'C:/Users/cjy/Desktop/'
    # rec_spider()
    spider4boss(url, job, cookie, path, 1)
