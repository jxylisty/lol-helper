<template>
	<view class="container">
		<view v-if="loading" class="loading">加载中...</view>
		<view v-else-if="error" class="error">{{ error }}</view>
		<view v-else>
			<view class="rune-header">
				<text class="rune-title">推荐符文</text>
				<text class="rune-version">版本: {{ buildData.version }}</text>
			</view>
			
			<view class="rune-tabs">
				<view 
					v-for="(rune, index) in buildData.runes" 
					:key="index"
					class="rune-tab"
					:class="{ active: selectedRuneIndex === index }"
					@click="selectRune(index)"
				>
					<text class="tab-win-rate">胜率: {{ rune.win_rate }}%</text>
					<text class="tab-pick-rate">登场: {{ rune.pick_rate }}%</text>
				</view>
			</view>
			
			<view v-if="currentRune" class="rune-content">
				<view class="rune-main">
					<view class="rune-path-header">
						<image :src="getTreeIcon(currentRune.primary_page_id)" class="rune-path-icon" />
						<text class="rune-path-name">{{ getTreeName(currentRune.primary_page_id) }}</text>
					</view>
					<view class="rune-slots">
						<view 
							v-for="(runeId, index) in currentRune.primary_rune_ids" 
							:key="index"
							class="rune-slot"
							:class="{ keystone: index === 0 }"
							@click="showRuneDetail(runeId)"
						>
							<image :src="getRuneIcon(runeId)" class="rune-icon" />
							<text class="rune-name">{{ getRuneName(runeId) }}</text>
						</view>
					</view>
				</view>
				
				<view class="rune-secondary">
					<view class="rune-path-header">
						<image :src="getTreeIcon(currentRune.secondary_page_id)" class="rune-path-icon" />
						<text class="rune-path-name">{{ getTreeName(currentRune.secondary_page_id) }}</text>
					</view>
					<view class="rune-slots">
						<view 
							v-for="(runeId, index) in currentRune.secondary_rune_ids" 
							:key="index"
							class="rune-slot"
							@click="showRuneDetail(runeId)"
						>
							<image :src="getRuneIcon(runeId)" class="rune-icon" />
							<text class="rune-name">{{ getRuneName(runeId) }}</text>
						</view>
					</view>
				</view>
				
				<view class="rune-shards">
					<text class="shard-title">属性碎片</text>
					<view class="shard-slots">
						<view 
							v-for="(shardId, index) in currentRune.stat_mod_ids" 
							:key="index"
							class="shard-slot"
						>
							<text class="shard-icon">{{ getShardIcon(shardId) }}</text>
							<text class="shard-name">{{ getShardName(shardId) }}</text>
						</view>
					</view>
				</view>
			</view>
			
			<view class="summoner-spells">
				<text class="section-title">召唤师技能</text>
				<view class="spell-list">
					<view 
						v-for="(spell, index) in buildData.summoner_spells" 
						:key="index"
						class="spell-item"
					>
						<view class="spell-icons">
							<image 
								v-for="spellId in spell.ids" 
								:key="spellId"
								:src="getSpellIcon(spellId)" 
								class="spell-icon" 
							/>
						</view>
						<view class="spell-stats">
							<text class="spell-win-rate">胜率: {{ spell.win_rate }}%</text>
							<text class="spell-pick-rate">登场: {{ spell.pick_rate }}%</text>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<view v-if="showDetail" class="rune-detail-modal" @click="closeDetail">
			<view class="rune-detail-content" @click.stop>
				<view class="detail-header">
					<image :src="selectedRuneDetail.icon" class="detail-icon" />
					<text class="detail-name">{{ selectedRuneDetail.name }}</text>
				</view>
				<text class="detail-desc">{{ selectedRuneDetail.longDesc || selectedRuneDetail.shortDesc }}</text>
				<view class="detail-close" @click="closeDetail">
					<text>关闭</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
const CACHE_DURATION = 24 * 60 * 60 * 1000;

