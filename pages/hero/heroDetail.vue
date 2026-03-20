<template>
	<view class="container">
		<view v-if="loading" class="loading">加载中...</view>
		<view v-else>
			<view class="hero-header">
				<image :src="hero.image" class="hero-image" />
				<view class="hero-info">
					<text class="hero-name">{{ hero.name }}</text>
					<text class="hero-title">{{ hero.title }}</text>
					<view class="hero-stats">
						<view class="stat-item">
							<text class="stat-label">均胜率</text>
							<text class="stat-value">{{ hero.avgWinRate || hero.winRate || 0 }}%</text>
						</view>
						<view class="stat-item">
							<text class="stat-label">均登场率</text>
							<text class="stat-value">{{ hero.avgPickRate || hero.pickRate || 0 }}%</text>
						</view>
						<view class="stat-item">
							<text class="stat-label">均Ban率</text>
							<text class="stat-value">{{ hero.avgBanRate || hero.banRate || 0 }}%</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 筛选条件 -->
			<view class="filter-section" v-if="optionsLoaded && tiers.length > 0">
				<view class="filter-row">
					<text class="filter-label">段位:</text>
					<picker :value="tierIndex" :range="tiers" range-key="label" @change="onTierChange">
						<view class="picker-value">{{ tiers[tierIndex] ? tiers[tierIndex].label : '加载中...' }}</view>
					</picker>
				</view>
				<view class="filter-row">
					<text class="filter-label">模式:</text>
					<picker :value="queueIndex" :range="queues" range-key="label" @change="onQueueChange">
						<view class="picker-value">{{ queues[queueIndex] ? queues[queueIndex].label : '加载中...' }}</view>
					</picker>
				</view>
			</view>
			
			<!-- 分路选择 -->
			<view class="lane-section" v-if="hero.lanes && hero.lanes.length > 0">
				<text class="section-title">分路选择</text>
				<view class="lane-tabs">
					<view 
						v-for="lane in hero.lanes" 
						:key="lane.name"
						class="lane-tab"
						:class="{ active: selectedLane === lane.name }"
						@click="selectLane(lane.name)"
					>
						<text class="lane-name">{{ lane.displayName }}</text>
						<text class="lane-percent">{{ lane.playRatePercent }}%</text>
					</view>
				</view>
			</view>
			
			<!-- 角色选择 -->
			<view class="role-section" v-if="currentRoles && currentRoles.length > 0">
				<text class="section-title">角色定位</text>
				<view class="role-tabs">
					<view 
						v-for="role in currentRoles" 
						:key="role.name"
						class="role-tab"
						:class="{ active: selectedRole === role.name }"
						@click="selectRole(role.name)"
					>
						<text class="role-name">{{ role.displayName || getRoleDisplayName(role.name) }}</text>
						<text class="role-percent">{{ role.roleRatePercent }}%</text>
						<text class="role-win-rate">胜率 {{ role.winRate }}%</text>
					</view>
				</view>
			</view>
			
			<!-- 分路数据展示 -->
			<view class="lane-data-section" v-if="selectedLaneData">
				<text class="section-title">{{ selectedLaneData.displayName }}数据</text>
				<view class="data-grid">
					<view class="data-item">
						<text class="data-label">胜率</text>
						<text class="data-value">{{ selectedLaneData.winRate }}%</text>
					</view>
					<view class="data-item">
						<text class="data-label">登场率</text>
						<text class="data-value">{{ selectedLaneData.pickRate }}%</text>
					</view>
					<view class="data-item">
						<text class="data-label">Ban率</text>
						<text class="data-value">{{ selectedLaneData.banRate }}%</text>
					</view>
					<view class="data-item">
						<text class="data-label">KDA</text>
						<text class="data-value">{{ selectedLaneData.kda }}</text>
					</view>
				</view>
				
				<!-- 角色详细数据 -->
				<view class="role-detail-section" v-if="selectedRoleData">
					<text class="section-subtitle">{{ selectedRoleData.displayName || getRoleDisplayName(selectedRoleData.name) }}详细数据</text>
					<view class="data-grid">
						<view class="data-item">
							<text class="data-label">胜率</text>
							<text class="data-value highlight">{{ selectedRoleData.winRate }}%</text>
						</view>
						<view class="data-item">
							<text class="data-label">场次</text>
							<text class="data-value">{{ selectedRoleData.play }}</text>
						</view>
						<view class="data-item">
							<text class="data-label">胜场</text>
							<text class="data-value">{{ selectedRoleData.win }}</text>
						</view>
						<view class="data-item">
							<text class="data-label">占比</text>
							<text class="data-value">{{ selectedRoleData.roleRatePercent }}%</text>
						</view>
					</view>
				</view>
			</view>
			
			<view class="tabs">
				<view 
					class="tab-item" 
					:class="{ active: activeTab === 'skills' }"
					@click="activeTab = 'skills'"
				>
					技能
				</view>
				<view 
					class="tab-item" 
					:class="{ active: activeTab === 'runes' }"
					@click="navigateToRunes"
				>
					天赋
				</view>
				<view 
					class="tab-item" 
					:class="{ active: activeTab === 'matchups' }"
					@click="navigateToMatchups"
				>
					对线
				</view>
			</view>
			
			<view class="tab-content" v-if="activeTab === 'skills'">
				<!-- 技能图标栏 -->
				<view class="skill-icons">
					<view 
						v-for="skill in hero.skills" 
						:key="skill.id"
						class="skill-icon-item"
						:class="{ active: selectedSkill.id === skill.id }"
						@click="selectSkill(skill)"
					>
						<image :src="skill.icon" class="skill-icon" />
						<text class="skill-key" v-if="skill.key">{{ skill.key }}</text>
					</view>
				</view>
				
				<!-- 技能描述区域 -->
				<view class="skill-description">
					<view class="skill-header">
						<text class="skill-name">{{ getSkillFullName(selectedSkill) }}</text>
					</view>
					
					<!-- 技能属性 -->
					<view class="skill-stats" v-if="selectedSkill.cooldown || selectedSkill.cost || selectedSkill.range">
						<view class="skill-stat" v-if="selectedSkill.cooldown && selectedSkill.cooldown.length > 0">
							<text class="stat-label">冷却:</text>
							<text class="stat-value">{{ formatArray(selectedSkill.cooldown) }}秒</text>
						</view>
						<view class="skill-stat" v-if="selectedSkill.cost && selectedSkill.cost.length > 0">
							<text class="stat-label">消耗:</text>
							<text class="stat-value">{{ formatArray(selectedSkill.cost) }}</text>
						</view>
						<view class="skill-stat" v-if="selectedSkill.range && selectedSkill.range.length > 0 && selectedSkill.range[0] > 0">
							<text class="stat-label">范围:</text>
							<text class="stat-value">{{ formatArray(selectedSkill.range) }}</text>
						</view>
					</view>
					
					<text class="skill-desc">{{ selectedSkill.description }}</text>
				</view>
				
				<!-- 技能加点顺序 -->
				<view class="skill-order-section" v-if="buildData.skill_order && buildData.skill_order.length > 0">
					<text class="section-title">技能加点</text>
					<view class="skill-order-tabs">
						<view 
							v-for="(order, index) in buildData.skill_order" 
							:key="index"
							class="skill-order-tab"
							:class="{ active: selectedSkillOrderIndex === index }"
							@click="selectedSkillOrderIndex = index"
						>
							<text class="order-priority">{{ order.priority.join(' > ') }}</text>
							<text class="order-stats">登场率: {{ order.pick_rate }}%</text>
						</view>
					</view>
					
					<!-- 技能加点图表 -->
					<view class="skill-order-chart" v-if="currentSkillOrder">
						<view class="chart-header">
							<view class="chart-cell header-cell"></view>
							<view class="chart-cell header-cell" v-for="level in 18" :key="level">
								<text class="level-num">{{ level }}</text>
							</view>
						</view>
						<view class="chart-row" v-for="key in ['Q', 'W', 'E', 'R']" :key="key">
							<view class="chart-cell skill-cell">
								<image :src="getSkillIconByKey(key)" class="chart-skill-icon" />
							</view>
							<view 
								class="chart-cell" 
								v-for="level in 18" 
								:key="level"
								:class="{ 'skill-up': isSkillUpAtLevel(key, level) }"
							>
								<text v-if="isSkillUpAtLevel(key, level)" class="skill-up-mark">{{ key }}</text>
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
			activeTab: 'skills',
			hero: {},
			buildData: {
				skill_order: [],
				skills: []
			},
			loading: true,
			selectedSkill: {
				id: 1,
				name: '被动技能',
				description: '技能描述加载中...'
			},
			selectedLane: null,
			selectedRole: null,
			heroId: null,
			tierIndex: 0,
			queueIndex: 0,
			tiers: [],
			queues: [],
			optionsLoaded: false,
			selectedSkillOrderIndex: 0
		}
	},
	computed: {
		currentRoles() {
			if (!this.selectedLane || !this.hero.lanes) return []
			const lane = this.hero.lanes.find(l => l.name === this.selectedLane)
			return lane ? lane.roles : []
		},
		selectedLaneData() {
			if (!this.selectedLane || !this.hero.lanes) return null
			return this.hero.lanes.find(l => l.name === this.selectedLane)
		},
		selectedRoleData() {
			if (!this.selectedRole || !this.currentRoles) return null
			return this.currentRoles.find(r => r.name === this.selectedRole)
		},
		currentSkillOrder() {
			if (!this.buildData.skills || this.buildData.skills.length === 0) return null
			return this.buildData.skills[this.selectedSkillOrderIndex] || null
		}
	},
	onLoad(options) {
		this.heroId = options.id;
		this.loadBuildFromCache();
		this.fetchOptions();
		this.fetchHeroData(this.heroId);
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
		
		loadBuildFromCache() {
			const cached = this.getCache(`build_${this.heroId}`);
			if (cached && cached.data) {
				this.buildData = cached.data;
			}
		},
		
		fetchOptions() {
			uni.request({
				url: 'https://myasw.pythonanywhere.com/api/options',
				method: 'GET',
				success: (res) => {
					this.tiers = res.data.tiers;
					this.queues = res.data.queues;
					this.tierIndex = 11;
					this.optionsLoaded = true;
				}
			});
		},
		fetchHeroData(heroId) {
			const cachedHero = uni.getStorageSync(`hero_${heroId}`);
			if (cachedHero) {
				this.hero = cachedHero;
				if (cachedHero.skills && cachedHero.skills.length > 0) {
					this.selectedSkill = cachedHero.skills[0];
				}
				if (cachedHero.lanes && cachedHero.lanes.length > 0) {
					this.selectedLane = cachedHero.lanes[0].name;
				}
				this.loading = false;
			}
			
			uni.request({
				url: `https://myasw.pythonanywhere.com/api/hero/${heroId}`,
				method: 'GET',
				success: (res) => {
					this.hero = res.data;
					if (res.data.skills && res.data.skills.length > 0) {
						this.selectedSkill = res.data.skills[0];
					}
					if (res.data.lanes && res.data.lanes.length > 0) {
						this.selectedLane = res.data.lanes[0].name;
					}
					this.loading = false;
					uni.setStorageSync(`hero_${heroId}`, res.data);
				},
				fail: (err) => {
					console.error('Failed to fetch hero data:', err);
					if (!cachedHero) {
						uni.showToast({
							title: '网络错误，无法获取数据',
							icon: 'none'
						});
					}
					this.loading = false;
				}
			});
		},
		fetchHeroStats() {
			const tier = this.tiers[this.tierIndex].value;
			const queue = this.queues[this.queueIndex].value;
			
			uni.showLoading({ title: '加载中...' });
			
			uni.request({
				url: `https://myasw.pythonanywhere.com/api/hero/${this.heroId}/stats`,
				method: 'GET',
				data: { tier, queue },
				success: (res) => {
					uni.hideLoading();
					if (res.data.error) {
						uni.showToast({
							title: res.data.error,
							icon: 'none'
						});
						return;
					}
					this.hero.avgWinRate = res.data.avgWinRate;
					this.hero.avgPickRate = res.data.avgPickRate;
					this.hero.avgBanRate = res.data.avgBanRate;
					this.hero.totalPlay = res.data.totalPlay;
					this.hero.lanes = res.data.lanes;
					if (res.data.lanes && res.data.lanes.length > 0) {
						this.selectedLane = res.data.lanes[0].name;
						this.selectedRole = null;
					}
				},
				fail: (err) => {
					uni.hideLoading();
					console.error('Failed to fetch stats:', err);
					uni.showToast({
						title: '获取数据失败',
						icon: 'none'
					});
				}
			});
		},
		onTierChange(e) {
			this.tierIndex = e.detail.value;
			this.fetchHeroStats();
		},
		onQueueChange(e) {
			this.queueIndex = e.detail.value;
			this.fetchHeroStats();
		},
		selectSkill(skill) {
			this.selectedSkill = skill;
		},
		getSkillFullName(skill) {
			if (!skill) return '';
			if (skill.key) {
				return `${skill.key}：${skill.name}`;
			}
			return skill.name;
		},
		formatArray(arr) {
			if (!arr || arr.length === 0) return '';
			if (arr.length === 1) return arr[0];
			return arr.join('/');
		},
		selectLane(laneName) {
			this.selectedLane = laneName;
			this.selectedRole = null;
		},
		selectRole(roleName) {
			this.selectedRole = roleName;
		},
		getRoleDisplayName(roleName) {
			const roleMap = {
				'Tank': '坦克',
				'Fighter': '战士',
				'Assassin': '刺客',
				'Mage': '法师',
				'Marksman': '射手',
				'Support': '辅助',
				'Controller': '控制',
				'Slayer': '杀手',
				'TANK': '坦克',
				'FIGHTER': '战士',
				'ASSASSIN': '刺客',
				'MAGE': '法师',
				'MARKSMAN': '射手',
				'SUPPORT': '辅助',
				'CONTROLLER': '控制',
				'SLAYER': '杀手'
			};
			return roleMap[roleName] || roleName;
		},
		navigateToRunes() {
			uni.navigateTo({
				url: `/pages/hero/heroRunes?id=${this.hero.id}`
			});
		},
		navigateToMatchups() {
			uni.navigateTo({
				url: `/pages/hero/heroMatchups?id=${this.hero.id}`
			});
		},
		fetchBuildData() {
			const cached = this.getCache(`build_${this.heroId}`);
			if (cached && this.isCacheValid(cached)) {
				this.buildData = cached.data;
				return;
			}
			
			uni.request({
				url: `https://myasw.pythonanywhere.com/api/hero/${this.heroId}/build`,
				method: 'GET',
				success: (res) => {
					if (res.statusCode === 200 && !res.data.error) {
						this.buildData = res.data;
						this.setCache(`build_${this.heroId}`, res.data);
					}
				},
				fail: (err) => {
					console.error('Failed to fetch build data:', err);
				}
			});
		},
		getSkillIconByKey(key) {
			const skill = this.hero.skills?.find(s => s.key === key);
			return skill ? skill.icon : '';
		},
		isSkillUpAtLevel(key, level) {
			if (!this.currentSkillOrder || !this.currentSkillOrder.order) return false;
			const order = this.currentSkillOrder.order;
			if (level > order.length) return false;
			return order[level - 1] === key;
		}
	}
}
</script>

