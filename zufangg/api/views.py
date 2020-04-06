import datetime
from datetime import timezone

import jwt
from django.core.cache import caches
from django.db.models import Prefetch, Q
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django_redis import get_redis_connection
from rest_framework.decorators import api_view, throttle_classes, action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.consts import CODE_TOO_FREQUENCY, MOBILE_CODE_SUCCESS, INVALID_TEL_NUM, USER_LOGIN_SUCCESS, USER_LOGIN_FAILED, \
    INVALID_LOGIN_INFO
from api.helpers import AgentCursorPagination, EstateFilterSet, HouseInfoFilterSet, check_tel, DefaultResponse
from api.serializers import *
from common.models import District, Agent, HouseType, User, LoginLog
from common.utils import gen_mobile_code, send_sms_by_luosimao, to_md5_hex, get_ip_address, upload_stream_to_qiniu
from zufang.settings import SECRET_KEY
# from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel



@api_view(('GET', ))
# @authentication_classes((LoginRequiredAuthentication, ))
def get_payment_page(request, houseid):
    # https://opendocs.alipay.com/apis/api_1/alipay.trade.page.pay
    model = AlipayTradePagePayModel()
    # 产品订单号
    model.out_trade_no = '202003051646520001'
    # 订单总金额
    model.total_amount = 200
    # 订单主题
    model.subject = '租房订金'
    # model.body = '支付宝测试'
    # 销售产品码，与支付宝签约的产品码名称。 注：目前仅支持FAST_INSTANT_TRADE_PAY
    model.product_code = 'FAST_INSTANT_TRADE_PAY'
    # 结算详细信息
    settle_detail_info = SettleDetailInfo()
    settle_detail_info.amount = 200
    # 结算收款方的账户类型
    settle_detail_info.trans_in_type = 'cardAliasNo'
    # 结算收款方
    settle_detail_info.trans_in = '6216603100004601162'
    settle_detail_infos = list()
    settle_detail_infos.append(settle_detail_info)
    # 结算信息
    settle_info = SettleInfo()
    settle_info.settle_detail_infos = settle_detail_infos
    model.settle_info = settle_info
    # sub_merchant = SubMerchant()
    # sub_merchant.merchant_id = '2088102180149774'
    # model.sub_merchant = sub_merchant
    request = AlipayTradePagePayRequest(biz_model=model)
    url = alipay_client.page_execute(request, http_method='GET')
    # 此处应该补充生成交易流水的代码 ---> Model
    # 将用户信息、房源信息、交易编号、交易金额、交易时间、交易状态、……写入数据库

    # 还需要一个设计一个接口作为接收通知的接口其中包括对订单交易结果的查询
    # 最后还要更新之前的交易流水信息
    # request = AlipayTradeQueryRequest(biz_model=model)
    # content = alipay_client.page_execute(request)
    return DefaultResponse(data={'url': url})


@api_view(('POST', ))
def upload_house_photo(request):
    file_obj = request.FILES.get('mainphoto')
    if file_obj and len(file_obj) < MAX_PHOTO_SIZE:
        prefix = to_md5_hex(file_obj.file)
        filename = f'{prefix}{os.path.splitext(file_obj.name)[1]}'
        upload_stream_to_qiniu.delay(file_obj, filename, len(file_obj))
        photo = HousePhoto()
        photo.path = f'http://q69nr46pe.bkt.clouddn.com/{filename}'
        photo.ismain = True
        photo.save()
        resp = DefaultResponse(*FILE_UPLOAD_SUCCESS, data={
            'photoid': photo.photoid,
            'url': photo.path
        })
    else:
        resp = DefaultResponse(*FILE_SIZE_EXCEEDED)
    return resp


@api_view(('GET', ))
def get_code_by_sms(request, tel):
    """获取短信验证码"""
    if check_tel(tel):
        if caches['default'].get(tel):
            resp = DefaultResponse(*CODE_TOO_FREQUENCY)
        else:
            code = gen_mobile_code()
            message = f'您的短信验证码是{code}，打死也不能告诉别人哟！【Python小课】'
            # 通过异步化函数的delay方法让函数异步化的执行，这个地方就相当于是消息的生产者
            # 如果要完成这个任务还需要消息的消费者，需要其他的进程来处理掉这条消息
            # 消费者跟生产者可以是不同的机器（通常情况下也是如此）
            # celery -A zufang worker -l debug
            # send_sms_by_luosimao.delay(tel, message)
            # task = send_sms_by_luosimao.s(countdown=10, expires=60)
            # task.delay(tel, message)
            send_sms_by_luosimao.apply_async(
                (tel, message),
                # {'tel': tel, 'message': message},
                queue='queue1',
                countdown=10,
                # retry_policy={},
                # expires=60,
                # compression='zlib',
            )
            caches['default'].set(tel, code, timeout=120)
            resp = DefaultResponse(*MOBILE_CODE_SUCCESS)
    else:
        resp = DefaultResponse(*INVALID_TEL_NUM)
    return resp


