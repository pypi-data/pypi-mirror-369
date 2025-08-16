from common_cache import Cache

# 程序运行缓存默认的超时时间为30天
local_cache = Cache(expire=60 * 60 * 24 * 30)
