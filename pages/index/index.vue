<template>
	<view class="container">
		<view class="hero-section">
			<image class="hero-bg" src="https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Garen_0.jpg" mode="aspectFill"></image>
			<view class="overlay"></view>
			<view class="hero-content">
				<text class="app-title">LOL 英雄 BP 助手</text>
				<text class="app-subtitle">实时胜率数据 · 符文推荐 · 对线攻略</text>
			</view>
		</view>
		
		<view class="features">
			<view class="feature-card" @click="navigateToHeroList">
				<view class="feature-icon">🏆</view>
				<text class="feature-title">英雄数据</text>
				<text class="feature-desc">查看所有英雄胜率、登场率</text>
			</view>
			
			<view class="feature-card" @click="navigateToHeroList">
				<view class="feature-icon">⚔️</view>
				<text class="feature-title">符文推荐</text>
				<text class="feature-desc">当前版本最优符文搭配</text>
			</view>
			
			<view class="feature-card" @click="navigateToHeroList">
				<view class="feature-icon">🎯</view>
				<text class="feature-title">对线攻略</text>
				<text class="feature-desc">克制关系与出装建议</text>
			</view>
		</view>
		
		<view class="start-btn-wrapper">
			<button class="start-btn" @click="navigateToHeroList">
				<text class="btn-text">开始探索</text>
				<text class="btn-arrow">→</text>
			</button>
		</view>
		
		<view class="footer">
			<text class="footer-text">数据来源: OP.GG · DDragon</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {}
	},
	methods: {
		navigateToHeroList() {
			uni.navigateTo({
				url: '/pages/hero/heroList'
			})
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
	display: flex;
	flex-direction: column;
}

.hero-section {
	position: relative;
	height: 450rpx;
	overflow: hidden;
}

.hero-bg {
	width: 100%;
	height: 100%;
	opacity: 0.4;
}

.overlay {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: linear-gradient(180deg, transparent 0%, rgba(26, 26, 46, 0.8) 70%, #1a1a2e 100%);
}

.hero-content {
	position: absolute;
	bottom: 60rpx;
	left: 40rpx;
	right: 40rpx;
}

.app-title {
	font-size: 56rpx;
	font-weight: bold;
	color: #ffffff;
	text-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.5);
	display: block;
	margin-bottom: 16rpx;
}

.app-subtitle {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.7);
	display: block;
}

.features {
	padding: 40rpx 30rpx;
	display: flex;
	justify-content: space-between;
	gap: 20rpx;
}

.feature-card {
	flex: 1;
	background: rgba(255, 255, 255, 0.08);
	border-radius: 20rpx;
	padding: 30rpx 20rpx;
	text-align: center;
	backdrop-filter: blur(10px);
	border: 1rpx solid rgba(255, 255, 255, 0.1);
	transition: all 0.3s ease;
}

.feature-card:active {
	transform: scale(0.95);
	background: rgba(255, 255, 255, 0.12);
}

.feature-icon {
	font-size: 48rpx;
	margin-bottom: 16rpx;
}

.feature-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #ffffff;
	display: block;
	margin-bottom: 10rpx;
}

.feature-desc {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.6);
	display: block;
}

.start-btn-wrapper {
	padding: 40rpx 60rpx;
	margin-top: auto;
}

.start-btn {
	width: 100%;
	height: 100rpx;
	background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
	border-radius: 50rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border: none;
	box-shadow: 0 10rpx 40rpx rgba(233, 69, 96, 0.4);
}

.start-btn::after {
	border: none;
}

.btn-text {
	font-size: 34rpx;
	font-weight: bold;
	color: #ffffff;
	margin-right: 16rpx;
}

.btn-arrow {
	font-size: 34rpx;
	color: #ffffff;
}

.footer {
	padding: 40rpx;
	text-align: center;
}

.footer-text {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.4);
}
</style>
