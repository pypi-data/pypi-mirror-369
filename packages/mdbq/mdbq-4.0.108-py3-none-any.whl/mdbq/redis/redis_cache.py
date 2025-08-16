# -*- coding: utf-8 -*-
"""
Redis智能缓存系统

主要功能：
1. Redis缓存的CRUD操作
2. 命名空间隔离
3. 分布式锁防止缓存击穿
4. 自动统计分析并提交到MySQL
5. 缓存健康检查和监控

"""

import json
import time
import threading
import socket
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import redis
from mdbq.log import mylogger
logger = mylogger.MyLogger(
    logging_mode='file',
    log_level='info',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,
    sample_rate=1,
    sensitive_fields=[],
    enable_metrics=False,
)


class CacheConfig:
    """缓存系统配置类"""
    
    def __init__(self, db_name: str = "redis统计", table_name: str = "dpflask路由分析"):
        # TTL配置（秒）
        self.default_ttl = 3600  # 1小时
        self.short_ttl = 300     # 5分钟
        self.medium_ttl = 1800   # 30分钟
        self.long_ttl = 7200     # 2小时
        self.very_long_ttl = 86400  # 24小时
        
        # 缓存键前缀
        self.cache_prefix = "smart_cache:"
        self.stats_prefix = "cache_stats:"
        self.lock_prefix = "cache_lock:"
        
        # 统计配置
        self.stats_interval = 1800  # 统计间隔（秒）, 自动提交统计信息到MySQL的间隔
        self.stats_retention = 7   # MySQL统计数据保留天数，超过此天数的数据将被自动删除
        
        # 性能配置
        self.max_key_length = 250
        self.max_value_size = 1024 * 1024  # 1MB
        self.batch_size = 100
        
        # MySQL数据库配置
        self.db_name = db_name
        self.table_name = table_name
        
        # 锁配置
        self.lock_timeout = 30     # 分布式锁超时时间
        self.lock_retry_delay = 0.1  # 锁重试延迟


