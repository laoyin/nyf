#coding=utf-8
from gcustomer.apps.jiachebao.models import *
from gcustomer.models import *
from gcustomer.utils import *
from gflux.apps.station.models import StationFuelType
from gcustomer.status  import *
import pdb,json
NEAR_DISTANCE = 10 #km

ajax_logger=logging.getLogger('ajax')

#获取附近油站sha1列表
def get_near_by_station_sha1s_data(request,**params):
    data = {}
    data['sha1s'] = []
    data['has_next'] = 'true'
    start = params['start']
    end = params['end']
    try :
      s=request.get_session()
      objs = s.query(StationProfile).all()
      if len(objs) <= end+1 :
          data['has_next'] = "false"
      for obj in objs :
         if distance(params['longitude'],params['latitude'],obj.geo_x,obj.geo_y) <= NEAR_DISTANCE :
            data['sha1s'].append(obj.site_sha1)
      #sort by sha1
      data['sha1s'].sort()
      data['sha1s'] = data['sha1s'][start:end+1]
    except Exception,e:
      print e
      data = {}
      data['sha1s'] = []
      return data
    return data

#获取附近油站详情
def get_near_by_station_data(request,**params):
    data = {}
    data['detail_list'] = []
    sha1s = params['sha1s']
    cardnum = params['cardnum']
    try:
        session = request.get_session()
        for sha1 in sha1s :
            try :
                # 获取站点的详情
                siteObj = session.query(StationProfile).filter_by(site_sha1=sha1).one()
                fuel_promotion = get_fuel_promotion_info(request,siteObj,cardnum)
                data['detail_list'].append(dict(
                    site_name = siteObj.site,
                    site_sha1 = siteObj.site_sha1,
                    site_img = "",
                    assist_type = siteObj.assist_type,
                    comment_score = siteObj.comment_score,
                    all_fuel_type = get_fuel_type(request,siteObj.site_code),
                    fuel_type = [],
                    is_busy =  cal_is_busy(siteObj.peak_range),
                    busy_info = '繁忙时段:'+cal_busy_time(siteObj.peak_range),
                    longitude = siteObj.geo_x,
                    latitude = siteObj.geo_y,
                    address = siteObj.address,
                    count = siteObj.comment_count,
                    phone = siteObj.site_tel,
                    promotion = fuel_promotion
            ))
            except Exception,e:
                print e
                data = {}
                return data
    except Exception, e:
        print e
        data = {}
        return data
    return data

