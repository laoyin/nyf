# #生成所有区域的报表
            # stations = session.query(UserStation).filter_by(user_id=user_id).all()
            # for station in stations:
            #     location = session.query(Station).filter_by(name=station.station).one()
            #     if location.province==0 or location.province in locations:
            #         continue
            #     locations.append(location.province)
            # for location in locations :
            #     try :
            #         location_string = session.query(DimChinaProvinceCityDistrict).filter_by(id=location).one().name
            #     except Exception ,e:
            #         print '查询行政区划失败'
            #         gearman_logger.error("查询行政区划失败")
            #         return 
            #     try :
            #         file_name = absolute_report_file_path +current_time +'_'+location_string+u"区域的报表.xls"
            #         report_creator.make_report_xlsx(user_id=user_id,location=location,tag=0,unit=1,file_name=file_name)
            #         print "生成用户"+user+location_string+"区域的报表.xls"
            #     except Exception,e:
            #         print e
            #         continue

            # #生成所有标签的报表
            # tags = session.query(Tag).filter_by(user_id = user_id).all()
            # tag_list = []
            # for tag in tags :
            #     tag_list.append(tag.id)
            # for tag_id in tag_list :
            #     try :
            #         tag_string = session.query(Tag).filter_by(id=tag_id).one().tag
            #     except Exception,e:
            #         print "查询标签名失败"
            #         continue
            #     try :
            #         file_name = absolute_report_file_path + current_time +'_'+u"标签"+tag_string+u"下所有站的报表.xls"
            #         report_creator.make_report_xlsx(user_id=user_id,location=0,tag=tag_id,unit=1,file_name=file_name)
            #         print "生成用户"+user+"标签"+tag_string+"下所有站的报表.xls"
            #     except Exception,e:
            #         print e
            #         continue
            #         return 
