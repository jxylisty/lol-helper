const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// 英雄列表数据（将从DDragon API获取）
const heroes = [];

// 英雄数据（将从本地JSON文件获取）
const heroData = {};

// 符文数据（将从本地JSON文件获取）
const runeData = {};

// 对线数据（将从本地JSON文件获取）
const matchupData = {};

let dataInitialized = false;

// 路由
app.get('/api/heroes', (req, res) => {
  if (heroes.length === 0 && !dataInitialized) {
    res.json([]);
  } else {
    res.json(heroes);
  }
});

app.get('/api/hero/:id', async (req, res) => {
  const id = parseInt(req.params.id);
  let hero = heroData[id];
  
  if (hero) {
    if (!hero.skills || hero.skills.length === 0) {
      hero.skills = await getHeroSkills(hero.name, hero.id);
    }
    res.json(hero);
  } else {
    res.status(404).json({ message: 'Hero not found' });
  }
});

function getHeroSkills(heroName, heroId) {
  return new Promise((resolve, reject) => {
    const pythonScriptPath = path.join(__dirname, 'get_champion_skills.py');
    const command = `chcp 65001 >nul && py "${pythonScriptPath}" ${heroId}`;
    
    exec(command, { encoding: 'utf8', timeout: 15000 }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Failed to get skills for ${heroName}:`, error.message);
        resolve(getDefaultSkills(heroName));
        return;
      }
      
      try {
        const data = JSON.parse(stdout);
        if (data.error) {
          console.error(`Python error for ${heroName}:`, data.error);
          resolve(getDefaultSkills(heroName));
          return;
        }
        resolve(data.skills);
      } catch (e) {
        console.error(`Failed to parse skills for ${heroName}:`, e.message);
        resolve(getDefaultSkills(heroName));
      }
    });
  });
}

function getDefaultSkills(heroName) {
  return [
    { id: 1, name: '被动技能', icon: 'https://opgg-static.akamaized.net/meta/images/lol/latest/spell/Passive.png', description: `${heroName}的被动技能` },
    { id: 2, name: 'Q技能', icon: 'https://opgg-static.akamaized.net/meta/images/lol/latest/spell/Q.png', description: `${heroName}的Q技能` },
    { id: 3, name: 'W技能', icon: 'https://opgg-static.akamaized.net/meta/images/lol/latest/spell/W.png', description: `${heroName}的W技能` },
    { id: 4, name: 'E技能', icon: 'https://opgg-static.akamaized.net/meta/images/lol/latest/spell/E.png', description: `${heroName}的E技能` },
    { id: 5, name: 'R技能', icon: 'https://opgg-static.akamaized.net/meta/images/lol/latest/spell/R.png', description: `${heroName}的R技能` }
  ];
}

// 根据段位、比赛类型获取英雄数据
app.get('/api/hero/:id/stats', async (req, res) => {
  const id = parseInt(req.params.id);
  const { tier = 'emerald_plus', queue = 'solo' } = req.query;
  
  try {
    const pythonScriptPath = path.join(__dirname, 'get_champion_stats_by_params.py');
    const command = `py "${pythonScriptPath}" --champion-id ${id} --tier ${tier} --queue ${queue}`;
    
    exec(command, { encoding: 'utf8' }, (error, stdout, stderr) => {
      if (error) {
        console.error('Python script error:', error);
        res.status(500).json({ message: 'Failed to fetch data' });
        return;
      }
      
      try {
        const data = JSON.parse(stdout);
        res.json(data);
      } catch (e) {
        console.error('Failed to parse Python output:', e.message);
        res.status(500).json({ message: 'Failed to parse data' });
      }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// 获取支持的参数选项
app.get('/api/options', (req, res) => {
  res.json({
    regions: [
      { value: 'global', label: '全球' }
    ],
    tiers: [
      { value: 'all', label: '全部段位' },
      { value: 'iron', label: '黑铁' },
      { value: 'bronze', label: '青铜' },
      { value: 'silver', label: '白银' },
      { value: 'gold', label: '黄金' },
      { value: 'platinum', label: '铂金' },
      { value: 'emerald', label: '翡翠' },
      { value: 'diamond', label: '钻石' },
      { value: 'master', label: '大师' },
      { value: 'grandmaster', label: '宗师' },
      { value: 'challenger', label: '王者' },
      { value: 'emerald_plus', label: '翡翠+' },
      { value: 'diamond_plus', label: '钻石+' }
    ],
    queues: [
      { value: 'solo', label: '单排/双排' },
      { value: 'flex', label: '灵活组排' },
      { value: 'aram', label: '大乱斗' }
    ]
  });
});

// 符文数据缓存
let cachedRunes = null;
let runesVersion = null;

// 获取符文数据
app.get('/api/runes', (req, res) => {
  const { refresh } = req.query;
  
  if (refresh === 'true' || !cachedRunes) {
    const pythonScriptPath = path.join(__dirname, 'get_runes_data.py');
    exec(`chcp 65001 >nul && py "${pythonScriptPath}"`, { encoding: 'utf8', timeout: 30000 }, (error, stdout, stderr) => {
      if (error) {
        console.error('Failed to fetch runes:', error.message);
        if (cachedRunes) {
          res.json(cachedRunes);
        } else {
          res.status(500).json({ message: 'Failed to fetch runes data' });
        }
        return;
      }
      
      try {
        const data = JSON.parse(stdout);
        if (data.error) {
          res.status(500).json({ message: data.error });
          return;
        }
        cachedRunes = data;
        runesVersion = data.version;
        console.log(`Runes data updated to version ${runesVersion}, total ${data.all_runes?.length || 0} runes`);
        res.json(cachedRunes);
      } catch (e) {
        console.error('Failed to parse runes data:', e.message);
        res.status(500).json({ message: 'Failed to parse runes data' });
      }
    });
  } else {
    res.json(cachedRunes);
  }
});

app.get('/api/hero/:id/build', (req, res) => {
  const id = parseInt(req.params.id);
  const { position = 'top', tier = 'emerald_plus' } = req.query;
  
  const pythonScriptPath = path.join(__dirname, 'get_champion_builds.py');
  const command = `chcp 65001 >nul && py "${pythonScriptPath}" ${id} ${position} ${tier}`;
  
  exec(command, { encoding: 'utf8', timeout: 20000 }, (error, stdout, stderr) => {
    if (error) {
      console.error('Failed to fetch build:', error.message);
      res.status(500).json({ message: 'Failed to fetch build data' });
      return;
    }
    
    try {
      const data = JSON.parse(stdout);
      if (data.error) {
        res.status(500).json({ message: data.error });
        return;
      }
      res.json(data);
    } catch (e) {
      console.error('Failed to parse build data:', e.message);
      res.status(500).json({ message: 'Failed to parse build data' });
    }
  });
});

app.get('/api/hero/:id/runes', (req, res) => {
  const id = parseInt(req.params.id);
  const runes = runeData[id];
  if (runes) {
    res.json(runes);
  } else {
    res.status(404).json({ message: 'Runes not found' });
  }
});

app.get('/api/hero/:id/matchups', (req, res) => {
  const id = parseInt(req.params.id);
  const matchups = matchupData[id];
  if (matchups) {
    res.json(matchups);
  } else {
    res.status(404).json({ message: 'Matchups not found' });
  }
});

async function loadLocalDataFast() {
  console.log('Fast loading local data...');
  
  const detailedDataPath = path.join(__dirname, 'champion_detailed_data.json');
  
  if (fs.existsSync(detailedDataPath)) {
    try {
      let idToChampion = {};
      
      try {
        const versionResponse = await axios.get('https://ddragon.leagueoflegends.com/api/versions.json', { timeout: 3000 });
        const version = versionResponse.data[0];
        const championsResponse = await axios.get(`https://ddragon.leagueoflegends.com/cdn/${version}/data/zh_CN/champion.json`, { timeout: 5000 });
        const championsData = championsResponse.data.data;
        
        for (const key in championsData) {
          const champ = championsData[key];
          idToChampion[champ.key] = champ;
        }
        console.log('Loaded DDragon name mapping, sample keys:', Object.keys(idToChampion).slice(0, 5));
      } catch (e) {
        console.log('Failed to load DDragon mapping, using fallback');
      }
      
      const fileContent = fs.readFileSync(detailedDataPath, 'utf8');
      const realData = JSON.parse(fileContent);
      
      realData.forEach(champ => {
        const ddragonChamp = idToChampion[String(champ.id)];
        const englishName = ddragonChamp ? ddragonChamp.id : champ.name;
        const heroName = ddragonChamp ? ddragonChamp.title : champ.name;
        const heroTitle = ddragonChamp ? ddragonChamp.name : (champ.title || '');
        const imageUrl = `https://ddragon.leagueoflegends.com/cdn/16.6.1/img/champion/${englishName}.png`;
        
        heroData[champ.id] = {
          id: champ.id,
          name: heroName,
          title: heroTitle,
          image: imageUrl,
          avgWinRate: champ.avgWinRate || 0,
          avgPickRate: champ.avgPickRate || 0,
          avgBanRate: champ.avgBanRate || 0,
          totalPlay: champ.totalPlay || 0,
          lanes: champ.lanes || [],
          skills: []
        };
        
        heroes.push({
          id: champ.id,
          name: heroName,
          title: heroTitle,
          image: imageUrl,
          lanes: champ.lanes || []
        });
      });
      
      dataInitialized = true;
      console.log(`Fast load complete. Total heroes: ${heroes.length}`);
      return true;
    } catch (e) {
      console.error('Failed to fast load:', e.message);
    }
  }
  return false;
}