#获取商品sha1列表
def get_goods_list_sha1s_data(request,**params):
    data = {}
    data['has_next'] = 'true'
    data['sha1s'] = []
    data['promotion_ids'] = []
    start = params['start']
    end = params['end']
    cardnum = params['cardnum']
    try :
        s=request.get_session()
        #创建完活动给某个用户推的优惠商品包括三部分: 1.给所有用户推的  2:给该用户推的 3:给某个用户群推的该用户在该群中

        if cardnum != "":
            cardnum = int(cardnum)
            #给所有用户推的 sha1s
            objs=s.query(UserTargetedPromotion).filter_by(user_type=1,user_id=0).all()
            good_sha1 = ''
            for obj in objs :
                session = request.get_session()
                if obj.obj_type == 0 :
                    pass
                elif obj.obj_type == 1:
                    try:
                        good_sha1 = session.query(StoreItem).filter_by(id = obj.obj_id).one().sha1
                    except:
                        pass
                elif obj.obj_type == 2:
                    pass
                if  good_sha1:
                    data['sha1s'].append(good_sha1)
                    data['promotion_ids'].append(obj.promotion_id)
            #给该用户推的 sha1s
            objs=s.query(UserTargetedPromotion).filter_by(user_type=1,user_id=int(cardnum)).all()
            good_sha1 = ''
            for obj in objs :
                session = request.get_session()
                if obj.obj_type == 0 :
                    pass
                elif obj.obj_type == 1:
                    try:
                        good_sha1 = session.query(StoreItem).filter_by(id = obj.obj_id).one().sha1
                    except:
                        pass
                elif obj.obj_type == 2:
                    pass
                if  good_sha1:
                    data['sha1s'].append(good_sha1)
                    data['promotion_ids'].append(obj.promotion_id)

            #给某个用户群推的该用户在该群中
            objs =  s.query(UserTargetedPromotion).filter_by(user_type=0).all()
            for obj in objs :
                try :
                    user_list = json.loads(s.query(CustomerGroup).filter_by(id = obj.user_id).one().user_list)
                except Exception,e:
                    pass
                if str(cardnum) in user_list:
                    session = request.get_session()
                    if obj.obj_type == 0 :
                        pass
                    elif obj.obj_type == 1:
                        try:
                            good_sha1 = session.query(StoreItem).filter_by(id = obj.obj_id).one().sha1
                        except:
                            pass
                    elif obj.obj_type == 2:
                        pass
                    if  good_sha1:
                        data['sha1s'].append(good_sha1)
                        data['promotion_ids'].append(obj.promotion_id)

        #data['sha1s'] 为空时
        if len(data['sha1s']) == 0:
            objs = s.query(StoreItem).all()
            for obj in objs :
                if  not obj.discount == 0:
                    data['sha1s'].append(obj.sha1)
                    data['promotion_ids'].append(-1)

        #sort by sha1
        temp = {}
        i = 0
        for sha1 in data['sha1s'] :
            temp[sha1] = data["promotion_ids"][i]
            i = i +1
        temp.keys().sort()
        data["sha1s"] = temp.keys()
        data['promotion_ids'] = []
        for sha1 in data['sha1s'] :
            data['promotion_ids'].append(temp[sha1])
        if len(data['sha1s']) <= end+1 :
            data['has_next'] = "false"
        data['sha1s'] = data['sha1s'][start:end+1]
        data['promotion_ids'] = data['promotion_ids'][start:end+1]
    except Exception,e:
        print e
        data = {}
        data['sha1s'] = []
        return data
    return data

#获取商品列表详情
def get_goods_list_data(request,**params):
  data = {}
  data['goods_list'] = []
  sha1s = params['sha1s']
  try :
    for sha1 in  sha1s :
      s=request.get_session()
      try :
          obj=s.query(StoreItem).filter_by(sha1=sha1).one()
      except Exception,e:
          continue
      # 获取商品的购买次数
      history_order = WheelTransaction.objects.filter(item_sha1=sha1).count()
      data['goods_list'].append(dict(
          obj_id = obj.id,
          good_pos_id = obj.pos_id,
          goods_name = obj.name,
          goods_sha1 = obj.sha1,
          discount = obj.discount,
          discount_info = obj.discount_info,
          discount_end_time = str(obj.discount_end_time).split(' ')[0],
          price = obj.price,
          history = history_order,
          pick = '',
          img_sha1 = obj.img_sha1 or "",
          img_info = obj.image or "",
          available_source = obj.user_source,
          seller_sha1 = obj.seller_sha1 or "232323asdcasdcasd",
          src='/gcustomer/ajax/render_image/'
        ))
  except Exception , e:
    print e
    data = {}
    return data
  return data

#获取商家数据
def get_seller_data(request,**params):
  data = {}
  data['seller_list'] = []
  sha1s = params['sha1s']
  try:
    for sha1 in sha1s :
      s=request.get_session()
      obj=s.query(Seller).filter_by(sha1=sha1).one()
      data['seller_list'].append(dict(
          name = obj.name,
          sha1 = obj.sha1,
          address = obj.address,
          geo_x = obj.geo_x,
          geo_y = obj.geo_y,
          phone = obj.phone,
          img_sha1 = obj.img_sha1 or  '' ,
          src='/gcustomer/ajax/render_image/'
        ))
  except Exception,e:
    print e
    data = {}
    return data
  return data