@api_view(('POST', ))
def login(request):
    """登录（获取用户身份令牌）"""
    username = request.data.get('username')
    password = request.data.get('password')
    if username and password:
        password = to_md5_hex(password)
        user = User.objects.filter(
            Q(username=username, password=password) |
            Q(tel=username, password=password) |
            Q(email=username, password=password)
        ).first()
        if user:
            # 用户登录成功通过JWT生成用户身份令牌
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'data': {'userid': user.userid, }
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode()
            with atomic():
                current_time = timezone.now()
                if not user.lastvisit or \
                        (current_time - user.lastvisit).days >= 1:
                    user.point += 2
                    user.lastvisit = current_time
                    user.save()
                loginlog = LoginLog()
                loginlog.user = user
                loginlog.logdate = current_time
                loginlog.ipaddr = get_ip_address(request)
                loginlog.save()
            resp = DefaultResponse(*USER_LOGIN_SUCCESS, data={'token': token})
        else:
            resp = DefaultResponse(*USER_LOGIN_FAILED)
    else:
        resp = DefaultResponse(*INVALID_LOGIN_INFO)
    return resp


def logout(request):
    """注销（销毁用户身份令牌）"""
    # 如果使用了JWT这种方式通过令牌进行用户身份认证
    # 如何彻底让令牌失效??? ---> Redis用集合类型做一个失效令牌清单
    # 定时任务从失效令牌清单中清理过期令牌避免集合元素过多
    pass


@cache_page(timeout=365 * 86400)
@api_view(('GET', ))
def get_provinces(request):
    """获取省级行政单位"""
    queryset = District.objects.filter(parent__isnull=True)\
        .only('name')
    serializer = DistrictSimpleSerializer(queryset, many=True)
    return Response({
        'code': 10000,
        'message': '获取省级行政区域成功',
        'results': serializer.data
    })


# @api_view(('GET', ))
# def get_district(request, distid):
#     """获取地区详情"""
#     district = caches['default'].get(f'district:{distid}')
#     if district is None:
#         district = District.objects.filter(distid=distid).first()
#         caches['default'].set(f'district:{distid}', district, timeout=900)
#     serializer = DistrictDetailSerializer(district)
#     return Response(serializer.data)


@api_view(('GET', ))
def get_district(request, distid):
    """获取地区详情"""
    redis_cli = get_redis_connection()
    data = redis_cli.get(f'zufang:district:{distid}')
    if data:
        data = json.loads(data)
    else:
        district = District.objects.filter(distid=distid)\
            .defer('parent').first()
        data = DistrictDetailSerializer(district).data
        redis_cli.set(f'zufang:district:{distid}', json.dumps(data), ex=900)
    return Response(data)


@method_decorator(decorator=cache_page(timeout=86400), name='get')
class HotCityView(ListAPIView):
    """热门城市视图"""
    queryset = District.objects.filter(ishot=True).only('distid', 'name')
    serializer_class = DistrictSimpleSerializer
    pagination_class = None


# class AgentView(RetrieveUpdateAPIView, ListCreateAPIView):
#     """经理人视图"""
#     # pagination_class = AgentCursorPagination

    # def get_queryset(self):
    #     queryset = Agent.objects.all()
    #     name = self.request.GET.get('name')
    #     if name:
    #         queryset = queryset.filter(name__startswith=name)
    #     servstar = self.request.GET.get('servstar')
    #     if servstar:
    #         queryset = queryset.filter(servstar__gte=servstar)
    #     if 'pk' not in self.kwargs:
    #         queryset = queryset.only('name', 'tel', 'servstar')
    #     else:
    #         queryset = queryset.prefetch_related(
    #             Prefetch('estates',
    #                      queryset=Estate.objects.all().only('name').order_by('-hot'))
    #         )
    #     return queryset.order_by('-servstar')
    #
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return AgentCreateSerializer
    #     else:
    #         return AgentDetailSerializer if 'pk' in self.kwargs else AgentSimpleSerializer
    #
    # def get(self, request, *args, **kwargs):
    #     cls = RetrieveUpdateAPIView if 'pk' in kwargs else ListCreateAPIView
    #     return cls.get(self, request, *args, **kwargs)

