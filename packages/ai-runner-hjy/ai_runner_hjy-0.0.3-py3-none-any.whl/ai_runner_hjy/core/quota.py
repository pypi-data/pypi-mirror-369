"""
配额与速率限制管理模块
实现用户Key的配额检查和速率限制功能
"""

import os
import time
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import mysql.connector
from loguru import logger


class QuotaManager:
    """配额管理器"""
    
    def __init__(self):
        self.enable_quota_check = os.environ.get("ENABLE_QUOTA_CHECK", "true").lower() == "true"
        self.enable_rate_limit = os.environ.get("ENABLE_RATE_LIMIT", "true").lower() == "true"
        self.quota_warning_only = os.environ.get("QUOTA_WARNING_ONLY", "true").lower() == "true"
        self.rate_limit_warning_only = os.environ.get("RATE_LIMIT_WARNING_ONLY", "true").lower() == "true"
        
        logger.info(f"配额管理器初始化: quota_check={self.enable_quota_check}, rate_limit={self.enable_rate_limit}")
        logger.info(f"警告模式: quota_warning_only={self.quota_warning_only}, rate_limit_warning_only={self.rate_limit_warning_only}")
    
    def check_quota_and_rate_limit(
        self, 
        cursor, 
        key_id: int, 
        user_id: int
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        检查配额和速率限制
        
        Returns:
            (is_allowed, error_message, quota_info)
        """
        if not self.enable_quota_check and not self.enable_rate_limit:
            return True, None, {}
        
        try:
            # 获取Key的配额配置
            cursor.execute("""
                SELECT daily_quota, rps_limit 
                FROM ai_user_key 
                WHERE id = %s AND status = 'active'
            """, (key_id,))
            key_config = cursor.fetchone()
            
            if not key_config:
                return True, None, {}  # 没有配置配额，允许通过
            
            daily_quota = key_config[0]
            rps_limit = key_config[1]
            
            quota_info = {
                "daily_quota": daily_quota,
                "rps_limit": rps_limit,
                "daily_used": 0,
                "current_rps": 0
            }
            
            # 检查日配额
            if self.enable_quota_check and daily_quota:
                daily_used = self._get_daily_usage(cursor, key_id)
                quota_info["daily_used"] = daily_used
                
                if daily_used >= daily_quota:
                    error_msg = f"日配额超限: 已使用 {daily_used}/{daily_quota}"
                    if self.quota_warning_only:
                        logger.warning(f"配额警告: {error_msg}")
                        return True, None, quota_info
                    else:
                        logger.error(f"配额拦截: {error_msg}")
                        return False, error_msg, quota_info
            
            # 检查速率限制
            if self.enable_rate_limit and rps_limit:
                current_rps = self._get_current_rps(cursor, key_id)
                quota_info["current_rps"] = current_rps
                
                if current_rps >= rps_limit:
                    error_msg = f"速率超限: 当前RPS {current_rps}/{rps_limit}"
                    if self.rate_limit_warning_only:
                        logger.warning(f"速率警告: {error_msg}")
                        return True, None, quota_info
                    else:
                        logger.error(f"速率拦截: {error_msg}")
                        return False, error_msg, quota_info
            
            return True, None, quota_info
            
        except Exception as e:
            logger.error(f"配额检查失败: {e}")
            # 配额检查失败时，默认允许通过
            return True, None, {}
    
    def _get_daily_usage(self, cursor, key_id: int) -> int:
        """获取今日已使用的配额"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ai_user_call_log 
            WHERE key_id = %s 
            AND created_at >= %s 
            AND created_at < %s
        """, (key_id, today, tomorrow))
        
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def _get_current_rps(self, cursor, key_id: int) -> int:
        """获取当前RPS（每秒请求数）"""
        # 统计最近1秒内的请求数
        one_second_ago = datetime.now() - timedelta(seconds=1)
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ai_user_call_log 
            WHERE key_id = %s 
            AND created_at >= %s
        """, (key_id, one_second_ago))
        
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def record_usage(self, cursor, key_id: int, user_id: int) -> None:
        """记录使用量（在调用完成后调用）"""
        try:
            # 这里可以添加更详细的使用量统计
            # 比如记录token使用量、费用等
            logger.debug(f"记录使用量: key_id={key_id}, user_id={user_id}")
        except Exception as e:
            logger.error(f"记录使用量失败: {e}")


# 全局配额管理器实例
quota_manager = QuotaManager()


def check_quota_and_rate_limit(
    cursor, 
    key_id: int, 
    user_id: int
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    检查配额和速率限制的便捷函数
    
    Returns:
        (is_allowed, error_message, quota_info)
    """
    return quota_manager.check_quota_and_rate_limit(cursor, key_id, user_id)


def record_usage(cursor, key_id: int, user_id: int) -> None:
    """记录使用量的便捷函数"""
    quota_manager.record_usage(cursor, key_id, user_id) 
 