#获取车后服务sha1列表
def get_service_list_sha1s_data(request,**params):
  data = {}
  data['has_next'] = 'true'
  data['sha1s'] = []
  start = params['start']
  end = params['end']
  try :
    s=request.get_session()
    # 这里首先查询 UserTargetedPromotion
    #objs=s.query(UserTargetedPromotion).filter_by(user_id='')
    objs=s.query(ServiceInformation).all()
    if len(objs) <= end+1 :
      data['has_next'] = "false"
    for obj in objs :
      if obj.sha1 :
        data['sha1s'].append(obj.sha1)
    #sort by sha1
    data['sha1s'].sort()
    data['sha1s'] = data['sha1s'][start:end+1]
  except Exception,e :
    print e
    data = {}
    data['sha1s'] = []
    return data
  return  data

#获取车后服务列表详情
def get_service_list_data(request,**params):
  data = {}
  data["service_list"] = []
  sha1s = params['sha1s']
  try :
    for sha1 in sha1s:
      s=request.get_session()
      obj=s.query(ServiceInformation).filter_by(sha1=sha1).one()
      sale_item_usge = StoreItemUsage.objects.filter(item_sha1=sha1).first()
      try:
          seller_obj = s.query(Seller).filter_by(sha1=obj.seller_sha1).one()
          seller_sha1 = seller_obj.sha1 or ''
          longitude =  seller_obj.geo_x
          latitude =  seller_obj.geo_y
          score = seller_obj.score or 0
      except :
          seller_obj = None
          seller_sha1 = ''
          longitude = 0
          latitude =  0
          score = 0
      data['service_list'].append(dict(
          #item_type = sale_item_usge.item_type,
          item_type = 1,
          sha1 = sha1,
          title = obj.title,
          price = obj.price or 0,
          seller_sha1 =seller_sha1,
          longitude =longitude ,
          latitude = latitude,
          item_img = '',
          discount_info =obj.discount_score or "",
          score = score,
          comment_count = obj.nb_comments or 0,
          img_sha1 = obj.img_sha1 or "",
          src='/gcustomer/ajax/render_image/'
        ))
  except Exception,e:
    print e
    data = {}
    return data
  return  data

#商品评论
def comment_item_data(request,**params):
  user_sha1 = params["user_sha1"]
  item_sha1 = params["item_sha1"]
  score = params["score"]
  try :
    #get user name
    #query user sha1 from CustomerAccount
    #return 1: no permossion 2: have comment 0:ok
    transaction = WheelTransaction.objects.filter(user_sha1=user_sha1,item_sha1 = item_sha1)
    if transaction:
      item = StoreItemUsage.objects.filter(item_sha1 = item_sha1).first()
      obj = WheelPurchaseComment(
          item_sha1 = item_sha1,
          item_type = item.item_type,
          user_score = score,
          comment_content ="",
        )
      try:
        obj.save()
      except Exception,e:
        print e
        return 2
      if item.item_type == 0:
          saleitem = WheelSaleItem.objects.filter(sha1=item_sha1).first()
          if saleitem :
            saleitem.score = saleitem.score + score
            saleitem.save()
      elif item.item_type == 1:
          saleitem = WheelSaleService.objects.filter(sha1=item_sha1).first()
          if saleitem :
            saleitem.score = saleitem.score + score
            saleitem.save()
  except Exception,e:
    print e
    return 1
  return 0

#获取可积分兑换商品sha1列表
def get_score_list_sha1_data(request,**params):
  data = {}
  data['has_next'] = 'true'
  data['sha1s'] = []
  user_sha1 = params['user_sha1']
  start = params['start']
  end = params['end']
  try :
    session = request.get_session()
    obj = CustomerAccount.objects.filter(sha1=user_sha1).first()
    if not obj :
      data = {}
      return data
    goods = session.query(StoreItem).all()
    if len(goods) <= end+1 :
      data['has_next'] = 'false'
    for good in goods :
      if good.exchange_score != -1:
            data['sha1s'].append(good.sha1)
    #sort by sha1
    data['sha1s'].sort()
    data['sha1s'] = data['sha1s'][start:end+1]
  except Exception,e :
    print e
    data = {}
    data['sha1s']=[]
    return data
  return  data

