<template>
	<view class="container">
		<view v-if="loading" class="loading">加载中...</view>
		<view v-else-if="error" class="error">{{ error }}</view>
		<view v-else>
			<view class="matchup-header">
				<text class="matchup-title">对线数据</text>
				<text class="matchup-version">版本: {{ buildData.version }}</text>
			</view>
			
			<view class="matchup-tabs">
				<view 
					class="matchup-tab"
					:class="{ active: activeTab === 'counters' }"
					@click="activeTab = 'counters'"
				>
					克制我的英雄
				</view>
				<view 
					class="matchup-tab"
					:class="{ active: activeTab === 'strong' }"
					@click="activeTab = 'strong'"
				>
					我克制的英雄
				</view>
			</view>
			
			<view class="matchup-list" v-if="displayCounters.length > 0">
				<view 
					v-for="counter in displayCounters" 
					:key="counter.champion_id"
					class="matchup-item"
				>
					<view class="matchup-hero">
						<image :src="getHeroImage(counter.champion_id)" class="hero-image" />
						<text class="hero-name">{{ getHeroName(counter.champion_id) }}</text>
					</view>
					<view class="matchup-stats">
						<view class="stat-row">
							<text class="stat-label">胜率</text>
							<text class="stat-value" :class="getWinRateClass(counter.win_rate)">
								{{ counter.win_rate }}%
							</text>
						</view>
						<view class="stat-row">
							<text class="stat-label">对局数</text>
							<text class="stat-value">{{ counter.play }}</text>
						</view>
						<view class="stat-row">
							<text class="stat-label">胜场</text>
							<text class="stat-value">{{ counter.win }}</text>
						</view>
					</view>
					<view class="win-rate-bar">
						<view class="bar-fill" :style="{ width: counter.win_rate + '%' }"></view>
					</view>
				</view>
			</view>
			
			<view v-else class="no-data">
				<text>暂无对线数据</text>
			</view>
			
			<view class="items-section" v-if="buildData.items && buildData.items.core && buildData.items.core.length > 0">
				<text class="section-title">推荐装备</text>
				
				<view class="item-category" v-if="buildData.items.starter && buildData.items.starter.length > 0">
					<text class="category-title">起始装备</text>
					<view class="item-list">
						<view 
							v-for="(item, index) in buildData.items.starter" 
							:key="index"
							class="item-card"
						>
							<view class="item-icons">
								<image 
									v-for="itemId in item.ids" 
									:key="itemId"
									:src="getItemIcon(itemId)" 
									class="item-icon" 
								/>
							</view>
							<view class="item-stats">
								<text class="item-win-rate">胜率: {{ item.win_rate }}%</text>
								<text class="item-pick-rate">登场: {{ item.pick_rate }}%</text>
							</view>
						</view>
					</view>
				</view>
				
				<view class="item-category" v-if="buildData.items.core && buildData.items.core.length > 0">
					<text class="category-title">核心装备</text>
					<view class="item-list">
						<view 
							v-for="(item, index) in buildData.items.core" 
							:key="index"
							class="item-card"
						>
							<view class="item-icons">
								<image 
									v-for="itemId in item.ids" 
									:key="itemId"
									:src="getItemIcon(itemId)" 
									class="item-icon" 
								/>
							</view>
							<view class="item-stats">
								<text class="item-win-rate">胜率: {{ item.win_rate }}%</text>
								<text class="item-pick-rate">登场: {{ item.pick_rate }}%</text>
							</view>
						</view>
					</view>
				</view>
				
				<view class="item-category" v-if="buildData.items.boots && buildData.items.boots.length > 0">
					<text class="category-title">鞋子</text>
					<view class="item-list">
						<view 
							v-for="(item, index) in buildData.items.boots" 
							:key="index"
							class="item-card"
						>
							<view class="item-icons">
								<image 
									v-for="itemId in item.ids" 
									:key="itemId"
									:src="getItemIcon(itemId)" 
									class="item-icon" 
								/>
							</view>
							<view class="item-stats">
								<text class="item-win-rate">胜率: {{ item.win_rate }}%</text>
								<text class="item-pick-rate">登场: {{ item.pick_rate }}%</text>
							</view>
						</view>
					</view>
				</view>
				
				<view class="item-category" v-if="buildData.items.last && buildData.items.last.length > 0">
					<text class="category-title">后期装备</text>
					<view class="item-list">
						<view 
							v-for="(item, index) in buildData.items.last" 
							:key="index"
							class="item-card"
						>
							<view class="item-icons">
								<image 
									v-for="itemId in item.ids" 
									:key="itemId"
									:src="getItemIcon(itemId)" 
									class="item-icon" 
								/>
							</view>
							<view class="item-stats">
								<text class="item-win-rate">胜率: {{ item.win_rate }}%</text>
								<text class="item-pick-rate">登场: {{ item.pick_rate }}%</text>
							</view>
						</view>
					</view>
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
				counters: [],
				items: {
					starter: [],
					core: [],
					boots: [],
					last: []
				}
			},
			heroList: [],
			activeTab: 'counters',
			loading: true,
			error: ''
		}
	},
	computed: {
		displayCounters() {
			if (this.activeTab === 'counters') {
				return this.buildData.counters.filter(c => c.win_rate < 50).sort((a, b) => a.win_rate - b.win_rate);
			} else {
				return this.buildData.counters.filter(c => c.win_rate >= 50).sort((a, b) => b.win_rate - a.win_rate);
			}
		}
	},
	onLoad(options) {
		this.heroId = options.id;
		this.loadFromCache();
		this.fetchHeroList();
		this.fetchBuildData();
	},
	methods: {
		getCache(key) {
			try {
				const cached = uni.getStorageSync(key);
				if (cached && cached.timestamp) {
					return cached;
				}
			} catch (e) {}
			return null;
		},
		
		setCache(key, data) {
			try {
				uni.setStorageSync(key, {
					data: data,
					timestamp: Date.now()
				});
			} catch (e) {}
		},
		
		isCacheValid(cached) {
			if (!cached || !cached.timestamp) return false;
			return Date.now() - cached.timestamp < CACHE_DURATION;
		},
		
		loadFromCache() {
			const cachedBuild = this.getCache(`build_${this.heroId}`);
			const cachedHeroes = this.getCache('heroList');
			
			if (cachedBuild && cachedBuild.data) {
				this.buildData = cachedBuild.data;
				this.loading = false;
			}
			if (cachedHeroes && cachedHeroes.data) {
				this.heroList = cachedHeroes.data;
			}
		},
		
		fetchHeroList() {
			const cached = this.getCache('heroList');
			if (cached && this.isCacheValid(cached)) {
				this.heroList = cached.data;
				return;
			}
			
			uni.request({
				url: 'https://myasw.pythonanywhere.com/api/heroes',
				method: 'GET',
				success: (res) => {
					if (res.statusCode === 200) {
						this.heroList = res.data;
						this.setCache('heroList', res.data);
					}
				}
			});
		},
		
		fetchBuildData() {
			const cached = this.getCache(`build_${this.heroId}`);
			if (cached && this.isCacheValid(cached)) {
				this.buildData = cached.data;
				this.loading = false;
				return;
			}
			
			uni.request({
				url: `https://myasw.pythonanywhere.com/api/hero/${this.heroId}/build`,
				method: 'GET',
				success: (res) => {
					if (res.statusCode === 200) {
						if (res.data.error) {
							this.error = res.data.error;
						} else {
							this.buildData = res.data;
							this.setCache(`build_${this.heroId}`, res.data);
						}
					} else {
						this.error = '加载失败';
					}
					this.loading = false;
				},
				fail: (err) => {
					console.error('Failed to fetch build data:', err);
					if (!this.buildData.counters || this.buildData.counters.length === 0) {
						this.error = '网络错误，请重试';
					}
					this.loading = false;
				}
			});
		},
		
		getHeroInfo(heroId) {
			return this.heroList.find(h => h.id === heroId) || {};
		},
		
		getHeroName(heroId) {
			const hero = this.getHeroInfo(heroId);
			return hero.name || `英雄${heroId}`;
		},
		
		getHeroImage(heroId) {
			const hero = this.getHeroInfo(heroId);
			if (hero.image) return hero.image;
			return `https://ddragon.leagueoflegends.com/cdn/16.6.1/img/champion/Unknown.png`;
		},
		
		getItemIcon(itemId) {
			return `https://ddragon.leagueoflegends.com/cdn/16.6.1/img/item/${itemId}.png`;
		},
		
		getWinRateClass(winRate) {
			if (winRate >= 50) return 'win-rate-high';
			if (winRate >= 45) return 'win-rate-medium';
			return 'win-rate-low';
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

.loading, .error, .no-data {
	text-align: center;
	padding: 100rpx 0;
	font-size: 28rpx;
	color: #666;
}

.error {
	color: #ff4d4f;
}

.matchup-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	margin-bottom: 20rpx;
}

.matchup-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.matchup-version {
	font-size: 24rpx;
	color: #999;
}

.matchup-tabs {
	display: flex;
	gap: 15rpx;
	margin-bottom: 20rpx;
}

.matchup-tab {
	flex: 1;
	text-align: center;
	padding: 15rpx;
	background-color: white;
	border-radius: 10rpx;
	font-size: 26rpx;
	color: #666;
	border: 2rpx solid #e8e8e8;
}

.matchup-tab.active {
	background-color: #1890ff;
	color: white;
	border-color: #1890ff;
}

.matchup-list {
	margin-bottom: 20rpx;
}

.matchup-item {
	display: flex;
	align-items: center;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	margin-bottom: 15rpx;
	position: relative;
	overflow: hidden;
}

.matchup-hero {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 120rpx;
	margin-right: 20rpx;
}

.hero-image {
	width: 70rpx;
	height: 70rpx;
	border-radius: 50%;
	margin-bottom: 8rpx;
}

.hero-name {
	font-size: 22rpx;
	color: #333;
	font-weight: bold;
	text-align: center;
}

.matchup-stats {
	flex: 1;
}

.stat-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 8rpx 0;
	border-bottom: 1rpx solid #f0f0f0;
}

