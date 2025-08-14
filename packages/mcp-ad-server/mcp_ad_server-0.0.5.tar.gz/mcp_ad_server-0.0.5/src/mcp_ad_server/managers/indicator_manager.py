"""
指标管理器 - 管理指标定义和分组
"""

import json
from typing import Any

import aiofiles

from ..config import Config
from .base import Manager


class IndicatorManager(Manager):
    """指标管理器类"""

    def __init__(self):
        super().__init__()
        self.groups: dict[str, dict[str, Any]] = {}
        # 支持的指标：game_type -> query_type -> indicators
        self.supported_indicators: dict[str, dict[str, list[str]]] = {}

    async def load_indicators(self):
        """加载所有指标定义"""
        indicators_dir = Config.INDICATORS_DIR

        if not indicators_dir.exists():
            self.logger.warning(f"指标目录不存在: {indicators_dir}")
            return

        try:
            # 加载棋牌游戏指标
            card_games_dir = indicators_dir / "card_games"
            if card_games_dir.exists():
                await self._load_game_type_indicators("card_games", card_games_dir)

            # 加载非棋牌游戏指标
            non_card_games_dir = indicators_dir / "non_card_games"
            if non_card_games_dir.exists():
                await self._load_game_type_indicators(
                    "non_card_games", non_card_games_dir
                )

            self.logger.info(f"成功加载指标配置: {dict(self.supported_indicators)}")

        except Exception as e:
            self.logger.error(f"加载指标目录失败: {e}")
            raise

    async def _load_game_type_indicators(self, game_type: str, game_type_dir):
        """加载特定游戏类型的指标配置"""
        self.supported_indicators[game_type] = {}

        # 加载广告查询指标
        ad_file = game_type_dir / "ad.json"
        if ad_file.exists():
            try:
                async with aiofiles.open(ad_file, encoding="utf-8") as f:
                    content = await f.read()
                    ad_indicators = json.loads(content)
                    self.supported_indicators[game_type]["ad_query"] = ad_indicators
                    self.logger.info(f"加载{game_type}广告指标: {len(ad_indicators)}个")
            except Exception as e:
                self.logger.error(f"加载{game_type}广告指标文件失败 {ad_file}: {e}")

        # 加载素材查询指标
        material_file = game_type_dir / "material.json"
        if material_file.exists():
            try:
                async with aiofiles.open(material_file, encoding="utf-8") as f:
                    content = await f.read()
                    material_indicators = json.loads(content)
                    self.supported_indicators[game_type][
                        "material_query"
                    ] = material_indicators
                    self.logger.info(f"加载{game_type}素材指标: {len(material_indicators)}个")
            except Exception as e:
                self.logger.error(f"加载{game_type}素材指标文件失败 {material_file}: {e}")

    async def load_groups(self):
        """加载所有指标分组"""
        groups_dir = Config.GROUPS_DIR

        if not groups_dir.exists():
            self.logger.warning(f"指标分组目录不存在: {groups_dir}")
            return

        try:
            group_files = list(groups_dir.glob("*.json"))
            self.logger.info(f"发现{len(group_files)}个分组文件")

            for file_path in group_files:
                group_name = file_path.stem
                try:
                    async with aiofiles.open(file_path, encoding="utf-8") as f:
                        content = await f.read()
                        group_data = json.loads(content)
                        self.groups[group_name] = group_data

                except Exception as e:
                    self.logger.error(f"加载分组文件失败 {file_path}: {e}")

            self.logger.info(f"成功加载{len(self.groups)}个指标分组")

        except Exception as e:
            self.logger.error(f"加载分组目录失败: {e}")
            raise

    async def load_data(self) -> None:
        """实现基类的抽象方法加载数据"""
        await self.load_indicators()
        await self.load_groups()
        self.loaded = True
        self.logger.info("指标管理器数据加载完成")

    async def initialize(self):
        """初始化管理器"""
        if self.is_loaded():
            return
        await self.load_data()
        self.logger.info("指标管理器初始化完成")

    def _get_game_type(self, app_id: str) -> str:
        """根据游戏ID获取游戏类型"""
        if app_id in Config.CARD_GAME_APPIDS:
            return "card_games"
        elif app_id in Config.NON_CARD_GAME_APPIDS:
            return "non_card_games"
        else:
            raise ValueError(f"不支持的游戏ID: {app_id}")

    def get_available_indicators(self, app_id: str, query_type: str) -> list[str]:
        """获取指定游戏、查询类型的可用指标列表（包含基于app_id的条件性指标）"""
        game_type = self._get_game_type(app_id)

        if game_type not in self.supported_indicators:
            raise ValueError(f"未找到游戏类型 {game_type} 的指标配置")

        if query_type not in self.supported_indicators[game_type]:
            raise ValueError(f"未找到游戏类型 {game_type} 的 {query_type} 指标配置")

        # 获取基础指标
        base_indicators = self.supported_indicators[game_type][query_type].copy()

        # 动态注入仅基于app_id的条件性指标（仅对广告查询）
        if query_type == "ad_query":
            app_conditional_indicators = self._get_app_conditional_indicators(app_id)
            base_indicators.extend(app_conditional_indicators)

        return base_indicators

    def _get_app_conditional_indicators(self, app_id: str) -> list[str]:
        """根据app_id获取条件性指标（不包括需要group_key的指标）"""
        conditional_indicators = []

        # 平均关卡系列：仅当 appid = 69
        if app_id == "69":
            conditional_indicators.extend(
                ["平均关卡", "平均在线时长（分钟）", "平均章节", "付费用户平均关卡", "付费用户平均在线时长（分钟）", "付费用户平均章节"]
            )

        # 注意：基于group_key的条件性指标（cid、广告创建时间、账户余额、优质广告状态）
        # 现在由 api_client._prepare_response_fields 在返回阶段处理

        return conditional_indicators

    def get_group(self, group_id: str) -> dict[str, Any] | None:
        """获取指标分组"""
        return self.groups.get(group_id)

    def get_all_groups(self) -> dict[str, dict[str, Any]]:
        """获取所有指标分组"""
        return self.groups.copy()

    def get_group_names(self) -> list[str]:
        """获取所有分组名称"""
        return list(self.groups.keys())

    def get_indicators_by_group(self, group_id: str) -> list[str]:
        """根据分组获取指标列表"""
        group = self.groups.get(group_id)
        if group:
            return group.get("indicators", [])
        return []

    def recommend_indicators_by_scenario(self, scenario: str) -> list[str]:
        """基于业务场景推荐指标"""
        group_id = Config.SCENARIO_MAPPING.get(scenario)
        if group_id:
            return self.get_indicators_by_group(group_id)
        return []

    def validate_indicators(
        self, indicators: list[str], app_id: str, query_type: str = "ad_query"
    ) -> tuple[list[str], list[str]]:
        """验证指标名称，返回(有效指标, 无效指标)

        Args:
            indicators: 要验证的指标列表
            app_id: 游戏ID，必需参数
            query_type: 查询类型，可选值：ad_query(广告数据查询)、material_query(素材数据查询)，默认ad_query

        Returns:
            tuple[list[str], list[str]]: (有效指标列表, 无效指标列表)

        Note:
            基于group_key的条件性指标（cid、广告创建时间等）现在由API客户端在返回阶段自动处理
        """
        try:
            available_indicators = self.get_available_indicators(app_id, query_type)
        except ValueError as e:
            # 如果没有找到游戏指标配置，直接抛出原始异常
            raise e

        valid_indicators = []
        invalid_indicators = []

        for indicator in indicators:
            if indicator in available_indicators:
                valid_indicators.append(indicator)
            else:
                invalid_indicators.append(indicator)

        return valid_indicators, invalid_indicators

    def get_supported_game_types(self) -> list[str]:
        """获取支持的游戏类型列表"""
        return list(self.supported_indicators.keys())

    def get_supported_query_types(self, game_type: str) -> list[str]:
        """获取指定游戏类型支持的查询类型"""
        return list(self.supported_indicators.get(game_type, {}).keys())

    def is_indicator_supported(
        self, indicator_name: str, game_type: str, query_type: str
    ) -> bool:
        """检查指标是否在指定上下文中支持"""
        return (
            game_type in self.supported_indicators
            and query_type in self.supported_indicators[game_type]
            and indicator_name in self.supported_indicators[game_type][query_type]
        )

    def get_indicator_contexts(self, indicator_name: str) -> list[dict[str, str]]:
        """获取指标支持的所有上下文（游戏类型和查询类型组合）"""
        contexts = []
        for game_type in self.get_supported_game_types():
            for query_type in self.get_supported_query_types(game_type):
                if self.is_indicator_supported(indicator_name, game_type, query_type):
                    contexts.append(
                        {
                            "game_type": game_type,
                            "query_type": query_type,
                            "game_type_display": "棋牌游戏"
                            if game_type == "card_games"
                            else "非棋牌游戏",
                            "query_type_display": "广告数据查询"
                            if query_type == "ad_query"
                            else "素材数据查询",
                        }
                    )
        return contexts

    def get_indicator_stats(self) -> dict[str, Any]:
        """获取指标统计信息"""
        # 计算各游戏类型的指标总数
        indicator_counts = {}
        for game_type, queries in self.supported_indicators.items():
            for query_type, indicators in queries.items():
                key = f"{game_type}_{query_type}"
                indicator_counts[key] = len(indicators)

        return {
            "supported_indicators": indicator_counts,
            "total_groups": len(self.groups),
            "groups_info": [
                {
                    "group_id": group_id,
                    "name": group_data.get("name", ""),
                    "indicator_count": len(group_data.get("indicators", [])),
                }
                for group_id, group_data in self.groups.items()
            ],
        }

    def recommend_indicators(
        self, scenario: str, app_id: str, query_type: str = "ad_query"
    ) -> list[str]:
        """基于游戏和业务场景推荐指标

        Args:
            scenario: 业务场景
            app_id: 游戏ID
            query_type: 查询类型，"ad_query" 或 "material_query"

        Returns:
            推荐的指标列表
        """
        # 先获取场景推荐的指标
        scenario_indicators = self.recommend_indicators_by_scenario(scenario)

        # 根据查询类型获取游戏可用指标
        try:
            available_indicators = self.get_available_indicators(app_id, query_type)
        except ValueError:
            # 如果没有游戏特定配置，返回场景指标
            return scenario_indicators

        # 返回场景指标与游戏可用指标的交集
        return [ind for ind in scenario_indicators if ind in available_indicators]

    async def reload(self):
        """重新加载指标和分组数据"""
        self.clear_data()
        self.groups.clear()
        self.supported_indicators.clear()

        await self.initialize()
        self.logger.info("指标管理器数据已重新加载")