#获取积分兑换商品列表详情
def get_score_list_data(request,**params):
  data = {}

  import operator

  #积分列表
  data["score_list"] = []
  data['has_next'] = 'true'

  #参数
  vcard_id = params['vcard_id']
  start = params['start']
  end = params['end']
  try:
    session = request.get_session()

    #未登录用户，可以查看10条积分商品
    if vcard_id == '':
        objs = session.query(StoreItem).filter_by(exchange_score>0).limit(10).all()
        data['has_next'] = 'false'
        for obj in objs:
            data['score_list'].append(dict(
                goods_name = obj.name or '',
                sha1 = obj.sha1 or '',
                seller_sha1 = obj.seller_sha1 or '',
                score = obj.exchange_score or 0,
                img_sha1 = obj.img_sha1 or "",
                src = '/gcustomer/ajax/render_image/'
              ))
    else:
        #该用户关联的石油公司
        comps = session.query(CustomerCompInfo).filter_by(vcard_id=vcard_id).all()
        for comp in comps:
            #查询关联公司下的，可兑换积分的商品
            objs = session.query(StoreItem).filter(StoreItem.comp_id==comp.comp_id,StoreItem.exchange_score>0).all()
            for obj in objs:
                data['score_list'].append(dict(
                    goods_name = obj.name or '',
                    sha1 = obj.sha1 or '',
                    seller_sha1 = obj.seller_sha1 or '',
                    score = obj.exchange_score or 0,
                    img_sha1 = obj.img_sha1 or "",
                    src = '/gcustomer/ajax/render_image/'
                  ))

        #是否还有更多
        need_count = int(end) - int(start)
        if need_count >= len(data["score_list"]):
            data['has_next'] = 'false'

        #排序返回
        data["score_list"] = sorted(data["score_list"], key=operator.itemgetter('sha1'))[int(start):int(end)]

  except Exception,e:
    print e
    data = {}
    data["score_list"] = []
    return data

  return  data

#获取商家信息
def get_merchants_info_data(request,result,**params):
  data = {}
  sha1 = params['sha1']
  try:
    session = request.get_session()
    obj = session.query(Seller).filter_by(sha1=sha1).one()
    data = dict(
            name = obj.name,
            address = obj.address,
            tel = obj.phone,
            longitude = obj.geo_x,
            latitude = obj.geo_y,
            logo = "",
            score = obj.score,
            introduction = obj.introduction
      )
  except Exception, e:
    print e
    data = {}
    return data
  finally:
    return data

#消息盒子
def myMessagesBox_data(result,**params):
    data = {}
    data['has_next'] = 'true'
    #主贴列表
    data['message_list'] = []
    sha1 = params['sha1']
    messageType = params['messageType']
    start = params['start']
    end = params['end']
    try :
        objs = WheelMessageMembership.objects.filter(user_sha1=sha1).all()
        for obj in objs :
            try:
                post = WheelMessage.objects.filter(sha1=obj.message_sha1).first()
                if post.parent_sha1 == '' and post.request_type == messageType :
                    try:
                        author = CustomerAccount.objects.filter(sha1 = sha1).first()
                    except Exception,e:
                        print e
                        data = {}
                        data['message_list'] = []
                    data['message_list'].append(dict(
                    sha1 = post.sha1,
                    career = author.career,
                    author_sha1 = sha1,
                    message_type = post.message_type,
                    time = post.time,
                    parent_sha1 = post.parent_sha1,
                    root_sha1 = post.root_sha1,
                    address = '',
                    body = post.body,
                    attachment_info = json.loads(post.attachment_info)
                    ))
            except Exception,e :
              print e
              data = {}
              data['message_list'] = []
    except Exception,e:
        print e
        data = {}
        data['message_list'] = []
    return data