.stat-row:last-child {
	border-bottom: none;
}

.stat-label {
	font-size: 22rpx;
	color: #999;
}

.stat-value {
	font-size: 24rpx;
	font-weight: bold;
	color: #333;
}

.win-rate-high {
	color: #52c41a;
}

.win-rate-medium {
	color: #faad14;
}

.win-rate-low {
	color: #f5222d;
}

.win-rate-bar {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	height: 6rpx;
	background-color: #f0f0f0;
}

.bar-fill {
	height: 100%;
	background-color: #1890ff;
	transition: width 0.3s ease;
}

.items-section {
	background-color: white;
	border-radius: 10rpx;
	padding: 20rpx;
}

.section-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.item-category {
	margin-bottom: 25rpx;
}

.item-category:last-child {
	margin-bottom: 0;
}

.category-title {
	font-size: 24rpx;
	font-weight: bold;
	color: #666;
	margin-bottom: 15rpx;
	display: block;
}

.item-list {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.item-card {
	display: flex;
	align-items: center;
	padding: 15rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
}

.item-icons {
	display: flex;
	gap: 8rpx;
	margin-right: 15rpx;
}

.item-icon {
	width: 45rpx;
	height: 45rpx;
	border-radius: 6rpx;
}

.item-stats {
	display: flex;
	flex-direction: column;
}

.item-win-rate {
	font-size: 22rpx;
	font-weight: bold;
	color: #1890ff;
}

.item-pick-rate {
	font-size: 18rpx;
	color: #999;
}
</style>
