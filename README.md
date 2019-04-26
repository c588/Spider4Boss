# Spider4Boss
需要下载火狐浏览器和驱动文件geckodriver.exe<br>
驱动文件放在Spider4Boss.py同一目录<br>
运行完成后会在指定目录生成单个Excel文件<br>
中途报错退出问题仍需解决，目前为手动ctrl C停止重新运行<br>
<br>
参数说明<br>
user_cookie:用户登录后的个人cookie，必须，登录后才显示最新数据。
登录后F12，选择Network，刷新后点击www.zhipin.com，右侧Request Headers中复制cookie项，通常以lastCity=开头<br>
user_url:选择城市后将此处的"c101210100"替换为地级市代号，此处为杭州市代号<br>
user_job:需要搜索的岗位<br>
user_path:Excel表存放的位置<br>
hz_districts:市辖区数组<br>