# 根据商品的sha1获取商品信息和商家支付信息
def get_goods_info(request,goods_sha1):
    goods_info = {}
    try:
        session = request.get_session()
        goods_obj = session.query(StoreItem).filter_by(sha1=goods_sha1).one()

        #该商品对应的油站
        comp_id = goods_obj.comp_id

        #该商品对应的油站
        station = session.query(Station).filter_by(comp_id=comp_id).one()
        #goods_obj = StoreItem.objects.get(sha1=goods_sha1)
        goods_info['goods_sha1']=goods_obj.sha1
        goods_info['goods_name']=goods_obj.name
        goods_info['price']=goods_obj.price
        goods_info['score']=goods_obj.score
        goods_info['seller_sha1']=goods_obj.seller_sha1 or ""
        goods_info['pick']=goods_obj.count
        goods_info['history']=1
        goods_info['src']="/gcustomer/ajax/render_image/"
        goods_info['img_sha1']=goods_obj.img_sha1 or ''
        goods_info['available_source']=station.name
        goods_info['information']=goods_obj.information
        goods_info['pos_id']=goods_obj.pos_id
        goods_info['exchange_score']=goods_obj.exchange_score
        goods_info['discount']=goods_obj.discount
        goods_info['discount_info']=goods_obj.discount_info
        goods_info['discount_end_time']=goods_obj.discount_end_time
    except:
        goods_info['goods_sha1']=''
        goods_info['goods_name']=''
        goods_info['price']=0
        goods_info['score']=0
        goods_info['seller_sha1']=''
        goods_info['pick']=0
        goods_info['history']=0
        goods_info['src']=''
        goods_info['img_sha1']=''
        goods_info['available_source']=''
        goods_info['information']=''
        goods_info['pos_id']=''
        goods_info['exchange_score']=''
        goods_info['discount']=0
        goods_info['discount_info']=''
        goods_info['discount_end_time']=''

    return goods_info

# 根据商品的sha1获取商品信息和商家支付信息
def get_seller_info(request,seller_sha1):
    seller_info = {}
    try:
        session = request.get_session()
        seller_object = session.query(Seller).filter_by(sha1=seller_sha1).one()
        #seller_info = Seller.objects.get(sha1=seller_sha1)
        seller_info['name'] = seller_object.name
        seller_info['sha1'] = seller_object.sha1
        seller_info['address'] = seller_object.address
        seller_info['geo_x'] = seller_object.geo_x
        seller_info['geo_y'] = seller_object.geo_y
        seller_info['phone'] = seller_object.phone
        goods_info['src']="/gcustomer/ajax/render_image/"
        seller_info['img_sha1'] = seller_object.img_sha1 or ''
        seller_info['score'] = seller_object.score
        seller_info['introduction'] = seller_object.introduction
    except:
        seller_info['name'] = "通用商品"
        seller_info['sha1'] = ""
        seller_info['address'] = ""
        seller_info['geo_x'] = 0
        seller_info['geo_y'] = 0
        seller_info['phone'] = 0
        seller_info['src']=""
        seller_info['img_sha1'] = ""
        seller_info['score'] = 0
        seller_info['introduction'] = ""
    finally :
        return seller_info

#获取车后服务
def get_services_info(request,good_sha1):
    service_info = {}
    try :
        session = request.get_session()
        service_object = session.query(ServiceInformation).filter_by(sha1=good_sha1).one()
        service_info['goods_name'] = service_object.title
        service_info['goods_sha1'] = service_object.sha1
        service_info['seller_sha1'] = service_object.seller_sha1 or ""
        service_info['price'] = service_object.price
        service_info['discount'] = 0
        service_info['discount_info'] = ''
        service_info['discount_end_time'] = ''
        service_info['available_source'] = ''
        service_info['history'] = 0
        service_info['pick'] = 0
        service_info['src'] = ''
        service_info['img_sha1'] = ''
    except Exception,e :
        service_info['goods_name'] = ''
        service_info['goods_sha1'] = ''
        service_info['seller_sha1'] = ''
        service_info['price'] = 0
        service_info['discount'] = 0
        service_info['discount_info'] = ''
        service_info['discount_end_time'] = ''
        service_info['available_source'] = ''
        service_info['history'] = 0
        service_info['pick'] = 0
        service_info['src'] = ''
        service_info['img_sha1'] = ''
    finally :
      return service_info

