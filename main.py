from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import re

app = FastAPI()

class LinkPreviewRequest(BaseModel):
    url: str

@app.post("/api/worker/link-preview")
async def link_preview(request_data: LinkPreviewRequest):
    url = request_data.url

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        # 获取网页内容
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取标题
        title = soup.find('title').text if soup.find('title') else 'No title found'

        # 提取描述
        description = ''
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description and meta_description.get('content'):
            description = meta_description.get('content')

        # 提取图片
        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url and img_url.startswith('http'):
                images.append(img_url)

        # 提取图标
        favicons = []
        for link in soup.find_all('link', rel=lambda x: x and 'icon' in x.lower()):
            favicon_url = link.get('href')
            if favicon_url and favicon_url.startswith('http'):
                favicons.append(favicon_url)

        # 提取网站名称
        match = re.search(r'(?:https?://)?([^/]+)', url)
        if match:
            domain = match.group(1)
            # 提取主域名
            site_name = '.'.join(domain.split('.')[-2:]) if '.' in domain else domain
        else:
            site_name = 'Unknown'

        # 返回结果
        result = {
            "url": url,
            "images": images,
            "videos": [],
            "favicons": favicons,
            "title": title,
            "siteName": site_name,
            "description": description,
            "mediaType": "article"  # 默认类型为文章
        }

        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
