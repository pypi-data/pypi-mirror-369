# 一、安装

```shell
pip install lms_ubitraq
pip install django_object_actions
```

# 二、配置

```python
# settings.py
INSTALLED_APPS = [
    # 其他
    "django_object_actions",
    "lms_ubitraq",
]
```

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path("ubitraq/", include("lms_ubitraq.urls")),
]
```

# 三、页面

- 运行日志：/ubitraq/console/
- 标签终端：ubitraq/tag/
- 基站设施：ubitraq/anchor/
- 产品型号：ubitraq/product/
- 地图详情：ubitraq/map/
- 应用配置：ubitraq/config/