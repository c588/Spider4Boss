import requests
from bs4 import BeautifulSoup
import time
import xlrd
import xlwt
import random
import datetime
import os
import json
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options


# 爬虫本体
def spider4boss(url, job, cookie, path, page_start, location):
    # header头信息 模拟火狐浏览器，加上自己的 cookie
    headers = {
        'user-agent': 'Mozilla/5.0',
        'cookie': cookie
    }
    # 打开Excel表 定义sheet 定义表头
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('job_detail')
    head = ['职位名', '薪资', '公司名', '地点', '经验', '学历', '公司行业', '融资阶段', '公司人数', '发布人',
            '发布时间', '实际经验要求', '岗位网址', 'JD', '经度', '纬度', '区']
    for h in range(len(head)):
        sheet.write(0, h, head[h])
    row = 1  # 第0行用来写表头，row变成1
    # 判断程序是否结束的标志位
    is_end = 0
    # 当前时间
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    for page in range(page_start, page_start+3):  # boss每个ip一次只能爬3页
        # 一级url  c101210100：杭州市代号 b_%E6%BB%A8%E6%B1%9F%E5%8C%BA：滨江区转码
        main_url = url + location + "/?query=" + job + "&page=" + str(page) + "&ka=page-" + str(page)
        print('第' + str(page) + '页  ' + main_url)
        hud = ['职位名', '薪资', '公司名', '地点', '经验', '学历', '公司行业', '融资阶段', '公司人数', '发布人',
               '发布时间', '实际经验要求', '岗位网址', 'JD', '详细地址']
        print('\t'.join(hud))
        # 请求对象
        html = requests.get(main_url, headers=headers)
        # bs对象
        soup = BeautifulSoup(html.text, 'html.parser')
        # 标记 如果ip被反爬限制此行报错，这一步需要进行滑块验证
        # 一级页面
        if soup.find('div', 'job-box') is None:
            print('一级页面在第' + str(page) + '页被限制ip')
            # 返回的是这一整个循环的起始位置，及 1,4,7,10...
            return page_start
        # 判断该页是否已经无数据
        is_null = soup.find('div', 'job-box').find('div', 'job-list').find('ul')
        if len(is_null) == 1:  # 当前页面为空值为1说明该页无信息，退出循环
            # return 0  # 此处使用return返回不会进行Excel表保存，所以选择用break结束循环
            # 标志位，可以结束程序
            is_end = 1
            break
        for n in soup.find_all('div', 'job-primary'):
            res = []
            pass  # 不写pass上面行会出warning，强迫症必须消除
            res.append(n.find('div', 'job-title').string)  # 添加职位名
            salary = n.find('span', 'red').string
            pot = salary.find('k-')
            res.append(n.find('span', 'red').string[0:pot])  # 添加薪资
            res.append(n.find('div', 'company-text').find('a').string)  # 添加公司名
            require = n.find('div', 'info-primary').find('p').contents
            res.append(require[0])  # 添加地区
            if '经验不限' == require[2]:  # 添加学历
                res.append(0)
            elif '应届生' == require[2]:
                res.append(1)
            elif '1年以内' == require[2]:
                res.append(2)
            elif '1-3年' == require[2]:
                res.append(3)
            elif '3-5年' == require[2]:
                res.append(4)
            else:
                res.append(5)
            if '学历不限' == require[4]:  # 添加经验
                res.append(0)
            elif '大专' == require[4]:
                res.append(2)
            elif '本科' == require[4]:
                res.append(3)
            else:
                res.append(1)
            info = n.find('div', 'company-text').find('p').contents
            res.append(info[0])  # 行业
            if 4 > len(info) > 2 and info[2].index('人') != 0:
                res.append('无信息')  # 融资
                pot = info[2].find('-')
                if -1 == pot:
                    res.append(10000)  # 规模
                else:
                    res.append(info[2][0:pot])  # 规模
            else:
                res.append(info[2])  # 融资
                pot = info[4].find('-')
                if -1 == pot:
                    res.append(10000)  # 规模
                else:
                    res.append(info[4][0:pot])  # 规模
            hr = n.find('div', 'info-publis').find('h3', 'name').contents
            res.append(hr[3] + '--' + hr[1])  # 发布者
            if n.find('div', 'info-publis').find('p').string[3:] == '昨天':  # 如果发布时间是 "昨天"，格式化为日期
                res.append(str(datetime.date.today()-datetime.timedelta(days=1))[5:])  # 发布时间
            elif n.find('div', 'info-publis').find('p').string[5:6] == ':':
                res.append(str(datetime.date.today())[5:])  # 发布时间
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
                print('二级页面被限制ip')
                return page_start
            # res.append(soup2.find('div', 'job-detail').find('div', 'detail-op').find('p', 'gray').contents[2])  # hr状态
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
            res.append(now_time)  # 当前时间
            res.append(soup2.find('div', 'location-address').string)  # 公司详细地址
            lng_lat = get_lng_lat(soup2.find('div', 'location-address').string)
            res.append(lng_lat['longitude'])  # 保存经度
            res.append(lng_lat['latitude'])  # 保存纬度
            res.append(location)
            # 写入Excel
            for i in range(len(res)):
                sheet.write(row, i, res[i])
            row += 1
            # 打印简略的内容
            print_num = list(range(0, 11))
            print_num.append(15)
            print_num.append(18)
            print_content = []
            for i in range(len(print_num)):
                print_content.append(res[print_num[i]])
            print(print_content)
            # quit()
            time.sleep(random.randint(100, 300)/1000)
    # 保存Excel 例：04-25_滨江区_1_boss_job.xls
    workbook.save(path + str(datetime.date.today())[5:] + '_' + location
                  + '_' + str(int(page_start/3+1)) + '_boss_job.xls')
    print('写入excel成功')
    if 0 == is_end:
        return 200
    else:
        return 0


