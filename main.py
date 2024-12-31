import requests
import re
import os
import json
import subprocess
from bs4 import BeautifulSoup

# 检查目录是否存在，用于存储下载的视频；如果不存在则创建目录
if not os.path.exists('./b_video'):
    os.mkdir('./b_video')

# HTTP 请求头，包括 Cookie 和 User-Agent，referer标识表示发起当前请求的来源页面的 URL，用于伪装为浏览器访问
headers = {
    # 包含 Cookie 信息，用于访问需要登录的资源
    'Cookie': '...',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76",
    'referer': 'https://www.bilibili.com/?spm_id_from=333.1365.0.0'
}

# 获取指定 URL 的响应数据
def get_response(html_url):
    response = requests.get(url=html_url, headers=headers)
    return response

# 获取视频标题
def get_video_info(html_url):
    response = get_response(html_url)  # 获取 HTML 响应
    soup = BeautifulSoup(response.text, 'html.parser')  # 使用 BeautifulSoup 解析 HTML
    title_tag = soup.find('h1', class_='video-title')  # 查找标题标签

    if title_tag:
        title = title_tag.get('title', '').replace(' ', '')  # 获取标题并去掉空格
        video_info = [title]
        return video_info
    else:
        print("未能找到视频标题")
        return None

# 获取视频和音频的链接
def get_video_content(BV_ID, spm_id_from, vd_source):
    index_url = 'https://www.bilibili.com/video/' + BV_ID + '/'  # 视频页面 URL
    data = {
        'spm_id_from': spm_id_from,
        'vd_source': vd_source
    }
    page_text = requests.get(url=index_url, params=data, headers=headers).text
    # 使用正则表达式提取视频和音频的 JSON 数据
    ex = r'window\.__playinfo__=({.*?})\s*</script>'
    json_data = re.findall(ex, page_text)[0]
    # 将 JSON 字符串转换为 Python 对象
    data = json.loads(json_data)
    audio_url = data['data']['dash']['audio'][0]['baseUrl']
    video_url = data['data']['dash']['video'][0]['baseUrl']
    video_content = [audio_url, video_url]
    return video_content

# 保存视频和音频数据到本地
def save(title, audio_url, video_url):
    print("开始下载" + title)
    audio_content = get_response(audio_url).content  # 获取音频数据
    video_content = get_response(video_url).content  # 获取视频数据

    # 保存音频文件
    with open(title + '.mp3', mode='wb') as fp:
        fp.write(audio_content)

    # 保存视频文件
    with open(title + '.mp4', mode='ab') as fp:
        fp.write(video_content)

    print(title, '保存完成')

# 合并音频和视频文件
def merge_data(video_name):
    '''数据合并'''
    output_dir = './out/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 创建输出目录

    # 使用 ffmpeg 命令合并音频和视频
    cmd = rf"ffmpeg -i {video_name}.mp4 -i {video_name}.mp3 -acodec copy -vcodec copy {output_dir}{video_name}out.mp4"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')

    if result.returncode == 0:  # 如果命令执行成功
        print(f"{video_name} 合并完成")
        # 删除原始的 .mp4 和 .mp3 文件
        for ext in ('.mp4', '.mp3'):
            file_path = f"{video_name}{ext}"
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
    else:
        print("合并过程中发生错误:", result.stderr)

# 主程序入口
def main(BV_ID, spm_id_from, vd_source):
    html_url = f'https://www.bilibili.com/video/{BV_ID}/?spm_id_from={spm_id_from}&vd_source={vd_source}'
    video_info = get_video_info(html_url)  # 获取视频信息
    if video_info is None:
        return

    video_content = get_video_content(BV_ID, spm_id_from, vd_source)  # 获取视频内容链接
    save(video_info[0], video_content[0], video_content[1])  # 保存音频和视频
    merge_data(video_info[0])  # 合并音频和视频

# 获取用户输入的 Bilibili 视频 URL
b_url = input('输入爬取视频的网址:')

# 从 URL 中提取参数 BV_ID、spm_id_from 和 vd_source
list = b_url.split('/')
BV_ID = list[4]
new_list = list[5].split('=')
spm_id_from = new_list[1].split('&')[0]
vd_source = new_list[-1]

# 调用主函数
main(BV_ID, spm_id_from, vd_source)
