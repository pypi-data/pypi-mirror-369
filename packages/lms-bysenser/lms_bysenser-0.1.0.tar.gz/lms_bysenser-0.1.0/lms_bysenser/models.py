from django.db import models
from django.contrib.auth.models import User


class UserTimeTemp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(app_label)s_%(class)s_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(app_label)s_%(class)s_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        abstract = True


class Map(UserTimeTemp):
    name = models.CharField(max_length=100, unique=False, verbose_name="地图名称")
    floor = models.IntegerField(default=1, unique=False, verbose_name="楼层")
    wms = models.CharField(max_length=200, blank=True, null=True, verbose_name="地图url")
    layer_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="图层名称")
    bounds = models.CharField(max_length=200, blank=True, null=True, verbose_name="地图范围")

    class Meta:
        verbose_name = "地图信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Anchor(UserTimeTemp):
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="基站名称")
    map = models.ForeignKey(Map, on_delete=models.CASCADE, verbose_name="地图", related_name="anchor")
    is_online = models.BooleanField(default=False, verbose_name="是否在线")
    x = models.FloatField(default=0, verbose_name="横坐标")
    y = models.FloatField(default=0, verbose_name="纵坐标")
    z = models.FloatField(default=0, verbose_name="垂直坐标")

    class Meta:
        verbose_name = "基站信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(UserTimeTemp):
    name = models.CharField(max_length=20, unique=True, verbose_name="标签名称")
    voltag = models.IntegerField(default=0, blank=True, null=True, verbose_name="电量百分比")

    class Meta:
        verbose_name = "标签信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Config(UserTimeTemp):
    NAME_CHOICES = [
        ("HOST", "服务地址"),
        ("SECRET_KEY", "32位字符串密钥"),
        ("TIMESTAMP", "秒时间戳"),
        ("SALT", "4位随机字符"),
        ("HEART_BEAT", "心跳间隔"),
        ("HTTP_URL", "驱动地址"),
        ("DEVICE_TYPE", "设备型号"),
    ]
    name = models.CharField(max_length=100, unique=True, choices=NAME_CHOICES, verbose_name="配置项")
    value = models.CharField(max_length=100, unique=False, verbose_name="数据值")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        verbose_name = "应用配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