async function loadDDragonDataInBackground() {
  try {
    console.log('Loading DDragon data in background...');
    const ddragonResponse = await axios.get('https://ddragon.leagueoflegends.com/api/versions.json');
    const latestVersion = ddragonResponse.data[0];
    
    const championsResponse = await axios.get(`https://ddragon.leagueoflegends.com/cdn/${latestVersion}/data/zh_CN/champion.json`);
    const championsData = championsResponse.data.data;
    
    for (const key in championsData) {
      const champion = championsData[key];
      const id = champion.key;
      
      if (heroData[parseInt(id)]) {
        heroData[parseInt(id)].name = champion.name;
        heroData[parseInt(id)].title = champion.title;
        heroData[parseInt(id)].image = `https://ddragon.leagueoflegends.com/cdn/${latestVersion}/img/champion/${champion.image.full}`;
      }
      
      const heroIndex = heroes.findIndex(h => h.id == id);
      if (heroIndex !== -1) {
        heroes[heroIndex].name = champion.name;
        heroes[heroIndex].title = champion.title;
        heroes[heroIndex].image = `https://ddragon.leagueoflegends.com/cdn/${latestVersion}/img/champion/${champion.image.full}`;
      }
    }
    console.log('DDragon data loaded in background');
  } catch (error) {
    console.error('Failed to load DDragon data:', error.message);
  }
}