class SmartCacheSystem:
    """智能缓存系统核心类"""
    
    def __init__(self, redis_client: redis.Redis, mysql_pool=None, instance_name: str = "default", 
                 config: CacheConfig = None, db_name: str = None, table_name: str = None):
        self.redis_client = redis_client
        self.mysql_pool = mysql_pool
        self.instance_name = instance_name
        
        # 配置优先级：传入的config > 自定义db_name/table_name > 默认配置
        if config:
            self.config = config
        elif db_name or table_name:
            self.config = CacheConfig(
                db_name=db_name or "redis统计",
                table_name=table_name or "dpflask路由分析"
            )
        else:
            self.config = CacheConfig()
            
        self.logger = logger
        
        # 统计数据
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
            'total_operations': 0,
            'start_time': time.time(),
            'response_times': []
        }
        
        # 热点键统计
        self.hot_keys = {}
        self.hot_keys_lock = threading.RLock()
        
        # 统计线程控制
        self._stats_running = False
        self._stats_thread = None
        self._stats_lock = threading.RLock()
        
        # 初始化
        self._init_mysql_db()
        self._start_stats_worker()
        
        self.logger.info("智能缓存系统初始化完成", {
            'instance_name': self.instance_name,
            'mysql_enabled': self.mysql_pool is not None,
            'redis_connected': self._test_redis_connection()
        })
    
    def _test_redis_connection(self) -> bool:
        """测试Redis连接"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Redis连接测试失败: {e}")
            return False
    
    def _init_mysql_db(self) -> bool:
        """初始化MySQL数据库和表"""
        if not self.mysql_pool:
            self.logger.warning("MySQL连接池未提供，统计功能将被禁用")
            return False
        
        try:
            connection = self.mysql_pool.connection()
            try:
                with connection.cursor() as cursor:
                    # 创建数据库
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.config.db_name}` DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
                    cursor.execute(f"USE `{self.config.db_name}`")
                    
                    # 创建表（MySQL 8.4+兼容语法）
                    create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS `{self.config.table_name}` (
                        `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
                        `日期` date NOT NULL COMMENT '统计日期',
                        `统计时间` datetime NOT NULL COMMENT '统计时间',
                        `时间段` varchar(20) NOT NULL COMMENT '时间段标识',
                        `缓存命中数` bigint DEFAULT 0 COMMENT '缓存命中次数',
                        `缓存未命中数` bigint DEFAULT 0 COMMENT '缓存未命中次数',
                        `缓存设置数` bigint DEFAULT 0 COMMENT '缓存设置次数',
                        `缓存删除数` bigint DEFAULT 0 COMMENT '缓存删除次数',
                        `缓存错误数` bigint DEFAULT 0 COMMENT '缓存错误次数',
                        `命中率` decimal(5,2) DEFAULT 0.00 COMMENT '缓存命中率(%)',
                        `总操作数` bigint DEFAULT 0 COMMENT '总操作次数',
                        `平均响应时间` decimal(10,4) DEFAULT 0.0000 COMMENT '平均响应时间(ms)',
                        `每秒操作数` decimal(10,2) DEFAULT 0.00 COMMENT '每秒操作数',
                        `唯一键数量` int DEFAULT 0 COMMENT '唯一键数量',
                        `系统运行时间` bigint DEFAULT 0 COMMENT '系统运行时间(秒)',
                        `热点键统计` json DEFAULT NULL COMMENT '热点键统计信息',
                        `服务器主机` varchar(100) DEFAULT NULL COMMENT '服务器主机名',
                        `实例名称` varchar(100) DEFAULT NULL COMMENT '缓存实例名称',
                        `创建时间` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                        `更新时间` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
                        PRIMARY KEY (`id`),
                        KEY `idx_stats_date` (`日期`),
                        KEY `idx_stats_time` (`统计时间`),
                        KEY `idx_time_period` (`时间段`),
                        KEY `idx_hit_rate` (`命中率`),
                        KEY `idx_instance` (`实例名称`),
                        KEY `idx_create_time` (`创建时间`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Redis缓存系统统计分析表'
                    """
                    
                    cursor.execute(create_table_sql)
                    connection.commit()
                    
                    self.logger.info("MySQL数据库表初始化成功", {
                        'database': self.config.db_name,
                        'table': self.config.table_name
                    })
                    return True
                    
            finally:
                connection.close()
                
        except Exception as e:
            self.logger.error(f"MySQL数据库初始化失败: {e}")
            return False
    
    def _generate_cache_key(self, key: str, namespace: str = "") -> str:
        """生成缓存键"""
        if namespace:
            return f"{self.config.cache_prefix}{namespace}:{key}"
        return f"{self.config.cache_prefix}{key}"
    
    def _record_operation(self, operation: str, response_time: float = 0):
        """记录操作统计"""
        with self._stats_lock:
            self.stats['total_operations'] += 1
            if operation in self.stats:
                self.stats[operation] += 1
            if response_time > 0:
                self.stats['response_times'].append(response_time)
                # 只保留最近1000次操作的响应时间
                if len(self.stats['response_times']) > 1000:
                    self.stats['response_times'] = self.stats['response_times'][-1000:]
    
    def _record_hot_key(self, key: str, namespace: str = ""):
        """记录热点键"""
        cache_key = self._generate_cache_key(key, namespace)
        with self.hot_keys_lock:
            self.hot_keys[cache_key] = self.hot_keys.get(cache_key, 0) + 1
    
    def get(self, key: str, namespace: str = "", default=None) -> Any:
        """获取缓存值"""
        start_time = time.time()
        
        try:
            cache_key = self._generate_cache_key(key, namespace)
            
            # 获取缓存值
            value = self.redis_client.get(cache_key)
            response_time = (time.time() - start_time) * 1000
            
            if value is not None:
                # 缓存命中
                self._record_operation('hits', response_time)
                self._record_hot_key(key, namespace)
                
                try:
                    return json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return value.decode('utf-8')
            else:
                # 缓存未命中
                self._record_operation('misses', response_time)
                return default
                
        except Exception as e:
            self._record_operation('errors')
            self.logger.error(f"缓存获取失败: {e}", {
                'key': key,
                'namespace': namespace
            })
            return default
    
    def set(self, key: str, value: Any, ttl: int = None, namespace: str = "") -> bool:
        """设置缓存值"""
        start_time = time.time()
        
        try:
            cache_key = self._generate_cache_key(key, namespace)
            ttl = ttl or self.config.default_ttl
            
            # 序列化值
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            # 检查值大小
            if len(serialized_value.encode('utf-8')) > self.config.max_value_size:
                self.logger.warning(f"缓存值过大，跳过设置: {len(serialized_value)} bytes")
                return False
            
            # 设置缓存
            result = self.redis_client.setex(cache_key, ttl, serialized_value)
            response_time = (time.time() - start_time) * 1000
            
            self._record_operation('sets', response_time)
            return bool(result)
            
        except Exception as e:
            self._record_operation('errors')
            self.logger.error(f"缓存设置失败: {e}", {
                'key': key,
                'namespace': namespace,
                'ttl': ttl
            })
            return False
    
    def delete(self, key: str, namespace: str = "") -> bool:
        """删除缓存值"""
        start_time = time.time()
        
        try:
            cache_key = self._generate_cache_key(key, namespace)
            result = self.redis_client.delete(cache_key)
            response_time = (time.time() - start_time) * 1000
            
            self._record_operation('deletes', response_time)
            return bool(result)
            
        except Exception as e:
            self._record_operation('errors')
            self.logger.error(f"缓存删除失败: {e}", {
                'key': key,
                'namespace': namespace
            })
            return False
    
    def exists(self, key: str, namespace: str = "") -> bool:
        """检查缓存键是否存在"""
        try:
            cache_key = self._generate_cache_key(key, namespace)
            return bool(self.redis_client.exists(cache_key))
        except Exception as e:
            self.logger.error(f"缓存存在性检查失败: {e}")
            return False
    
    def clear_namespace(self, namespace: str) -> int:
        """清除指定命名空间的所有缓存"""
        try:
            pattern = f"{self.config.cache_prefix}{namespace}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.logger.info(f"清除命名空间缓存: {namespace}, 删除键数: {deleted}")
                return deleted
            return 0
            
        except Exception as e:
            self.logger.error(f"清除命名空间缓存失败: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._stats_lock:
            total_ops = self.stats['total_operations']
            hits = self.stats['hits']
            
            # 计算命中率
            hit_rate = (hits / total_ops * 100) if total_ops > 0 else 0
            
            # 计算平均响应时间
            response_times = self.stats['response_times']
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # 计算运行时间
            uptime = time.time() - self.stats['start_time']
            
            # 计算每秒操作数
            ops_per_second = total_ops / uptime if uptime > 0 else 0
            
            # 获取热点键（前10个）
            with self.hot_keys_lock:
                top_hot_keys = sorted(self.hot_keys.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'hits': hits,
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'errors': self.stats['errors'],
                'total_operations': total_ops,
                'hit_rate': round(hit_rate, 2),
                'avg_response_time': round(avg_response_time, 4),
                'ops_per_second': round(ops_per_second, 2),
                'uptime_seconds': int(uptime),
                'hot_keys': dict(top_hot_keys),
                'unique_keys_count': len(self.hot_keys)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_info = {
            'redis_connected': False,
            'mysql_available': False,
            'stats_worker_running': self._stats_running,
            'instance_name': self.instance_name,
            'timestamp': datetime.now().isoformat()
        }
        
        # 检查Redis连接
        try:
            self.redis_client.ping()
            health_info['redis_connected'] = True
        except Exception as e:
            health_info['redis_error'] = str(e)
        
        # 检查MySQL连接
        if self.mysql_pool:
            try:
                connection = self.mysql_pool.connection()
                connection.close()
                health_info['mysql_available'] = True
            except Exception as e:
                health_info['mysql_error'] = str(e)
        
        return health_info
    
    def _start_stats_worker(self):
        """启动统计工作线程"""
        if not self._stats_running:
            self._stats_running = True
            self._stats_thread = threading.Thread(target=self._stats_worker, daemon=True)
            self._stats_thread.start()
            self.logger.info("统计工作线程已启动")
    
    def _stats_worker(self):
        """后台统计工作线程"""
        cleanup_counter = 0  # 清理计数器
        while self._stats_running:
            try:
                # 收集统计数据
                stats_data = self.get_stats()
                
                # 提交到MySQL
                self._submit_stats_to_mysql(stats_data)
                
                # 清理过期的热点键统计
                self._cleanup_hot_keys()
                
                # 每24次统计周期（约2小时）执行一次过期数据清理
                cleanup_counter += 1
                if cleanup_counter >= 24:  # 24 * 300秒 = 2小时
                    self._cleanup_expired_mysql_data()
                    cleanup_counter = 0
                
            except Exception as e:
                self.logger.error(f"统计工作线程异常: {e}")
            
            # 等待下一个统计间隔
            time.sleep(self.config.stats_interval)
    
    def _submit_stats_to_mysql(self, stats_data: Dict[str, Any]):
        """提交统计数据到MySQL"""
        if not self.mysql_pool:
            self.logger.debug("MySQL连接池不可用，跳过统计数据提交")
            return
        
        try:
            connection = self.mysql_pool.connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"USE `{self.config.db_name}`")
                    
                    # 准备数据
                    now = datetime.now()
                    date_str = now.strftime("%Y-%m-%d")  # 格式: 2024-10-01
                    time_period = now.strftime("%Y%m%d_%H%M")
                    
                    insert_sql = f"""
                    INSERT INTO `{self.config.table_name}` (
                        `日期`, `统计时间`, `时间段`, `缓存命中数`, `缓存未命中数`, `缓存设置数`,
                        `缓存删除数`, `缓存错误数`, `命中率`, `总操作数`, `平均响应时间`,
                        `每秒操作数`, `唯一键数量`, `系统运行时间`, `热点键统计`,
                        `服务器主机`, `实例名称`
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """
                    
                    cursor.execute(insert_sql, (
                        date_str,
                        now,
                        time_period,
                        stats_data['hits'],
                        stats_data['misses'],
                        stats_data['sets'],
                        stats_data['deletes'],
                        stats_data['errors'],
                        stats_data['hit_rate'],
                        stats_data['total_operations'],
                        stats_data['avg_response_time'],
                        stats_data['ops_per_second'],
                        stats_data['unique_keys_count'],
                        stats_data['uptime_seconds'],
                        json.dumps(stats_data['hot_keys'], ensure_ascii=False),
                        socket.gethostname(),
                        self.instance_name
                    ))
                    
                    connection.commit()
                    
                    self.logger.debug("统计数据已提交到MySQL", {
                        'time_period': time_period,
                        'total_operations': stats_data['total_operations'],
                        'hit_rate': stats_data['hit_rate']
                    })
                    
            finally:
                connection.close()
                
        except Exception as e:
            self.logger.error(f"提交统计数据到MySQL失败: {e}")
    
    def _cleanup_hot_keys(self):
        """清理热点键统计（保留访问次数最高的1000个）"""
        with self.hot_keys_lock:
            if len(self.hot_keys) > 1000:
                # 保留访问次数最高的1000个键
                sorted_keys = sorted(self.hot_keys.items(), key=lambda x: x[1], reverse=True)
                self.hot_keys = dict(sorted_keys[:1000])
    
    def _cleanup_expired_mysql_data(self):
        """清理过期的MySQL统计数据"""
        if not self.mysql_pool:
            return
        
        try:
            connection = self.mysql_pool.connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"USE `{self.config.db_name}`")
                    
                    # 计算过期时间点
                    from datetime import timedelta
                    expire_date = datetime.now() - timedelta(days=self.config.stats_retention)
                    
                    # 删除过期数据
                    delete_sql = f"""
                    DELETE FROM `{self.config.table_name}` 
                    WHERE `统计时间` < %s
                    """
                    
                    cursor.execute(delete_sql, (expire_date,))
                    deleted_rows = cursor.rowcount
                    connection.commit()
                    
                    if deleted_rows > 0:
                        self.logger.info("清理过期MySQL统计数据", {
                            'deleted_rows': deleted_rows,
                            'expire_date': expire_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'retention_days': self.config.stats_retention
                        })
                    
            finally:
                connection.close()
                
        except Exception as e:
            self.logger.error(f"清理过期MySQL统计数据失败: {e}")
    
    def shutdown(self):
        """关闭缓存系统"""
        self.logger.info("正在关闭缓存系统...")
        
        # 停止统计线程
        self._stats_running = False
        if self._stats_thread and self._stats_thread.is_alive():
            self._stats_thread.join(timeout=5)
        
        # 最后一次提交统计数据
        try:
            stats_data = self.get_stats()
            self._submit_stats_to_mysql(stats_data)
        except Exception as e:
            self.logger.error(f"关闭时提交统计数据失败: {e}")
        
        self.logger.info("缓存系统已关闭")