# 通过boss直聘网站的ip限制验证
def verify_slider():
    options = Options()
    # 无头参数
    options.add_argument('-headless')
    browser = webdriver.Firefox(firefox_options=options)
    browser.implicitly_wait(5)
    browser.get('https://www.zhipin.com/verify/slider')
    browser.execute_script("Object.defineProperties(navigator,{webdriver:{get:() => false}});")
    element = browser.find_element_by_id('nc_1_n1z')
    action = ActionChains(browser)
    action.drag_and_drop_by_offset(element, 280, 0).perform()
    time.sleep(2)
    browser.close()


# 状态码 200:成功爬取三页数据，继续爬取后三页 (0,200):被限制在第x页 0:爬取完成
def rec_spider(url, job, cookie, path, location, page=1):
    res = spider4boss(url, job, cookie, path, page, location)
    if 200 == res:
        page += 3
        rec_spider(url, job, cookie, path, location, page)
    elif 200 > res > 0:
        # res --  1:爬1-3页被限制  2:4-6页  3:7-9页  4:第10页
        print('在第 ' + str(res) + ' 次需要进行人机验证')
        # 调用验证方法进行验证
        verify_slider()
        # 继续爬取
        rec_spider(url, job, cookie, path, location, res)
    else:  # 爬取完成
        print(location + '爬取完成')


def merge_excel(path, districts, date=str(datetime.date.today())[5:]):
    # 先读取所有Excel表
    all_data = list()
    all_district = districts
    for k in range(len(all_district)):  # 遍历所有市辖区
        for i in range(1, 4):  # 每个市辖区最多4个Excel文件（10页/3页每个）
            file_path = path + date + '_' + all_district[k] + '_' + str(i) + '_boss_job.xls'
            if os.path.exists(file_path):
                data = xlrd.open_workbook(file_path)  # 打开Excel
                table = data.sheet_by_index(0)  # 打开第一个表
                for j in range(1, table.nrows):
                    all_data.append(table.row_values(j))
                # 读取完后删除文件
                os.remove(file_path)
            else:
                break
    print('本次共爬取 ' + str(len(all_data)) + ' 条数据')
    # ↓这里连接数据库并将数据写入
    pass
    # ↑这里连接数据库并将数据写入
    print('数据写入数据库成功')
    # 将数据输入到总表
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('job_detail')
    # 表头写入第一行
    head = ['id', 'job', 'salary', 'company', 'location', 'exp', 'education', 'industry', 'financing', 'scale', 'hr',
            'pub_time', 'real_exp', 'url', 'jd', 'search_time', 'address', 'longitude', 'latitude', 'cg_district']
    for h in range(len(head)):
        sheet.write(0, h, head[h])
    row = 1
    # 写入职位数据
    for i in range(len(all_data)):
        for j in range(len(head)-1):
            sheet.write(row, j+1, all_data[i][j])
        row += 1
    # 保存Excel
    workbook.save(path + date + '_boss_job.xls')
    print('合并excel成功')


# 调用高德web api获取地址的经纬度
def get_lng_lat(address):
    # 防止地名过短匹配到外省的经纬度
    add_address = address
    if address[0:2] != '浙江' or address[0:2] != '杭州':
        add_address = '浙江省' + address
    ll_response = requests.get('https://restapi.amap.com/v3/geocode/geo?address='
                               + add_address + '&output=json&key=cbb6acd4327b17ee38659d94ade357af')
    ll_result = ll_response.text
    lng_lat = json.loads(ll_result)['geocodes'][0]['location']  # 得到经纬度字符串 经度,纬度
    pot = lng_lat.find(',')
    if pot <= 0:
        res = {'longitude': 0, 'latitude': 0}
    else:
        res = {'longitude': lng_lat[: pot], 'latitude': lng_lat[pot + 1:]}
    return res


if __name__ == "__main__":
    cities_code = {'北京': '101010100', '上海': '101020100', '广州': '101280100', '深圳': '101280600',
                   '杭州': '101210100', '宁波': '101210400', '金华': '101210900', '南京': '101190100',
                   '苏州': '101190400', '扬州': '101190600', '武汉': '101200100', '重庆': '101040100',
                   '成都': '101270100'}
    # 参数说明
    # user_cookie:用户登录后的个人cookie，必须，登录后才显示最新数据
    # 登录后F12，选择Network，刷新后点击www.zhipin.com，右侧Request Headers中复制cookie项，通常以lastCity=开头
    user_cookie = ''
    # user_url:选择城市后将此处的"杭州"替换为所需地级市
    user_url = 'https://www.zhipin.com/c' + cities_code['杭州'] + '/b_'
    # user_job:需要搜索的岗位
    user_job = 'PHP'
    # user_path:Excel表存放的位置，以 / 结尾
    user_path = 'C:/Users/帅气的吴彦祖/Desktop/'
    # hz_districts:市辖区数组
    hz_districts = ['滨江区', '西湖区', '江干区', '余杭区', '萧山区', '拱墅区', '下城区', '上城区', '富阳区', '临安区']
    # hz_districts = ['西湖区', '江干区', '余杭区', '萧山区', '拱墅区', '下城区', '上城区', '富阳区', '临安区']
    for i in range(len(hz_districts)):
        rec_spider(user_url, user_job, user_cookie, user_path, hz_districts[i])
        # 爬完一个区暂停一分钟
        time.sleep(30)
    print('爬虫完成，进行Excel合并')
    merge_excel(user_path, hz_districts)
