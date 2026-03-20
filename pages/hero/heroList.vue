<template>
	<view class="container">
		<view class="search-bar">
			<input type="text" v-model="searchKeyword" placeholder="搜索英雄称号或姓名" class="search-input" />
		</view>
		
		<view class="lane-filter">
			<view 
				v-for="lane in laneOptions" 
				:key="lane.value"
				class="lane-tab"
				:class="{ active: selectedLane === lane.value }"
				@click="selectLane(lane.value)"
			>
				<text class="lane-icon">{{ lane.icon }}</text>
				<text class="lane-name">{{ lane.label }}</text>
			</view>
		</view>
		
		<view v-if="loading" class="loading">加载中...</view>
		<view v-else class="hero-grid">
			<view 
				v-for="hero in filteredHeroes" 
				:key="hero.id"
				class="hero-card"
				@click="navigateToHeroDetail(hero.id)"
			>
				<image :src="hero.image" class="hero-image" />
				<view class="hero-info">
					<text class="hero-title-name">{{ hero.name }} - {{  hero.title }}</text>
					<view class="hero-lanes">
						<text 
							v-for="(lane, index) in getHeroLanes(hero)" 
							:key="index"
							class="lane-tag"
						>{{ lane }}</text>
					</view>
				</view>
			</view>
		</view>
		
		<view v-if="!loading && filteredHeroes.length === 0" class="no-result">
			<text>未找到匹配的英雄</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			searchKeyword: '',
			heroes: [],
			loading: true,
			selectedLane: 'all',
			laneOptions: [
				{ value: 'all', label: '全部', icon: '🎮' },
				{ value: 'TOP', label: '上单', icon: '🗡️' },
				{ value: 'JUNGLE', label: '打野', icon: '🌲' },
				{ value: 'MID', label: '中单', icon: '🔮' },
				{ value: 'ADC', label: 'ADC', icon: '🏹' },
				{ value: 'SUPPORT', label: '辅助', icon: '💚' }
			]
		}
	},
	computed: {
		filteredHeroes() {
			let result = this.heroes;
			
			if (this.selectedLane !== 'all') {
				result = result.filter(hero => {
					if (!hero.lanes) return false;
					return hero.lanes.some(lane => lane.name === this.selectedLane);
				});
			}
			
			if (this.searchKeyword) {
				const keyword = this.searchKeyword.toLowerCase();
				result = result.filter(hero => {
					const name = hero.name || '';
					const title = hero.title || '';
					return name.toLowerCase().includes(keyword) || title.toLowerCase().includes(keyword) || (name + title).toLowerCase().includes(keyword);
				});
			}
			
			return result;
		}
	},
	onLoad() {
		this.fetchHeroes();
	},
	methods: {
		fetchHeroes() {
			uni.request({
				url: 'https://myasw.pythonanywhere.com/api/heroes',
				method: 'GET',
				success: (res) => {
					this.heroes = res.data;
					this.loading = false;
					uni.setStorageSync('heroes', res.data);
				},
				fail: (err) => {
					console.error('Failed to fetch heroes:', err);
					const cachedHeroes = uni.getStorageSync('heroes');
					if (cachedHeroes) {
						this.heroes = cachedHeroes;
						this.loading = false;
					} else {
						uni.showToast({
							title: '网络错误，无法获取数据',
							icon: 'none'
						});
						this.loading = false;
					}
				}
			});
		},
		
		selectLane(lane) {
			this.selectedLane = lane;
		},
		
		getHeroLanes(hero) {
			if (!hero.lanes || hero.lanes.length === 0) return [];
			const laneNames = {
				'TOP': '上单',
				'JUNGLE': '打野',
				'MID': '中单',
				'ADC': 'ADC',
				'SUPPORT': '辅助'
			};
			return hero.lanes.map(lane => laneNames[lane.name] || lane.name);
		},
		
		navigateToHeroDetail(heroId) {
			uni.navigateTo({
				url: `/pages/hero/heroDetail?id=${heroId}`
			});
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

.search-bar {
	margin-bottom: 20rpx;
}

.search-input {
	width: 100%;
	height: 70rpx;
	border: 2rpx solid #e0e0e0;
	border-radius: 35rpx;
	padding: 0 30rpx;
	font-size: 28rpx;
	background-color: white;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.lane-filter {
	display: flex;
	gap: 15rpx;
	margin-bottom: 20rpx;
	padding: 15rpx;
	background-color: white;
	border-radius: 15rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
	overflow-x: auto;
}

.lane-tab {
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 15rpx 20rpx;
	background-color: #f5f5f5;
	border-radius: 10rpx;
	border: 2rpx solid transparent;
	transition: all 0.3s ease;
	min-width: 80rpx;
}

.lane-tab.active {
	background-color: #e6f7ff;
	border-color: #1890ff;
}

.lane-icon {
	font-size: 32rpx;
	margin-bottom: 5rpx;
}

.lane-name {
	font-size: 22rpx;
	color: #333;
	font-weight: bold;
}

.lane-tab.active .lane-name {
	color: #1890ff;
}

.loading {
	text-align: center;
	padding: 50rpx 0;
	font-size: 28rpx;
	color: #666;
}

.no-result {
	text-align: center;
	padding: 100rpx 0;
	font-size: 28rpx;
	color: #999;
}

.hero-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 15rpx;
}

.hero-card {
	background-color: white;
	border-radius: 12rpx;
	padding: 15rpx;
	text-align: center;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
	transition: all 0.3s ease;
}

.hero-card:hover {
	transform: translateY(-5rpx);
	box-shadow: 0 5rpx 15rpx rgba(0,0,0,0.15);
}

.hero-image {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	margin-bottom: 10rpx;
}

.hero-info {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.hero-title-name {
	font-size: 22rpx;
	color: #333;
	font-weight: bold;
	line-height: 1.3;
	margin-bottom: 8rpx;
}

.hero-lanes {
	display: flex;
	flex-wrap: wrap;
	justify-content: center;
	gap: 5rpx;
}

.lane-tag {
	font-size: 16rpx;
	color: #1890ff;
	background-color: #e6f7ff;
	padding: 3rpx 10rpx;
	border-radius: 10rpx;
}
</style>
