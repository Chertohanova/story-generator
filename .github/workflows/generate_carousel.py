import os
import json
import re
import anthropic
from playwright.sync_api import sync_playwright

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

prompt = """
Создай карусель из 5 слайдов для Instagram на тему: "5 правил минимализма".
Ответь ИСКЛЮЧИТЕЛЬНО в формате JSON-массива строк, где каждый элемент — это полный HTML-код одного слайда.
Требования:
- Размеры слайда: width: 1080px; height: 1350px; (для Сторис используй height: 1920px).
- Минималистичный дизайн, Google Fonts (Inter/Montserrat), контрастные цвета.
Формат ответа (только JSON):
["<html>...слайд 1...</html>", "<html>...слайд 2...</html>"]
"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,
    messages=[{"role": "user", "content": prompt}]
)

content = response.content[0].text.strip()
content = re.sub(r'^```json\s*', '', content)
content = re.sub(r'\s*```$', '', content)

slides_html = json.loads(content)
os.makedirs("output_images", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1080, 'height': 1350})
    
    for idx, html_code in enumerate(slides_html, 1):
        page.set_content(html_code)
        page.wait_for_timeout(1000)
        output_path = f"output_images/slide_{idx}.png"
        page.screenshot(path=output_path)
        print(f"Слайд сохранен: {output_path}")
        
    browser.close()
