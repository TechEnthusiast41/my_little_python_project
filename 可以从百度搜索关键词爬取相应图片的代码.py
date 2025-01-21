import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import quote

# 创建保存图片的目录
save_dir = "downloaded_images"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


# 下载图片的函数
def download_image(img_url, img_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        img_data = requests.get(img_url, headers=headers, timeout=5, proxies={"http": None, "https": None}).content
        with open(os.path.join(save_dir, img_name), 'wb') as f:
            f.write(img_data)
        print(f"下载成功: {img_name}")
    except Exception as e:
        print(f"下载失败: {img_name}, 错误: {e}")


# 获取页面图片链接
def get_image_urls(driver):
    # 获取当前页面的源代码
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 找到所有图片的 <img> 标签
    img_tags = soup.find_all('img', {'src': True})
    img_urls = []

    for img in img_tags:
        img_url = img['src']
        if img_url.startswith('http'):
            img_urls.append(img_url)

    return img_urls


# 模拟浏览器滚动加载图片
def scroll_and_download(search_query, total_images=80000):
    # 使用 Selenium 打开 Chrome 浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 隐藏浏览器窗口
    options.add_argument('--disable-gpu')  # 禁用GPU硬件加速

    # 使用 webdriver-manager 自动下载和管理 chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    search_query_encoded = quote(search_query)
    url = f'https://image.baidu.com/search/index?tn=baiduimage&fm=result&ie=utf-8&word={search_query_encoded}'

    driver.get(url)

    # 滚动页面，加载更多图片
    downloaded_images = 0
    while downloaded_images < total_images:
        print(f"当前下载图片数量: {downloaded_images}")

        # 获取当前页面图片链接
        img_urls = get_image_urls(driver)

        for img_url in img_urls:
            img_name = f"img_{downloaded_images + 1}.jpg"
            download_image(img_url, img_name)
            downloaded_images += 1

            if downloaded_images >= total_images:
                break

        # 如果未达到目标图片数量，进行滚动加载
        if downloaded_images < total_images:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 3))  # 模拟人类行为，延时避免被封禁

    print(f"共下载 {downloaded_images} 张图片")
    driver.quit()


# 执行函数
search_query = "血常规"  # 可以更换为你需要搜索的关键字
scroll_and_download(search_query)