// 初始化数据函数（从本地JSON加载数据）
async function initializeData() {
  const fastLoaded = await loadLocalDataFast();
  
  if (fastLoaded) {
    loadDDragonDataInBackground();
    return;
  }
  
  try {
    console.log('Initializing data from DDragon API...');
    
    const ddragonResponse = await axios.get('https://ddragon.leagueoflegends.com/api/versions.json');
    const latestVersion = ddragonResponse.data[0];
    
    const championsResponse = await axios.get(`https://ddragon.leagueoflegends.com/cdn/${latestVersion}/data/zh_CN/champion.json`);
    const championsData = championsResponse.data.data;
    
    const champions = [];
    
    for (const key in championsData) {
      const champion = championsData[key];
      champions.push({
        id: champion.key,
        name: champion.name,
        title: champion.title,
        image: `https://ddragon.leagueoflegends.com/cdn/${latestVersion}/img/champion/${champion.image.full}`
      });
    }
    
    console.log(`Found ${champions.length} champions from DDragon API`);
    
    let realData = null;
    const detailedDataPath = path.join(__dirname, 'champion_detailed_data.json');
    const localDataPath = path.join(__dirname, 'champion_data.json');
    
    if (fs.existsSync(detailedDataPath)) {
      try {
        const fileContent = fs.readFileSync(detailedDataPath, 'utf8');
        realData = JSON.parse(fileContent);
        console.log(`Loaded ${realData.length} champions from detailed JSON file`);
      } catch (e) {
        console.error('Failed to load detailed JSON file:', e.message);
      }
    }
    
    if (!realData && fs.existsSync(localDataPath)) {
      try {
        const fileContent = fs.readFileSync(localDataPath, 'utf8');
        realData = JSON.parse(fileContent);
        console.log(`Loaded ${realData.length} champions from basic JSON file`);
      } catch (e) {
        console.error('Failed to load basic JSON file:', e.message);
      }
    }
    
    // 3. 如果没有本地文件，尝试使用Python脚本获取
    if (!realData) {
      try {
        console.log('No local data found, attempting to get real data from OPGG API using Python...');
        const pythonScriptPath = path.join(__dirname, 'get_detailed_champion_data.py');
        
        realData = await new Promise((resolve, reject) => {
          exec(`py "${pythonScriptPath}"`, { encoding: 'utf8' }, (error, stdout, stderr) => {
            console.log('Python script stdout length:', stdout.length);
            console.log('Python script stderr:', stderr);
            
            if (error) {
              console.error('Python script error:', error);
              reject(error);
              return;
            }
            
            if (!stdout || stdout.trim() === '') {
              console.error('Python script returned empty output');
              reject(new Error('Empty output'));
              return;
            }
            
            try {
              const data = JSON.parse(stdout);
              console.log(`Successfully parsed ${data.length} champions from Python script`);
              resolve(data);
            } catch (e) {
              console.error('Failed to parse Python output:', e.message);
              console.error('First 200 chars of output:', stdout.substring(0, 200));
              reject(e);
            }
          });
        });
      } catch (error) {
        console.error('Failed to get real data from OPGG API:', error.message);
      }
    }
    
    // 4. 如果有真实数据，合并到heroData中
    if (realData) {
      
      // 创建英雄ID到DDragon英雄的映射
      const idToChampion = {};
      champions.forEach(champion => {
        idToChampion[champion.id] = champion;
      });
      
      // 合并真实数据和DDragon数据（使用ID匹配）
      console.log(`Merging ${realData.length} real champions with ${champions.length} DDragon champions...`);
      let matchedCount = 0;
      
      realData.forEach(realChampion => {
          const ddragonChampion = idToChampion[realChampion.id];
          if (ddragonChampion) {
            heroData[ddragonChampion.id] = {
              id: ddragonChampion.id,
              name: ddragonChampion.name,
              title: ddragonChampion.title,
              image: ddragonChampion.image,
              // 使用新的数据结构
              avgWinRate: realChampion.avgWinRate || realChampion.winRate,
              avgPickRate: realChampion.avgPickRate || realChampion.pickRate,
              avgBanRate: realChampion.avgBanRate || realChampion.banRate,
              totalPlay: realChampion.totalPlay || 0,
              lanes: realChampion.lanes || [],
              skills: []
            };
            
            // 更新符文数据
            if (realChampion.runes) {
              runeData[ddragonChampion.id] = realChampion.runes;
            }
            
            matchedCount++;
            console.log(`Updated data for ${ddragonChampion.name}: Avg Win Rate ${realChampion.avgWinRate || realChampion.winRate}%, Lanes: ${(realChampion.lanes || []).length}`);
          } else {
            console.log(`No match found for champion ID ${realChampion.id} (${realChampion.name})`);
          }
        });
      
      console.log(`Successfully matched ${matchedCount} out of ${realData.length} real champions`);
      
    } else {
      console.log('No real data available and no local JSON file found');
    }
    
    heroes.length = 0;
    if (realData) {
      champions.forEach(champion => {
        const realChampion = realData.find(r => r.id == champion.id);
        heroes.push({
          id: champion.id,
          name: champion.name,
          title: champion.title,
          image: champion.image,
          lanes: realChampion ? realChampion.lanes : []
        });
      });
    } else {
      champions.forEach(champion => {
        heroes.push(champion);
      });
    }
    
    dataInitialized = true;
    console.log(`Data initialization complete. Total heroes: ${heroes.length}`);
    
  } catch (error) {
    console.error('Error initializing data:', error);
  }
}

// 定期爬取数据（已禁用，数据从本地JSON文件获取）
// setInterval(crawlOPGG, 24 * 60 * 60 * 1000);

// 初始数据加载并启动服务器
// 先启动服务器，再初始化数据
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  initializeData().catch(err => {
    console.error('Failed to initialize data:', err);
  });
});