export default {
	data() {
		return {
			heroId: 0,
			buildData: {
				version: '',
				runes: [],
				summoner_spells: []
			},
			runeData: {
				trees: [],
				all_runes: []
			},
			selectedRuneIndex: 0,
			loading: true,
			error: '',
			showDetail: false,
			selectedRuneDetail: {}
		}
	},
	computed: {
		currentRune() {
			return this.buildData.runes[this.selectedRuneIndex] || null;
		}
	},
	onLoad(options) {
		this.heroId = options.id;
		this.fetchData();
	},
	methods: {
		async fetchData() {
			const cachedRunes = this.getCache('runeData');
			const cachedBuild = this.getCache(`build_${this.heroId}`);
			
			if (cachedRunes && cachedRunes.data) {
				this.runeData = cachedRunes.data;
			}
			if (cachedBuild && cachedBuild.data) {
				this.buildData = cachedBuild.data;
				this.loading = false;
			}
			
			try {
				await Promise.all([
					this.fetchRuneData(cachedRunes),
					this.fetchBuild(cachedBuild)
				]);
				
				if (!cachedBuild) {
					this.loading = false;
				}
			} catch (err) {
				console.error('Failed to fetch data:', err);
				if (!cachedBuild) {
					this.error = '加载失败，请重试';
					this.loading = false;
				}
			}
		},
		
		getCache(key) {
			try {
				const cached = uni.getStorageSync(key);
				if (cached && cached.timestamp) {
					return cached;
				}
			} catch (e) {
				console.error('Cache read error:', e);
			}
			return null;
		},
		
		setCache(key, data) {
			try {
				uni.setStorageSync(key, {
					data: data,
					timestamp: Date.now()
				});
			} catch (e) {
				console.error('Cache write error:', e);
			}
		},
		
		isCacheValid(cached) {
			if (!cached || !cached.timestamp) return false;
			return Date.now() - cached.timestamp < CACHE_DURATION;
		},
		
		fetchRuneData(cached) {
			if (cached && this.isCacheValid(cached)) {
				return Promise.resolve(cached.data);
			}
			
			return new Promise((resolve, reject) => {
				uni.request({
					url: 'https://myasw.pythonanywhere.com/api/runes',
					method: 'GET',
					success: (res) => {
						if (res.statusCode === 200 && res.data.all_runes) {
							this.runeData = res.data;
							this.setCache('runeData', res.data);
							resolve(res.data);
						} else {
							reject(new Error('Failed to fetch runes'));
						}
					},
					fail: reject
				});
			});
		},
		
		fetchBuild(cached) {
			if (cached && this.isCacheValid(cached)) {
				return Promise.resolve(cached.data);
			}
			
			return new Promise((resolve, reject) => {
				uni.request({
					url: `https://myasw.pythonanywhere.com/api/hero/${this.heroId}/build`,
					method: 'GET',
					success: (res) => {
						if (res.statusCode === 200 && res.data.runes) {
							this.buildData = res.data;
							this.setCache(`build_${this.heroId}`, res.data);
							resolve(res.data);
						} else {
							reject(new Error('Failed to fetch build'));
						}
					},
					fail: reject
				});
			});
		},
		
		selectRune(index) {
			this.selectedRuneIndex = index;
		},
		
		getTreeName(treeId) {
			const treeNames = {
				8000: '精密',
				8100: '主宰',
				8200: '巫术',
				8400: '坚决',
				8300: '启迪'
			};
			return treeNames[treeId] || '未知';
		},
		
		getTreeIcon(treeId) {
			const tree = this.runeData.trees.find(t => t.id === treeId);
			return tree ? tree.icon : '';
		},
		
		getRuneInfo(runeId) {
			return this.runeData.all_runes.find(r => r.id === runeId) || {};
		},
		
		getRuneName(runeId) {
			const rune = this.getRuneInfo(runeId);
			return rune.name || '未知';
		},
		
		getRuneIcon(runeId) {
			const rune = this.getRuneInfo(runeId);
			return rune.icon || '';
		},
		
		getShardName(shardId) {
			const shardNames = {
				5001: '生命值',
				5002: '护甲',
				5003: '魔抗',
				5005: '攻击速度',
				5007: '技能急速',
				5008: '适应之力',
				5010: '移速',
				5011: '生命回复',
				5013: '韧性'
			};
			return shardNames[shardId] || '未知';
		},
		
		getShardIcon(shardId) {
			const shardIcons = {
				5001: '❤️',
				5002: '🛡️',
				5003: '🔮',
				5005: '⚔️',
				5007: '⚡',
				5008: '💪',
				5010: '🏃',
				5011: '💚',
				5013: '🧱'
			};
			return shardIcons[shardId] || '◆';
		},
		
		getSpellIcon(spellId) {
			return `https://ddragon.leagueoflegends.com/cdn/16.6.1/img/spell/Summoner${this.getSpellName(spellId)}.png`;
		},
		
		getSpellName(spellId) {
			const spellNames = {
				1: 'Cleanse',
				3: 'Exhaust',
				4: 'Flash',
				6: 'Ghost',
				7: 'Heal',
				11: 'Smite',
				12: 'Teleport',
				13: 'Clarity',
				14: 'Ignite',
				21: 'Barrier',
				32: 'Mark',
				54: 'Placeholder'
			};
			return spellNames[spellId] || 'Flash';
		},
		
		showRuneDetail(runeId) {
			const rune = this.getRuneInfo(runeId);
			this.selectedRuneDetail = rune;
			this.showDetail = true;
		},
		
		closeDetail() {
			this.showDetail = false;
		}
	}
}
</script>

