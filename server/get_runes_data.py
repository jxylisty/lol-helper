import requests
import json
import re
import sys

def fetch_json(url, timeout=10):
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text) if text else ""

def get_runes_data(language="zh_CN"):
    versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    versions = fetch_json(versions_url)
    if not versions:
        print(json.dumps({'error': '无法获取版本信息'}, ensure_ascii=False))
        return
    
    version = versions[0]
    
    runes_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{language}/runesReforged.json"
    runes_data = fetch_json(runes_url)
    if not runes_data:
        print(json.dumps({'error': '无法获取符文数据'}, ensure_ascii=False))
        return
    
    base_icon_url = "https://ddragon.leagueoflegends.com/cdn/img"
    
    rune_trees = []
    all_runes = []
    
    for tree in runes_data:
        tree_info = {
            'id': tree.get('id'),
            'key': tree.get('key'),
            'name': tree.get('name'),
            'icon': f"{base_icon_url}/{tree.get('icon', '')}",
            'slots': []
        }
        
        for slot in tree.get('slots', []):
            slot_runes = []
            for rune in slot.get('runes', []):
                rune_info = {
                    'id': rune.get('id'),
                    'key': rune.get('key'),
                    'name': rune.get('name'),
                    'shortDesc': clean_html(rune.get('shortDesc', '')),
                    'longDesc': clean_html(rune.get('longDesc', '')),
                    'icon': f"{base_icon_url}/{rune.get('icon', '')}"
                }
                slot_runes.append(rune_info)
                all_runes.append(rune_info)
            
            tree_info['slots'].append({
                'type': slot.get('type'),
                'runes': slot_runes
            })
        
        rune_trees.append(tree_info)
    
    result = {
        'version': version,
        'trees': rune_trees,
        'all_runes': all_runes
    }
    
    # 只在直接运行时打印
    if __name__ == '__main__':
        print(json.dumps(result, ensure_ascii=False))
    
    return result

if __name__ == '__main__':
    lang = sys.argv[1] if len(sys.argv) > 1 else "zh_CN"
    get_runes_data(lang)
