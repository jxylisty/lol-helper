import requests
import json
import sys

def get_champion_builds(champion_id, position="top", tier="emerald_plus", region="global", mode="ranked"):
    url = f"https://lol-api-champion.op.gg/api/{region}/champions/{mode}/{champion_id}/{position}"
    params = {"tier": tier}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def extract_build_data(data):
    if "error" in data:
        return data
    
    result = data.get("data", {})
    
    build_data = {
        "version": data.get("meta", {}).get("version", ""),
        
        "summoner_spells": [],
        "runes": [],
        "skills": [],
        "skill_order": [],
        "items": {
            "starter": [],
            "core": [],
            "boots": [],
            "last": []
        },
        "counters": []
    }
    
    for spell in result.get("summoner_spells", [])[:3]:
        build_data["summoner_spells"].append({
            "ids": spell.get("ids", []),
            "win_rate": round(spell.get("win", 0) / spell.get("play", 1) * 100, 2) if spell.get("play", 0) > 0 else 0,
            "pick_rate": round(spell.get("pick_rate", 0) * 100, 2),
            "play": spell.get("play", 0)
        })
    
    for rune in result.get("runes", [])[:5]:
        build_data["runes"].append({
            "primary_page_id": rune.get("primary_page_id"),
            "primary_rune_ids": rune.get("primary_rune_ids", []),
            "secondary_page_id": rune.get("secondary_page_id"),
            "secondary_rune_ids": rune.get("secondary_rune_ids", []),
            "stat_mod_ids": rune.get("stat_mod_ids", []),
            "win_rate": round(rune.get("win", 0) / rune.get("play", 1) * 100, 2) if rune.get("play", 0) > 0 else 0,
            "pick_rate": round(rune.get("pick_rate", 0) * 100, 2),
            "play": rune.get("play", 0)
        })
    
    for mastery in result.get("skill_masteries", [])[:3]:
        build_data["skill_order"].append({
            "priority": mastery.get("ids", []),
            "win_rate": round(mastery.get("win", 0) / mastery.get("play", 1) * 100, 2) if mastery.get("play", 0) > 0 else 0,
            "pick_rate": round(mastery.get("pick_rate", 0) * 100, 2),
            "play": mastery.get("play", 0)
        })
    
    for skill in result.get("skills", [])[:3]:
        build_data["skills"].append({
            "order": skill.get("order", []),
            "win_rate": round(skill.get("win", 0) / skill.get("play", 1) * 100, 2) if skill.get("play", 0) > 0 else 0,
            "pick_rate": round(skill.get("pick_rate", 0) * 100, 2),
            "play": skill.get("play", 0)
        })
    
    for item in result.get("starter_items", [])[:3]:
        build_data["items"]["starter"].append({
            "ids": item.get("ids", []),
            "win_rate": round(item.get("win", 0) / item.get("play", 1) * 100, 2) if item.get("play", 0) > 0 else 0,
            "pick_rate": round(item.get("pick_rate", 0) * 100, 2),
            "play": item.get("play", 0)
        })
    
    for item in result.get("core_items", [])[:5]:
        build_data["items"]["core"].append({
            "ids": item.get("ids", []),
            "win_rate": round(item.get("win", 0) / item.get("play", 1) * 100, 2) if item.get("play", 0) > 0 else 0,
            "pick_rate": round(item.get("pick_rate", 0) * 100, 2),
            "play": item.get("play", 0)
        })
    
    for item in result.get("boots", [])[:3]:
        build_data["items"]["boots"].append({
            "ids": item.get("ids", []),
            "win_rate": round(item.get("win", 0) / item.get("play", 1) * 100, 2) if item.get("play", 0) > 0 else 0,
            "pick_rate": round(item.get("pick_rate", 0) * 100, 2),
            "play": item.get("play", 0)
        })
    
    for item in result.get("last_items", [])[:5]:
        build_data["items"]["last"].append({
            "ids": item.get("ids", []),
            "win_rate": round(item.get("win", 0) / item.get("play", 1) * 100, 2) if item.get("play", 0) > 0 else 0,
            "pick_rate": round(item.get("pick_rate", 0) * 100, 2),
            "play": item.get("play", 0)
        })
    
    for counter in result.get("counters", []):
        build_data["counters"].append({
            "champion_id": counter.get("champion_id"),
            "play": counter.get("play", 0),
            "win": counter.get("win", 0),
            "win_rate": round(counter.get("win", 0) / counter.get("play", 1) * 100, 2) if counter.get("play", 0) > 0 else 0
        })
    
    return build_data

if __name__ == "__main__":
    champion_id = int(sys.argv[1]) if len(sys.argv) > 1 else 86
    position = sys.argv[2] if len(sys.argv) > 2 else "top"
    tier = sys.argv[3] if len(sys.argv) > 3 else "emerald_plus"
    
    data = get_champion_builds(champion_id, position, tier)
    build_data = extract_build_data(data)
    
    print(json.dumps(build_data, ensure_ascii=False))
