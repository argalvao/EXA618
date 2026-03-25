from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin

def parse_sites(filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), 'sites.txt')
    
    try:
        with open(filename, 'r') as f:
            sites = f.read().splitlines()
        
        results = []
        
        for site in sites:
            if not site.strip():
                continue
            
            try:

                url = site if site.startswith(('http://', 'https://')) else f'https://{site}'
                
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = soup.find('title')
                title_text = title.string if title else 'N/A'

                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    img_src = img_tag.get('src')
                    if img_src.startswith('http'):
                        img_text = img_src
                    elif img_src.startswith('/'):
                        base_url = '/'.join(url.split('/')[:3])
                        img_text = urljoin(base_url, img_src)
                    else:
                        img_text = urljoin(url, img_src)
                else:
                    img_text = 'N/A'
                
                results.append({
                    'url': url,
                    'title': title_text,
                    'img': img_text
                })                
                print(f"[OK] {url}")                
            except Exception as e:
                print(f"[ERRO] {site}: {str(e)}")
        
        return results
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

def generate_html(data, output_file=None):
    """
    Generate a simple HTML page from the parsed data.
    """
    if output_file is None:
        output_file = os.path.join(os.path.dirname(__file__), 'index.html')
    
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>EXA618 - Atividade 5 - Resultados</title>
</head>
<body>
    <h1>EXA618 - Atividade 5</h1>
    <p>Discente: Abel Ramalho Galvão</p>
    <hr>
    <p><strong>Total de sites:</strong> """ + str(len(data)) + """</p>
    <hr>
"""
    
    if data:
        for i, item in enumerate(data, 1):
            html_content += f"""    <h2>#{i}</h2>
    <p><strong>Nome:</strong> {item['title']}</p>
    <p><strong>Imagem:</strong></p>
"""
            if item['img'] != 'N/A':
                html_content += f"""    <img src="{item['img']}" alt="Imagem" width="192" height="192">
"""
            else:
                html_content += f"""    <p>Nenhuma imagem encontrada</p>
"""
            html_content += f"""    <hr>
"""
    else:
        html_content += "    <p>Nenhum dado foi coletado.</p>\n    <hr>\n"
    
    html_content += """ 
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n[OK] Arquivo HTML gerado: {output_file}")


if __name__ == '__main__':
    data = parse_sites()
    
    print("\n" + "="*80)
    print(f"Total de sites processados: {len(data)}")
    print("="*80 + "\n")
    
    for i, item in enumerate(data, 1):
        print(f"{i}. URL: {item['url']}")
        print(f"   Nome: {item['title']}")
        print(f"   IMG: {item['img']}")
        print()
    
    generate_html(data)