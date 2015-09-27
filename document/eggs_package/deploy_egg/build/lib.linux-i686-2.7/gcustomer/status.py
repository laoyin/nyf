#coding=utf-8
from django.utils.translation import ugettext as _
status_collection = {
    '1111':_(u'服务器繁忙'),
    '0000':_(u'用户未登录'),
    '0001':'Everything is OK',
    '0002':_(u'用户不存在'),
    '0003':_(u'密码错误'),
    '0004':_(u'评论失败，没有权限'),
    '0005':_(u'已评论'),
    '0006':_(u'用户已存在'),
    '0007':_(u'暂无数据'),
    '0008':_(u'没有更多数据'),
    '0009':_(u'创建订单出错，订单创建失败'),
    '0010':_(u'订单查询出错，未能找到订单'),
    '0011':_(u'积分不足'),
    '0012':_(u'两次密码不一致'),
    '0013':_(u'加油卡不存在'),
    '0014':_(u'当前已经离线'),
    '0015':_(u'修改支付密码错误'),
    '0016':_(u'余额不足'),
    '0017':_(u'加油卡支付失败'),
    '0018':_(u'充值失败'),
    '0019':_(u'获取订单详情失败'),
    '0020':_(u'收银员不存在'),
    '0021':_(u'删除订单失败'),
    '0022':_(u'修改订单状态失败'),
    '0023':_(u'上传图片失败'),
    '0024':_(u'修改用户信息失败'),
    '0025':_(u'石油公司已关联'),
    '0026':_(u'用户身份证信息格式错误'),
    '0027':_(u'查询油站失败'),
    '0028':_(u'查询指定油站的油品失败'),
    '0029':_(u'获取附近失败'),
    '0030':_(u'获取便利店热销商品失败'),
    '0031':_(u'获取救援电话失败'),
    '0032':_(u'用户身份验证错误'),
    '0033':_(u'获取广告周期设置失败'),
    '0034':_(u'查询广告失败'),
    '0035':_(u'查询Gcustomer用户信息失败'),
    '0036':_(u'广告查看记录失败'),
    '0037':_(u'记录行车轨迹失败'),
    '0038':_(u'注册错误'),
    '0039':_(u'请求方法错误'),
    '0040':_(u'用户在其它地方登录'),
    '0041':_(u'存储用户身份证号失败'),
    '0042':_(u'绑定加油卡失败'),
    '0043':_(u'请先办理虚拟卡业务'),
    '0044':_(u'查询绑定卡失败'),
    '0045':_(u'查询公司失败'),
    '0046':_(u'验证用户和卡关联信息失败'),
    '0047':_(u'解除卡绑定失败'),
    '0048':_(u'注册公司失败'),
    '0049':_(u'关联石油公司失败'),
    '0050':_(u'查询账户失败'),
    '0051':_(u'站点信息与石油公司信息不匹配'),
    '0052':_(u'查询油品信息失败'),
    '0053':_(u'交易类型错误'),
    '0054':_(u'确认订单失败'),
    '0055':_(u'该石油公司已关联'),
    '0056':_(u'查询石油公司信息失败'),
    '0057':_(u'订单已完成'),
    '0058':_(u'调用消息服务器发送消息失败'),
    '0059':_(u'查询用户群信息失败'),
    '0060':_(u'创建用户群失败'),
    '0061':_(u'计算用户群聚合信息失败'),
    '0062':_(u'已创建相同的用户群'),
    '0063':_(u'订单还未支付'),
    '0064':_(u'加密错误'),
    '0065':_(u'解密错误'),
    '0066':_(u'激活虚拟卡失败'),
    '0067':_(u'虚拟卡已激活'),
    '0068':_(u'md5加密失败'),
    '0069':_(u'查询油站工作人员失败'),
    '0070':_(u'更新订单信息失败'),
    '0071':_(u'订单类型错误'),
    '0072':_(u'等待审核'),
    '0073':_(u'查询商品信息失败'),
    '0074':_(u'查询车后服务信息失败'),
    '0075':_(u'查询营销活动失败'),
    '0076':_(u'查询用户公司信息失败'),
    '0077':_(u'查询用户失败'),
    '0078':_(u'修改石油公司用户类型失败'),
    '0079':_(u'修改app用户类型失败'),
    '0080':_(u'解除绑定卡失败'),
    '0081':_(u'加油卡已绑定'),
    '0082':_(u'获取加油流失客户油站信息失败'),
    '0083':_(u'获取高峰期油站列表失败'),
    '0084':_(u"没有加油流失客户"),
    '0085':_(u"预订不可以支付"),
    '0086':_(u'油站信息不一致,收银员无法确认'),
    '0087':_(u'没有退款订单'),
    '0088':_(u'操作退款失败'),
    '0089':_(u'已提交退款申请'),
    '0090':_(u'退款申请失败'),
    '0091':_(u'用户订单信息不匹配'),
    '0092':_(u'申请已提交或未支付'),
    '0093':_(u'微信支付失败'),
    '0094':_(u'添加油站失败'),
    '0095':_(u'油站已存在'),
    '0096':_(u'没有权限'),
    '0097':_(u'删除目标用户群失败'),
    '0098':_(u'修改登录密码失败'),
    '0099':_(u'原错误密码'),
    '0100':_(u'意见反馈内容长度不合法'),
    '0101':_(u'意见反馈包含敏感信息'),
    '0102':_(u'用户名或密码格式错误'),
}

