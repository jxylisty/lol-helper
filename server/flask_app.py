from flask import Flask, jsonify, send_file, make_response
import json
import os

app = Flask(__name__)

# 手动添加 CORS 支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHAMPIONS_FILE = os.path.join(DATA_DIR, 'champions.json')
RUNES_FILE = os.path.join(DATA_DIR, 'runes.json')

def load_json_file(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

@app.route('/api/heroes', methods=['GET'])
def get_heroes():
    """获取英雄列表"""
    data = load_json_file(CHAMPIONS_FILE)
    if data:
        return jsonify(data.get('heroes', []))
    return jsonify([]), 404

@app.route('/api/hero/<hero_id>', methods=['GET'])
def get_hero_detail(hero_id):
    """获取英雄详情"""
    data = load_json_file(CHAMPIONS_FILE)
    if data:
        heroes = data.get('heroes', [])
        hero = next((h for h in heroes if str(h.get('id')) == str(hero_id)), None)
        if hero:
            return jsonify(hero)
    return jsonify({'error': 'Hero not found'}), 404

@app.route('/api/hero/<hero_id>/build', methods=['GET'])
def get_hero_build(hero_id):
    """获取英雄出装符文"""
    # 从缓存文件读取
    build_file = os.path.join(DATA_DIR, f'hero_{hero_id}_build.json')
    data = load_json_file(build_file)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Build data not found'}), 404

@app.route('/api/hero/<hero_id>/stats', methods=['GET'])
def get_hero_stats(hero_id):
    """获取英雄统计数据"""
    data = load_json_file(CHAMPIONS_FILE)
    if data:
        heroes = data.get('heroes', [])
        hero = next((h for h in heroes if str(h.get('id')) == str(hero_id)), None)
        if hero:
            return jsonify({
                'winRate': hero.get('avgWinRate', 0),
                'pickRate': hero.get('avgPickRate', 0),
                'banRate': hero.get('avgBanRate', 0)
            })
    return jsonify({'error': 'Stats not found'}), 404

@app.route('/api/runes', methods=['GET'])
def get_runes():
    """获取符文数据"""
    data = load_json_file(RUNES_FILE)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Runes data not found'}), 404

@app.route('/api/options', methods=['GET'])
def get_options():
    """获取选项数据（分段、队列等）"""
    return jsonify({
        'tiers': [
            {'name': 'Challenger', 'label': '王者'},
            {'name': 'Grandmaster', 'label': '宗师'},
            {'name': 'Master', 'label': '大师'},
            {'name': 'Diamond', 'label': '钻石'},
            {'name': 'Platinum', 'label': '铂金'},
            {'name': 'Gold', 'label': '黄金'},
            {'name': 'Silver', 'label': '白银'},
            {'name': 'Bronze', 'label': '青铜'},
            {'name': 'Iron', 'label': '黑铁'},
            {'name': 'emerald_plus', 'label': '翡翠+'}
        ],
        'queues': [
            {'name': 'ranked_solo_5x5', 'label': '单排'},
            {'name': 'ranked_flex_sr', 'label': '组排'}
        ]
    })

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
