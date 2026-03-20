import asyncio
import json
import sys
import io
import re
from opgg import opgg
from opgg.params import By, LangCode

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_html(text):
    if not text:
        return ''
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    
    return text.strip()

async def get_champion_skills(champion_id):
    try:
        opgg_client = opgg.OPGG()
        champ = await opgg_client.get_champion_by_async(By.ID, champion_id, lang_code=LangCode.CHINESE)
        
        if not champ:
            print(json.dumps({'error': 'Champion not found'}, ensure_ascii=False))
            return
        
        skills = []
        
        if champ.passive:
            skills.append({
                'id': 1,
                'name': f'被动：{champ.passive.name}',
                'icon': champ.passive.image_url,
                'description': clean_html(champ.passive.description),
                'tooltip': clean_html(getattr(champ.passive, 'tooltip', '')) if hasattr(champ.passive, 'tooltip') else ''
            })
        
        spell_keys = ['Q', 'W', 'E', 'R']
        for i, spell in enumerate(champ.spells):
            if i < 4:
                skills.append({
                    'id': i + 2,
                    'key': spell_keys[i],
                    'name': spell.name,
                    'icon': spell.image_url,
                    'description': clean_html(spell.description),
                    'tooltip': clean_html(spell.tooltip) if hasattr(spell, 'tooltip') and spell.tooltip else '',
                    'cooldown': spell.cooldown_burn if hasattr(spell, 'cooldown_burn') else [],
                    'cost': spell.cost_burn if hasattr(spell, 'cost_burn') else [],
                    'range': spell.range_burn if hasattr(spell, 'range_burn') else [],
                    'maxRank': spell.max_rank if hasattr(spell, 'max_rank') else 5
                })
        
        result = {
            'id': champion_id,
            'name': champ.name,
            'skills': skills
        }
        
        print(json.dumps(result, ensure_ascii=False))
        await opgg_client.close()
        
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))

if __name__ == '__main__':
    champion_id = int(sys.argv[1]) if len(sys.argv) > 1 else 86
    asyncio.run(get_champion_skills(champion_id))
