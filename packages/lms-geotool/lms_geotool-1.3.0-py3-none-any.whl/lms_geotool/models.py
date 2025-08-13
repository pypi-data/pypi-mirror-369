from django.db import models
from django.contrib.auth.models import User


class UserTimeTemp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(app_label)s_%(class)s_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(app_label)s_%(class)s_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        abstract = True


class AffineMatrix(UserTimeTemp):
    mapid = models.CharField(max_length=20, unique=True, verbose_name="地图编码")
    name = models.CharField(max_length=20, unique=False, verbose_name="地图名称")
    floor = models.IntegerField(default=1, unique=False, verbose_name="楼层")
    matrix = models.CharField(max_length=200, editable=False, verbose_name="转换矩阵")

    class Meta:
        verbose_name = "地图信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Anchor(UserTimeTemp):
    map = models.ForeignKey(AffineMatrix, on_delete=models.CASCADE, related_name="anchor", verbose_name="地图信息")
    origin_x = models.FloatField(default=0, verbose_name="原坐标x")
    origin_y = models.FloatField(default=0, verbose_name="原坐标y")
    target_x = models.FloatField(default=0, verbose_name="目标坐标x")
    target_y = models.FloatField(default=0, verbose_name="目标坐标y")

    class Meta:
        verbose_name = "锚点信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return ""


class LinearRegression(UserTimeTemp):
    lrid = models.CharField(max_length=20, unique=False, verbose_name="规则编码")
    name = models.CharField(max_length=50, unique=False, verbose_name="规则名称")
    k = models.FloatField(editable=False, null=True, blank=True, verbose_name="权重")
    b = models.FloatField(editable=False, null=True, blank=True, verbose_name="偏置")

    class Meta:
        verbose_name = "线性回归"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SamplePoint(UserTimeTemp):
    regression = models.ForeignKey(LinearRegression, on_delete=models.CASCADE, related_name="samplepoint", verbose_name="线性回归")
    x = models.FloatField(default=0, verbose_name="特征变量")
    y = models.FloatField(default=0, verbose_name="目标变量")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        verbose_name = "样本点位"
        verbose_name_plural = verbose_name

    def __str__(self):
        return ""
