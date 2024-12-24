import requests
import re
import os
import json
import subprocess
from bs4 import BeautifulSoup


if not os.path.exists('./b_video'):
    os.mkdir('./b_video')
headers = {
    # 获取最高清1080p数据,加入cookie个人信息
    'Cookie': 'buvid3=E0CC3B70-C034-5F99-108B-417EAAB6D58D72208infoc; b_nut=1713876972; _uuid=787A410510-29D6-3E12-CA3F-B34193EB71D473899infoc; buvid4=0E1C561F-6DF8-B44C-DF45-45C180B3AEF473881-024042312-A0qBauS20OKwBtcJZSUxzWEO4CNtd2qdxh3XvdPkMx%2FKI6%2BT71OvmVbVmN3eRp3P; enable_web_push=DISABLE; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW3; rpdid=0zbfAHUo63|11buTGIeY|2D|3w1RZfHa; header_theme_version=CLOSE; DedeUserID=442663406; DedeUserID__ckMd5=30156e8f6d52e5c9; buvid_fp_plain=undefined; LIVE_BUVID=AUTO4017241252399556; SESSDATA=3cbf9059%2C1744699099%2Cf005d%2Aa1CjDXidLlhcVQXR2HJMsuiJC3VkrBakxgwqwJxoUEyxO4niemqZCfdbUOhexvScrim8MSVkdNM05WSng4Vmtfd1M2c19SalE3a25zYkp5eU1xOEhKZUU4a2w5Q3FLUlJUSU5ya1Q4VHE5Y1p6bmVzMElNazFndnhILWRZSW1leGFSaE12THZXbVdnIIEC; bili_jct=4c281368a7f9090515b851a60880ccc1; home_feed_column=5; browser_resolution=1545-825; blackside_state=0; CURRENT_BLACKGAP=0; fingerprint=adcfd40cacc10584fc9742a0bf252c85; buvid_fp=adcfd40cacc10584fc9742a0bf252c85; CURRENT_QUALITY=80; CURRENT_FNVAL=4048; bp_t_offset_442663406=1012124732817932288; b_lsid=F106454FB_193F62BDD10; sid=5914pnm3; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUyNjMyOTAsImlhdCI6MTczNTAwNDAzMCwicGx0IjotMX0.le6Ukbm15K5jiL1tPu2zn8g0SFALGNzzDXoL-2cqcho; bili_ticket_expires=1735263230; bsource=search_google; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com'
    ,
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"
    ,
    'referer': 'https://www.bilibili.com/?spm_id_from=333.1365.0.0'
}


def get_resopnse(html_url):
    response = requests.get(url=html_url, headers=headers)
    return response


# 获取视频标题
def get_viedeo_info(html_url):
    resopnse = get_resopnse(html_url)
    soup = BeautifulSoup(resopnse.text, 'html.parser')
    title_tag = soup.find('h1', class_='video-title')

    if title_tag:
        title = title_tag.get('title', '').replace(' ', '')
        video_info = [title]
        return video_info
    else:
        print("未能找到视频标题")
        return None


# 获取视频的视频和音频的链接
def get_video_content(BV_ID, spm_id_from, vd_source):
    index_url = 'https://www.bilibili.com/video/' + BV_ID + '/'
    data = {
        'spm_id_from': spm_id_from,
        'vd_source': vd_source
    }
    page_text = requests.get(url=index_url, params=data, headers=headers).text
    # window.__playinfo__ =({.*?})
    # (.*?只能匹配字符不能匹配符号,例如'{}')
    ex = r'window\.__playinfo__=({.*?})\s*</script>'
    json_data = re.findall(ex, page_text)[0]
    # json字符串转换为python对象
    data = json.loads(json_data)
    audio_url = data['data']['dash']['audio'][0]['baseUrl']
    video_url = data['data']['dash']['video'][0]['baseUrl']
    video_content = [audio_url, video_url]
    return video_content


# 数据保存
def save(title, audio_url, video_url):
    print("开始下载"+title)
    audio_content = get_resopnse(audio_url).content
    video_content = get_resopnse(video_url).content
    fp = open(title + '.mp3', mode='wb')
    fp.write(audio_content)
    fp = open(title + '.mp4', mode='ab')
    fp.write(video_content)
    print(title, '保存完成')


# 音视频合成
def merge_data(video_name):
    '''数据合并'''
    output_dir = './out/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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

def main(BV_ID, spm_id_from, vd_source):
    html_url = f'https://www.bilibili.com/video/{BV_ID}/?spm_id_from={spm_id_from}&vd_source={vd_source}'
    video_info = get_viedeo_info(html_url)
    video_content = get_video_content(BV_ID, spm_id_from, vd_source)
    save(video_info[0], video_content[0], video_content[1])
    merge_data(video_info[0])


b_url = input('输入爬取视频的网址:')
# b_url='https://www.bilibili.com/video/BV1et421a7E1/?spm_id_from=333.337.search-card.all.click&vd_source=77c296188837a388ccd6343ff122de09'
# 取出参数,BV_ID,spm,_id_from,vd_source
list = b_url.split('/')
BV_ID = list[4]
new_list = list[5].split('=')
spm_id_from = new_list[1].split('&')[0]
vd_source = new_list[-1]
main(BV_ID, spm_id_from, vd_source)