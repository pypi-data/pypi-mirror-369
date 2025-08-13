from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse

from django_object_actions import DjangoObjectActions, action

from .models import AffineMatrix, Anchor, LinearRegression, SamplePoint
from .tools.matrix import affine_matrix, calc_polyfit


class AnchorChoiceInline(admin.TabularInline):
    model = Anchor
    extra = 0


@admin.register(AffineMatrix)
class AffineMatrixAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ("mapid", "name", "floor", "matrix_html")
    changelist_actions = ('get_matrix',)

    @action(label="矩阵计算")
    def get_matrix(self, request, queryset):
        try:
            for each in queryset:
                anchors = each.anchor.all()
                source_data = [[each.origin_x, each.origin_y] for each in anchors]
                target_data = [[each.target_x, each.target_y] for each in anchors]
                matrix_result = affine_matrix(source_data, target_data)
                each.matrix = matrix_result
                each.save()
            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"{e}", messages.ERROR)

    def matrix_html(self, obj):
        if obj.matrix:
            path = reverse("matrix")
            full_url = f"{path}?mapid={obj.mapid}"
            res = f'<a href="{full_url}">查看</a>'
            # res = f"<a href='/geotool/matrix?mapid={obj.mapid}'>查看</a>"
            return format_html(res)
        else:
            res = f"<span style='color:red'>暂未转换</span>"
            return format_html(res)

    matrix_html.short_description = '矩阵计算'

    fieldsets = [
        ("地图信息", {"fields": ["mapid", "name", "floor"]}),
    ]

    inlines = [AnchorChoiceInline]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change == False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class SamplePointChoiceInline(admin.TabularInline):
    model = SamplePoint
    extra = 0


@admin.register(LinearRegression)
class LinearRegressionAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ("lrid", "name", "k", "b", "regression_html")
    changelist_actions = ('get_regression',)

    @action(label="回归计算")
    def get_regression(self, request, queryset):
        try:
            for each in queryset:
                samplepoint = each.samplepoint.filter(is_valid=True).all()
                data_list = [[each.x, each.y] for each in samplepoint]
                k, b = calc_polyfit(data_list)
                each.k = k
                each.b = b
                each.save()
            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"{e}", messages.ERROR)

    def regression_html(self, obj):
        if obj.k and obj.b:
            path = reverse("regression")
            full_url = f"{path}?lrid={obj.lrid}"
            res = f'<a href="{full_url}">查看</a>'
            return format_html(res)
        else:
            res = f"<span style='color:red'>暂未计算</span>"
            return format_html(res)

    regression_html.short_description = '回归计算'

    fieldsets = [
        ("基础信息", {"fields": ["lrid", "name"]}),
    ]

    inlines = [SamplePointChoiceInline]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change == False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