class CacheManager:
    """缓存管理器 - 单例模式"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.cache_instance = None
        self.enabled = True
        self.initialization_error = None
        self._initialized = True
        self.logger = logger
    
    def initialize(self, redis_client: redis.Redis, mysql_pool=None, instance_name: str = "default",
                   config: CacheConfig = None, db_name: str = None, table_name: str = None):
        """初始化缓存系统"""
        try:
            self.cache_instance = SmartCacheSystem(
                redis_client=redis_client,
                mysql_pool=mysql_pool,
                instance_name=instance_name,
                config=config,
                db_name=db_name,
                table_name=table_name
            )
            self.initialization_error = None
            self.logger.info("缓存管理器初始化成功", {
                'instance_name': instance_name,
                'mysql_enabled': mysql_pool is not None,
                'db_name': self.cache_instance.config.db_name,
                'table_name': self.cache_instance.config.table_name
            })
            return self  # 支持链式调用
            
        except Exception as e:
            self.initialization_error = str(e)
            self.cache_instance = None
            self.logger.error(f"缓存管理器初始化失败: {e}")
            return self
    
    def get_cache(self) -> Optional[SmartCacheSystem]:
        """获取缓存实例"""
        return self.cache_instance if self.enabled else None
    
    def is_available(self) -> bool:
        """检查缓存是否可用"""
        return self.cache_instance is not None and self.enabled
    
    def enable(self):
        """启用缓存"""
        self.enabled = True
        self.logger.info("缓存系统已启用")
        return self  # 支持链式调用
    
    def disable(self):
        """禁用缓存"""
        self.enabled = False
        self.logger.info("缓存系统已禁用")
        return self  # 支持链式调用
    
    def get_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        return {
            'enabled': self.enabled,
            'available': self.cache_instance is not None,
            'initialization_error': self.initialization_error,
            'instance_name': getattr(self.cache_instance, 'instance_name', None) if self.cache_instance else None
        }
    
    def shutdown(self):
        """关闭缓存系统"""
        if self.cache_instance:
            self.cache_instance.shutdown()
            self.cache_instance = None
        self.logger.info("缓存管理器已关闭")


# 导出单例实例
cache_manager = CacheManager() 