@method_decorator(decorator=cache_page(timeout=120), name='list')
@method_decorator(decorator=cache_page(timeout=300), name='retrieve')
class AgentViewSet(ModelViewSet):
    """经理人视图"""
    queryset = Agent.objects.all()

    def get_queryset(self):
        name = self.request.GET.get('name')
        if name:
            self.queryset = self.queryset.filter(name__startswith=name)
        servstar = self.request.GET.get('servstar')
        if servstar:
            self.queryset = self.queryset.filter(servstar__gte=servstar)
        if self.action == 'list':
            self.queryset = self.queryset.only('name', 'tel', 'servstar')
        else:
            self.queryset = self.queryset.prefetch_related(
                Prefetch('estates',
                         queryset=Estate.objects.all().only('name').order_by('-hot'))
            )
        return self.queryset.order_by('-servstar')

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return AgentCreateSerializer
        return AgentDetailSerializer if self.action == 'retrieve' \
            else AgentSimpleSerializer


@method_decorator(decorator=cache_page(timeout=86400), name='list')
@method_decorator(decorator=cache_page(timeout=86400), name='retrieve')
class HouseTypeViewSet(ModelViewSet):
    """户型视图集"""
    queryset = HouseType.objects.all()
    serializer_class = HouseTypeSerializer
    pagination_class = None


@method_decorator(decorator=cache_page(timeout=3600), name='list')
class TagViewSet(ModelViewSet):
    """房源标签视图集"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@method_decorator(decorator=cache_page(timeout=86400), name='list')
@method_decorator(decorator=cache_page(timeout=86400), name='retrieve')
class EstateViewSet(ReadOnlyModelViewSet):
    """楼盘视图集"""
    queryset = Estate.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    # filter_fields = ('name', 'hot', 'district')
    filterset_class = EstateFilterSet
    ordering = '-hot'
    ordering_fields = ('district', 'hot', 'name')

    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.only('name')
        else:
            queryset = self.queryset\
                .defer('district__parent', 'district__ishot', 'district__intro')\
                .select_related('district')
        return queryset

    def get_serializer_class(self):
        # 如果用三目表达式可代替下边的代码
        # return EstateDetailSerializer if self.action == 'retrieve' else EstateSimpleSerializer
        if self.action in ('create', 'update'):
            return EstateCreateSerializer
        return EstateDetailSerializer if self.action == 'retrieve' \
            else EstateSimpleSerializer

@method_decorator(decorator=cache_page(timeout=120), name='list')
@method_decorator(decorator=cache_page(timeout=300), name='retrieve')
class HouseInfoViewSet(ModelViewSet):
    """房源视图集"""
    queryset = HouseInfo.objects.all()
    serializer_class = HouseInfoDetailSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = HouseInfoFilterSet
    ordering = ('-pubdate', )
    ordering_fields = ('pubdate', 'price')

    @action(methods=('GET', ), detail=True)
    def photos(self, request, pk):
        queryset = HousePhoto.objects.filter(house=self.get_object())
        return Response(HousePhotoSerializer(queryset, many=True).data)


    def get_queryset(self):
        if self.action == 'list':
            return self.queryset\
                .only('houseid', 'title', 'area', 'floor', 'totalfloor', 'price',
                      'mainphoto', 'priceunit', 'street', 'type',
                      'district_level3__distid', 'district_level3__name')\
                .select_related('district_level3', 'type')\
                .prefetch_related('tags')
        return self.queryset\
            .defer('user', 'district_level2',
                   'district_level3__parent', 'district_level3__ishot', 'district_level3__intro',
                   'estate__district', 'estate__hot', 'estate__intro',
                   'agent__realstar', 'agent__profstar', 'agent__certificated')\
            .select_related('district_level3', 'type', 'estate', 'agent')\
            .prefetch_related('tags')

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return HouseInfoCreateSerializer
        return HouseInfoDetailSerializer if self.action == 'retrieve' \
            else HouseInfoSimpleSerializer

class UserViewSet(ModelViewSet):
    """用户模型视图集"""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update':
            return UserUpdateSerializer
        return UserSimpleSerializer