#获取油品
def get_fuel_info(request,barcode,order):
    fuel_info = {}
    try :
      session = request.get_session()
      fuel_name = session.query(StationFuelType).filter_by(barcode = barcode)[0].description
      fuel_info['goods_name'] = fuel_name
      fuel_info['goods_sha1'] = ''
      fuel_info['seller_sha1'] = order.station_sha1 or ''
      fuel_info['price'] = order.item_total or 0
      fuel_info['discount'] = 0
      fuel_info['discount_info'] = ''
      fuel_info['discount_end_time'] = ''
      fuel_info['available_source'] = ''
      fuel_info['history'] = 0
      fuel_info['pick'] = 0
      fuel_info['src'] = ''
      fuel_info['img_sha1'] = ''
    except Exception,e:
      fuel_info['goods_name'] = ''
      fuel_info['goods_sha1'] = ''
      fuel_info['seller_sha1'] = ''
      fuel_info['price'] = 0
      fuel_info['discount'] = 0
      fuel_info['discount_info'] = ''
      fuel_info['discount_end_time'] = ''
      fuel_info['available_source'] = ''
      fuel_info['history'] = 0
      fuel_info['pick'] = 0
      fuel_info['src'] = ''
      fuel_info['img_sha1'] = ''
    finally :
      return fuel_info

#获取站点精准推送给用户的油品优惠活动
def get_fuel_promotion_info(request,siteObj,cardnum):
    try :
            session = request.get_session()
            fuel_id_list = []
            #获取精准推送给该用户的油品
            if cardnum != "":
                    cardnum = int(cardnum)
                    #获取自动给该用户推送的优惠商品 sha1s
                    objs=session.query(UserTargetedPromotion).filter_by(user_type=1,user_id=0).all()
                    for obj in objs :
                        if obj.obj_type == 0 :
                            fuel_id_list.append(obj)
                    #获取自动给该用户推送的优惠商品 sha1s
                    objs=session.query(UserTargetedPromotion).filter_by(user_type=1,user_id=int(cardnum)).all()
                    for obj in objs :
                        if obj.obj_type == 0 :
                            fuel_id_list.append(obj)
                    #手动创建优惠活动时给该用户推送的优惠商品
                    objs =  session.query(UserTargetedPromotion).filter_by(user_type=0).all()
                    for obj in objs :
                        user_list = json.loads(session.query(CustomerGroup).filter_by(id = obj.user_id).one().user_list)
                        if str(cardnum) in user_list:
                            if obj.obj_type == 0 :
                                fuel_id_list.append(obj)
            #取得该油站油品优惠信息
            fuel_promotion_list = []
            for fuel_id in fuel_id_list :
                promotion_info = session.query(PromotionInfo).filter_by(promotion_id=fuel_id.promotion_id,obj_id=fuel_id.obj_id).all()
                for relation in promotion_info :
                    site_code = relation.site_code
                    if site_code == siteObj.site_code :
                        fuel_promotion_list.append(relation)
            #按照promotion_id分组
            site_fuel_promotion_list = {}
            for fuel_promotion in fuel_promotion_list :
                if site_fuel_promotion_list.has_key(fuel_promotion.promotion_id) :
                    site_fuel_promotion_list[fuel_promotion.promotion_id].append(fuel_promotion)
                else :
                    site_fuel_promotion_list[fuel_promotion.promotion_id] = []
                    site_fuel_promotion_list[fuel_promotion.promotion_id].append(fuel_promotion)
            #返回活动信息
            result_fuel_promotion_list = []
            for promotion_id in site_fuel_promotion_list.keys():
                    promotion_obj = session.query(Promotion).filter_by(id = promotion_id).one()
                    discount_information = ""
                    for promotion in site_fuel_promotion_list[promotion_id] :
                        if str(promotion.discount*10).split(".")[1] == "0" :
                            discount = str(promotion.discount*10).split(".")[0]
                        else :
                            discount = str(promotion.discount*10)
                        discount_information = discount_information +  get_fuel_info(request,promotion.obj_id)['goods_name'] + " : " +  discount  + u"折" +"\n"
                    result_fuel_promotion_list.append(dict(
                          name = promotion_obj.name,
                          start_time = str(promotion_obj.start_time).split(".")[0],
                          end_time =  str(promotion_obj.end_time).split(".")[0],
                          discount_information =  discount_information ,
                          activity_img = ""
                    ))
    except Exception,e:
            result_fuel_promotion_list = []
    return result_fuel_promotion_list
