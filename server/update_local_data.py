"""
本地数据更新脚本
用于从 OP.GG 和 DDragon 抓取数据并保存到本地 JSON 文件
"""
import json
import os
import sys
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from get_runes_data import get_runes_data
from get_champion_builds import get_champion_builds, extract_build_data

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)

def save_json(data, filename):
    """保存数据到 JSON 文件"""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved {filename}")

def load_json(filename):
    """从 JSON 文件加载数据"""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

async def get_all_champions_skills_opgg(hero_ids):
    """使用 OP.GG API 批量获取所有英雄技能"""
    from opgg import opgg
    from opgg.params import By, LangCode
    import re
    
    def clean_html(text):
        if not text:
            return ''
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    skills_data = {}
    opgg_client = opgg.OPGG()
    
    total = len(hero_ids)
    for i, hero_id in enumerate(hero_ids, 1):
        print(f"[{i}/{total}] 获取英雄 {hero_id} 技能...")
        try:
            champ = await opgg_client.get_champion_by_async(By.ID, hero_id, lang_code=LangCode.CHINESE)
            
            if champ:
                skills = []
                
                if champ.passive:
                    skills.append({
                        'id': 1,
                        'name': f'被动：{champ.passive.name}',
                        'icon': champ.passive.image_url,
                        'description': clean_html(champ.passive.description),
                        'cooldown': [],
                        'cost': [],
                        'range': []
                    })
                
                spell_keys = ['Q', 'W', 'E', 'R']
                for j, spell in enumerate(champ.spells):
                    if j < 4:
                        skills.append({
                            'id': j + 2,
                            'key': spell_keys[j],
                            'name': spell.name,
                            'icon': spell.image_url,
                            'description': clean_html(spell.description),
                            'cooldown': spell.cooldown_burn if hasattr(spell, 'cooldown_burn') else [],
                            'cost': spell.cost_burn if hasattr(spell, 'cost_burn') else [],
                            'range': spell.range_burn if hasattr(spell, 'range_burn') else []
                        })
                
                skills_data[hero_id] = skills
                print(f"  ✓ 成功获取 {len(skills)} 个技能")
            else:
                print(f"  ✗ 未找到英雄")
        except Exception as e:
            print(f"  ✗ 获取失败: {e}")
        
        await asyncio.sleep(0.1)
    
    await opgg_client.close()
    return skills_data

def update_champions_data():
    """更新英雄数据（包含技能）"""
    print("\n📊 Updating champions data...")
    
    detailed_data_path = os.path.join(os.path.dirname(__file__), 'champion_detailed_data.json')
    if not os.path.exists(detailed_data_path):
        print("✗ champion_detailed_data.json not found")
        return None, None
    
    with open(detailed_data_path, 'r', encoding='utf-8') as f:
        champions = json.load(f)
    
    import requests
    try:
        version_resp = requests.get('https://ddragon.leagueoflegends.com/api/versions.json', timeout=5)
        version = version_resp.json()[0]
        
        champ_resp = requests.get(
            f'https://ddragon.leagueoflegends.com/cdn/{version}/data/zh_CN/champion.json',
            timeout=5
        )
        ddragon_data = champ_resp.json()['data']
        
        id_to_ddragon = {}
        for key, champ in ddragon_data.items():
            id_to_ddragon[champ['key']] = champ
        
        heroes = []
        for champ in champions:
            champ_id = str(champ['id'])
            ddragon_champ = id_to_ddragon.get(champ_id, {})
            
            hero = {
                'id': champ['id'],
                'name': ddragon_champ.get('title', champ.get('name', '')),
                'title': ddragon_champ.get('name', champ.get('title', '')),
                'image': f'https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{ddragon_champ.get("id", "")}.png',
                'avgWinRate': champ.get('avgWinRate', 0),
                'avgPickRate': champ.get('avgPickRate', 0),
                'avgBanRate': champ.get('avgBanRate', 0),
                'lanes': champ.get('lanes', []),
                'skills': []
            }
            heroes.append(hero)
        
        print(f"✓ Processed {len(heroes)} champions")
        return heroes, version
        
    except Exception as e:
        print(f"✗ Error updating champions: {e}")
        return None, None

def update_skills_data(heroes):
    """更新技能数据并合并到英雄数据中"""
    print("\n🌀 Updating skills data from OP.GG...")
    
    hero_ids = [hero['id'] for hero in heroes]
    
    try:
        skills_data = asyncio.run(get_all_champions_skills_opgg(hero_ids))
        
        if not skills_data:
            print("✗ No skills data received")
            return heroes
        
        updated_count = 0
        for hero in heroes:
            hero_id = hero['id']
            if hero_id in skills_data:
                hero['skills'] = skills_data[hero_id]
                updated_count += 1
        
        print(f"✓ Updated skills for {updated_count} heroes")
        return heroes
        
    except Exception as e:
        print(f"✗ Error updating skills: {e}")
        return heroes

def update_runes_data():
    """更新符文数据"""
    print("\n🔮 Updating runes data...")
    try:
        runes_data = get_runes_data()
        if runes_data and 'all_runes' in runes_data:
            save_json(runes_data, 'runes.json')
            print(f"✓ Updated {len(runes_data.get('all_runes', []))} runes")
        else:
            print("✗ No runes data received")
    except Exception as e:
        print(f"✗ Error updating runes: {e}")

def update_hero_builds(heroes):
    """更新英雄出装数据"""
    print("\n⚔️  Updating hero builds...")
    
    if not heroes:
        print("✗ No heroes data")
        return
    
    print(f"Found {len(heroes)} heroes")
    
    for i, hero in enumerate(heroes, 1):
        hero_id = hero['id']
        hero_name = hero['name']
        print(f"[{i}/{len(heroes)}] Updating {hero_name} (ID: {hero_id})...")
        
        try:
            raw_data = get_champion_builds(hero_id, 'top', 'emerald_plus')
            build_data = extract_build_data(raw_data)
            if build_data and 'runes' in build_data:
                save_json(build_data, f'hero_{hero_id}_build.json')
                print(f"  ✓ Saved build for {hero_name}")
            else:
                print(f"  ✗ No build data for {hero_name}")
        except Exception as e:
            print(f"  ✗ Error updating {hero_name}: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("LOL Data Updater")
    print("=" * 50)
    
    ensure_data_dir()
    
    heroes, version = update_champions_data()
    
    if heroes and version:
        heroes = update_skills_data(heroes)
        save_json({'heroes': heroes, 'version': version, 'updated': datetime.now().isoformat()}, 'champions.json')
        print(f"\n✓ Saved champions.json with {len(heroes)} heroes")
    
    update_runes_data()
    update_hero_builds(heroes)
    
    print("\n" + "=" * 50)
    print("✓ Update complete!")
    print("=" * 50)

if __name__ == '__main__':
    main()