class Status :
    UNKNOWNERR                        = '1111'
    LOGINSUCCESS                       = '0001'
    OK                                           = '0001'
    USERNOTEXIST                        = '0002'
    PASSWORDERROR                   = '0003'
    WITHOUTPERMISSION            = '0004'
    HAVECOMMENTS                    = '0005'
    USEREXIST                               = '0006'
    NODATA                                  = '0007'
    NOMOREDATA                         = '0008'
    CREATE_ORDER_ERROR             = '0009'
    QUERY_ORDER_ERROR              = '0010'
    GOODS_SCORE_ERROR              = '0011'
    PASSWORDINCONSISTENT        = '0012'
    PUMPCARDNOTEXIST                = '0013'
    NOTLOGGEDIN                         = '0014'
    MODIFYPAYPASSWORDERROR  = '0015'
    CURRENTBALANCEDEFICENTCY = '0016'
    PAYBYOILCARDERRO                 = '0017'
    RECHARGEERROR                      = '0018'
    GET_ORDER_INFO_ERROR         = '0019'
    GasWorkerNOTEXIST                = '0020'
    DELETE_ORDER_ERROR              = '0021'
    ALTER_ORDER_STATUS_ERROR   = '0022'
    UPLOAD_IMAGE_ERROR            = '0023'
    ALTER_USER_ERROR                  = '0024'
    PUMP_CARD_HAS_EXIST            = '0025'
    ID_CARD_FORMAT_ERROR          = '0026'
    QUERY_SITE_ERROR                   = '0027'
    QUERY_SITE_FUEL_ERROR          = '0028'
    QUERY_NEAR_INFO_ERROR        = '0029'
    GET_STORE_HOT_GOODS_ERROR = '0030'
    QUERY_HELP_PHONE_ERROR       = '0031'
    USER_ID_CARD_CHECK_ERROR     = '0032'
    GET_ADVERTISE_SETTING_ERROR  = '0033'
    QUERY_ADVERTISE_ERROR             = '0034'
    QUERY_CUSTOMER_ERROR            = '0035'
    ADVERTISEMENT_RECORD             = '0036'
    DRIN_TRACE_RECORD_ERROR         = '0037'
    REGISTER_ERROR                           = '0038'
    REQMETHODERROR                       = '0039'
    LOGINED_ON_OTHER_SIDE            = '0040'
    SAVE_USER_ID_CARD_ERROR          = '0041'
    BIND_PUMP_CARD_ERROR             = '0042'
    PLEASE_FRIST_CREATE_CARD          = '0043'
    QUERY_BIND_CARD_ERROR            = '0044'
    QUERY_COMPANY_ERROR              = '0045'
    CHECK_USER_AND_CARD_ERROR    = '0046'
    DELETE_BIND_CARD_ERROR           = '0047'
    REGISTER_COMPANY_ERROR          = '0048'
    ASSOCIATE_COMPANY_ERROR        = '0049'
    QYERY_ACCOUNT_ERROR                = '0050'
    SITE_AND_COMPANY_ERROR             = '0051'
    QUERY_OIL_INFORMATION_ERROR   = '0052'
    TRANS_TYPE_ERROR                          = '0053'     
    COMFIRM_ORDER_ERROR                  = '0054'        
    OIL_COMP_HAS_ACOSIATE                = '0055'
    QUERY_COMP_INFO_ERROR               = '0056'
    ORDER_HAS_COMPLETE                     = '0057'
    MESSAGESERVERPUSHERROR             = '0058'
    QUERY_TARGETAUDIENCE_ERROR      = '0059'
    CREATE_TARGET_AUDIENCE_ERROR    = '0060'
    CAL_TARGET_AUDIENCE_USERLIST_ERROR = '0061'
    HAS_CREATE_SAME_TARGET_AUDIENCE = '0062'
    ORDER_HAS_NOT_PURCHASE                    = '0063'
    ENCRYPTION_DATA_ERROR                       = '0064'
    DECRYPTION_DATA_ERROR                       = '0065'
    ACTIVITY_VCARD_ERROR                            = '0066'
    HAS_ACTIVITY_VCARD_ERROR                    = '0067'
    MD5_ERROR                                              ='0068'
    QUERY_WORKER_ERROR                             = '0069'
    UPDATE_ORDER_ERROR                              = '0070'
    ORDER_TYPR_ERROR                                   = '0071'
    WAITCHECK                                                 = '0072'
    QUERY_STOREITEM_ERROR                          = '0073'
    QUERY_SERVICE_INFORMATION_ERROR       = '0074'
    QUERY_PROMOTION_ERROR                        = '0075'
    QUERY_USER_COMP_ERROR                          = '0076'
    QUERY_USER_ERROR                                    = '0077'
    ALERT_USER_ROLE_ERROR                              ='0078'
    ALERT_APP_USER_SETTING_ERROR                ='0079'
    DELETE_BIND_CARD_ERROR                           ='0080'
    OIL_CARD_HAS_BIND                                     = '0081'
    QUERY_OIL_LOSS_STATION_ERROR               ='0082'
    QUERY_PEAK_PERIOD_STATION_ERROR        ='0083'
    NO_OIL_LOSS_USER                                        ='0084'
    RESERVATION_CAN_NOT_PURCHASE              = '0085'
    HAS_NO_AUTHORITY_FOR_ORDER                 = '0086'
    HAS_NOT_REFUND_ORDER                            = '0087'
    REFUND_ORDER_ERROR                                = '0088'
    HAS_SUBMIT_ORDER_REFUND                      = '0089'
    APPLICATION_ORDER_REFUND_ERROR         ='0090'
    USER_ORDER_INFO_ERROR                           ='0091'
    HAS_NOT_PURCHASE                                    ='0092'
    WEIXIN_PURCHASE_ERROR                           ='0093'
    ADD_SITE_ERROR                                          ='0094'
    SITE_HAS_EXIST                                            ='0095'
    HAS_NO_ACCESS                                            ='0096'
    DELETE_TARGETAUDIENCE_ERROR               = '0097'
    ALTER_LODIN_PASSWORD_ERROR              = '0098'
    PRE_PASSWORD_ERROR                             = '0099'
    FEEDBACK_CONTENT_LENGTH_ERROR                  = '0100'
    FEEDBACK_CONTENT_HAS_SENTENSIVE_ERROR            = '0101'
    USERNAME_PASSWORD_ERROR                   = '0102'






    
    def getReason(self, code,error=None):
        if error==None:
            return status_collection[code]
        else:
            return 'Info:%s,Error:%s'%(
                status_collection[code],
                error
            )