<style scoped>
.container {
	padding: 20rpx;
}

.loading {
	text-align: center;
	padding: 100rpx 0;
	font-size: 28rpx;
	color: #666;
}

.hero-header {
	display: flex;
	margin-bottom: 30rpx;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.hero-image {
	width: 150rpx;
	height: 150rpx;
	border-radius: 50%;
	margin-right: 20rpx;
}

.hero-info {
	flex: 1;
}

.filter-section {
	display: flex;
	flex-wrap: wrap;
	margin-bottom: 20rpx;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.filter-row {
	display: flex;
	align-items: center;
	margin-right: 30rpx;
	margin-bottom: 10rpx;
}

.filter-label {
	font-size: 26rpx;
	color: #666;
	margin-right: 10rpx;
}

.picker-value {
	font-size: 26rpx;
	color: #1890ff;
	padding: 8rpx 16rpx;
	background-color: #e6f7ff;
	border-radius: 6rpx;
	border: 1rpx solid #91d5ff;
}

.hero-name {
	font-size: 36rpx;
	font-weight: bold;
	margin-bottom: 5rpx;
	color: #333;
}

.hero-title {
	font-size: 24rpx;
	color: #666;
	margin-bottom: 15rpx;
}

.hero-stats {
	display: flex;
	justify-content: space-around;
}

.stat-item {
	text-align: center;
	padding: 10rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
	flex: 1;
	margin: 0 5rpx;
}

.stat-label {
	display: block;
	font-size: 20rpx;
	color: #666;
	margin-bottom: 5rpx;
}

.stat-value {
	display: block;
	font-size: 24rpx;
	font-weight: bold;
	color: #1890ff;
}

.section-title {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 15rpx;
	padding-left: 10rpx;
	border-left: 4rpx solid #1890ff;
}

/* 分路选择样式 */
.lane-section {
	margin-bottom: 20rpx;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.lane-tabs {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.lane-tab {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 15rpx 25rpx;
	background-color: #f5f5f5;
	border-radius: 10rpx;
	border: 2rpx solid transparent;
	transition: all 0.3s ease;
}

.lane-tab.active {
	background-color: #e8f4fd;
	border-color: #1890ff;
}

.lane-name {
	font-size: 26rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 5rpx;
}

.lane-percent {
	font-size: 20rpx;
	color: #666;
}

/* 角色选择样式 */
.role-section {
	margin-bottom: 20rpx;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.role-tabs {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.role-tab {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 12rpx 20rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
	border: 2rpx solid transparent;
	transition: all 0.3s ease;
}

.role-tab.active {
	background-color: #fff3e0;
	border-color: #ff9800;
}

.role-name {
	font-size: 24rpx;
	color: #333;
	margin-bottom: 3rpx;
}

.role-percent {
	font-size: 20rpx;
	color: #ff9800;
	font-weight: bold;
	margin-bottom: 3rpx;
}

.role-win-rate {
	font-size: 18rpx;
	color: #4caf50;
}

/* 分路数据展示样式 */
.lane-data-section {
	margin-bottom: 20rpx;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.data-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.data-item {
	flex: 1;
	min-width: 45%;
	text-align: center;
	padding: 15rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
}

.data-label {
	display: block;
	font-size: 22rpx;
	color: #666;
	margin-bottom: 8rpx;
}

.data-value {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	color: #1890ff;
}

.data-value.highlight {
	color: #ff9800;
}

/* 角色详细数据样式 */
.role-detail-section {
	margin-top: 20rpx;
	padding-top: 15rpx;
	border-top: 1rpx dashed #e0e0e0;
}

.section-subtitle {
	display: block;
	font-size: 24rpx;
	font-weight: bold;
	color: #ff9800;
	margin-bottom: 12rpx;
	padding-left: 10rpx;
	border-left: 3rpx solid #ff9800;
}

/* 标签页样式 */
.tabs {
	display: flex;
	border-bottom: 1rpx solid #e0e0e0;
	margin-bottom: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	overflow: hidden;
}

.tab-item {
	flex: 1;
	text-align: center;
	padding: 15rpx 0;
	font-size: 28rpx;
	color: #666;
	position: relative;
	transition: all 0.3s ease;
}

.tab-item.active {
	color: #1890ff;
	background-color: #e8f4fd;
}

.tab-item.active::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 0;
	width: 100%;
	height: 3rpx;
	background-color: #1890ff;
}

/* 技能样式 */
.skill-icons {
	display: flex;
	justify-content: space-around;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.skill-icon-item {
	padding: 10rpx;
	border-radius: 8rpx;
	transition: all 0.3s ease;
	position: relative;
}

.skill-icon-item.active {
	background-color: #e8f4fd;
	border: 2rpx solid #1890ff;
}

.skill-icon {
	width: 80rpx;
	height: 80rpx;
}

.skill-key {
	position: absolute;
	bottom: 5rpx;
	left: 50%;
	transform: translateX(-50%);
	font-size: 20rpx;
	color: #666;
	font-weight: bold;
}

.skill-description {
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.skill-header {
	margin-bottom: 15rpx;
}

.skill-name {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	margin-bottom: 15rpx;
	color: #333;
}

.skill-stats {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
	margin-bottom: 15rpx;
	padding: 15rpx;
	background-color: #f5f7fa;
	border-radius: 8rpx;
}

.skill-stat {
	display: flex;
	align-items: center;
}

.stat-label {
	font-size: 22rpx;
	color: #999;
	margin-right: 8rpx;
}

.stat-value {
	font-size: 24rpx;
	color: #1890ff;
	font-weight: bold;
}

.skill-desc {
	display: block;
	font-size: 22rpx;
	color: #666;
	line-height: 1.5;
	white-space: pre-wrap;
}

/* 技能加点顺序样式 */
.skill-order-section {
	margin-top: 20rpx;
	padding: 20rpx;
	background-color: white;
	border-radius: 10rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.skill-order-tabs {
	display: flex;
	gap: 15rpx;
	margin-bottom: 20rpx;
	overflow-x: auto;
	padding-bottom: 10rpx;
}

.skill-order-tab {
	flex-shrink: 0;
	padding: 12rpx 20rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
	border: 2rpx solid transparent;
}

.skill-order-tab.active {
	background-color: #e8f4fd;
	border-color: #1890ff;
}

.order-priority {
	display: block;
	font-size: 24rpx;
	font-weight: bold;
	color: #333;
}

.order-stats {
	display: block;
	font-size: 20rpx;
	color: #999;
	margin-top: 5rpx;
}

.skill-order-chart {
	overflow-x: auto;
}

.chart-header, .chart-row {
	display: flex;
	align-items: center;
}

.chart-cell {
	flex-shrink: 0;
	width: 40rpx;
	height: 40rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border: 1rpx solid #e8e8e8;
	margin-right: 2rpx;
	margin-bottom: 2rpx;
}

.header-cell {
	background-color: #f5f5f5;
}

.level-num {
	font-size: 18rpx;
	color: #666;
}

.skill-cell {
	background-color: #fafafa;
	border: none;
}

.chart-skill-icon {
	width: 32rpx;
	height: 32rpx;
}

.skill-up {
	background-color: #1890ff;
}

.skill-up-mark {
	font-size: 20rpx;
	color: white;
	font-weight: bold;
}
</style>