<style scoped>
.container {
	padding: 20rpx;
	background-color: #f5f5f5;
	min-height: 100vh;
}

.loading, .error {
	text-align: center;
	padding: 100rpx 0;
	font-size: 28rpx;
	color: #666;
}

.error {
	color: #ff4d4f;
}

.rune-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	margin-bottom: 20rpx;
}

.rune-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.rune-version {
	font-size: 24rpx;
	color: #999;
}

.rune-tabs {
	display: flex;
	gap: 15rpx;
	margin-bottom: 20rpx;
	overflow-x: auto;
	padding-bottom: 10rpx;
}

.rune-tab {
	flex-shrink: 0;
	padding: 15rpx 25rpx;
	background-color: white;
	border-radius: 10rpx;
	border: 2rpx solid #e8e8e8;
}

.rune-tab.active {
	border-color: #1890ff;
	background-color: #e6f7ff;
}

.tab-win-rate {
	display: block;
	font-size: 24rpx;
	font-weight: bold;
	color: #1890ff;
}

.tab-pick-rate {
	display: block;
	font-size: 20rpx;
	color: #999;
	margin-top: 5rpx;
}

.rune-content {
	background-color: white;
	border-radius: 10rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
}

.rune-main, .rune-secondary {
	margin-bottom: 25rpx;
}

.rune-path-header {
	display: flex;
	align-items: center;
	margin-bottom: 15rpx;
	padding: 10rpx 15rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
	width: fit-content;
}

.rune-path-icon {
	width: 36rpx;
	height: 36rpx;
	margin-right: 10rpx;
}

.rune-path-name {
	font-size: 26rpx;
	font-weight: bold;
	color: #333;
}

.rune-slots {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.rune-slot {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 90rpx;
	padding: 12rpx;
	background-color: #fafafa;
	border-radius: 10rpx;
	border: 2rpx solid #e8e8e8;
}

.rune-slot.keystone {
	background-color: #fff7e6;
	border-color: #ffd591;
}

.rune-icon {
	width: 48rpx;
	height: 48rpx;
	margin-bottom: 8rpx;
}

.rune-name {
	font-size: 18rpx;
	text-align: center;
	color: #333;
	line-height: 1.2;
}

.rune-shards {
	padding-top: 15rpx;
	border-top: 1rpx solid #e8e8e8;
}

.shard-title {
	font-size: 24rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 15rpx;
	display: block;
}

.shard-slots {
	display: flex;
	gap: 15rpx;
}

.shard-slot {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 80rpx;
	padding: 10rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
}

.shard-icon {
	font-size: 28rpx;
	margin-bottom: 5rpx;
}

.shard-name {
	font-size: 16rpx;
	text-align: center;
	color: #666;
}

.summoner-spells {
	background-color: white;
	border-radius: 10rpx;
	padding: 20rpx;
}

.section-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 15rpx;
	display: block;
}

.spell-list {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.spell-item {
	display: flex;
	align-items: center;
	padding: 15rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
}

.spell-icons {
	display: flex;
	gap: 10rpx;
	margin-right: 20rpx;
}

.spell-icon {
	width: 50rpx;
	height: 50rpx;
	border-radius: 8rpx;
}

.spell-stats {
	display: flex;
	flex-direction: column;
}

.spell-win-rate {
	font-size: 24rpx;
	font-weight: bold;
	color: #1890ff;
}

.spell-pick-rate {
	font-size: 20rpx;
	color: #999;
}

.rune-detail-modal {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.rune-detail-content {
	width: 85%;
	max-width: 600rpx;
	background-color: white;
	border-radius: 15rpx;
	padding: 30rpx;
}

.detail-header {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.detail-icon {
	width: 60rpx;
	height: 60rpx;
	margin-right: 15rpx;
}

.detail-name {
	font-size: 30rpx;
	font-weight: bold;
	color: #333;
}

.detail-desc {
	font-size: 24rpx;
	color: #666;
	line-height: 1.6;
	margin-bottom: 25rpx;
}

.detail-close {
	text-align: center;
	padding: 15rpx;
	background-color: #1890ff;
	border-radius: 8rpx;
	color: white;
	font-size: 26rpx;
}
</style>
