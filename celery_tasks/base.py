import os
flask_env = os.environ.get("FLASK_DEBUG")

if flask_env == 'development':
    base_redis = "redis://ps_plag_redis:6379"
elif flask_env == 'product':
    base_redis = "redis://ps_plag_redis_pro:6379"
else:
    base_redis = "redis://127.0.0.1:6381"