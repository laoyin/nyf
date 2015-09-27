#生成图表样式
def create_report_style(workbook):
    #title format
    format0 = workbook.add_format()
    format0.set_align('center')
    format0.set_align('vcenter')
    format0.set_bold(True)
    format0.set_font_size(16)

    #sub title format
    format1 = workbook.add_format()
    format1.set_align('center')
    format1.set_align('vcenter')
    format1.set_bold(True)
    format1.set_font_size(11)
    format1.set_border(2)
    format1.set_border_color('#000000')

    #msg format
    format2 = workbook.add_format()
    format2.set_align('center')
    format2.set_align('vcenter')
    format2.set_font_size(10)
    format2.set_bold(True)
    format2.set_bg_color('#434552')
    format2.set_font_color('#ffffff')
    format2.set_pattern()
    format2.set_border(1)
    format2.set_border_color('#000000')

    #normal style
    format3 = workbook.add_format()
    format3.set_font_size(8)
    format3.set_border(1)
    format3.set_border_color('#000000')
    format3.set_align('center')
    format3.set_align('vcenter')
    format_list = [format0,format1,format2,format3]
    return format_list

#创建图表的内容格式
def create_report_context(worksheet,format_list) :
    format0 = format_list[0]
    format1 = format_list[1]
    format2 = format_list[2]
    format3 = format_list[3]


    #write context
    worksheet.set_row(0,20)
    for i in range(1,24):
        worksheet.set_row(i,14)
    for i in range(25,42):
        worksheet.set_row(i,12)

    worksheet.set_row(8,8)
    worksheet.set_row(15,8)
    worksheet.set_row(24,8)

    worksheet.set_column(0,0,3)
    worksheet.set_column(1,1,12)
    worksheet.set_column(2,14,10)
    worksheet.set_column(15,15,1)


    worksheet.merge_range(2,0,7,0,u'油\n品\n业\n务',format1)
    worksheet.merge_range(9,0,14,0,u'非\n油\n业\n务',format1)
    worksheet.merge_range(16,0,23,0,u'卡\n业\n务',format1)

    worksheet.write(2,1,u'去年实际',format3)
    worksheet.write(3,1,u'今年预估',format3)
    worksheet.write(4,1,u'今年实际',format3)
    worksheet.write(5,1,u'增长率',format3)
    worksheet.write(6,1,u'差异/吨',format3)
    worksheet.write(7,1,u'站日均',format3)

    worksheet.write(9,1,u'去年实际',format3)
    worksheet.write(10,1,u'今年预估',format3)
    worksheet.write(11,1,u'今年实际',format3)
    worksheet.write(12,1,u'增长率',format3)
    worksheet.write(13,1,u'差异/吨',format3)
    worksheet.write(14,1,u'站日均',format3)

    worksheet.write(16,1,u'去年消费笔数',format3)
    worksheet.write(17,1,u'今年消费笔数',format3)
    worksheet.write(18,1,u'去年消费金额',format3)
    worksheet.write(19,1,u'今年消费金额',format3)
    worksheet.write(20,1,u'去年单次消费',format3)
    worksheet.write(21,1,u'今年单次消费',format3)
    worksheet.write(22,1,u'去年沉淀资金',format3)
    worksheet.write(23,1,u'今年沉淀资金',format3)

    worksheet.write(1, 0, '', format2)
    worksheet.write(1, 1, '', format2)
    for i in range(1,13):
        worksheet.write(1, i+1, str(i)+u'月', format2)
    worksheet.write(1, 14, u'总计', format2)

    worksheet.merge_range(25,10,25,14,u'油品销售分析',format2)
    worksheet.write(26,10,'',format2)
    worksheet.write(26,11,u'当日销量',format2)
    worksheet.write(26,12,u'日均销量',format2)
    worksheet.write(26,13,u'当月累计',format2)
    worksheet.write(26,14,u'波动率%',format2)
    worksheet.write(27,10,u'97#',format3)
    worksheet.write(28,10,u'93#',format3)
    worksheet.write(29,10,u'柴油',format3)
    worksheet.write(30,10,u'小计',format3)

    worksheet.merge_range(32,10,32,14,u'非油销售分析',format2)
    worksheet.write(33,10,'',format2)
    worksheet.write(33,11,u'当日销量',format2)
    worksheet.write(33,12,u'日均销量',format2)
    worksheet.write(33,13,u'当月累计',format2)
    worksheet.write(33,14,u'波动率%',format2)
    worksheet.write(34,10,u'饮料',format3)
    worksheet.write(35,10,u'酒精',format3)
    worksheet.write(36,10,u'香烟',format3)
    worksheet.write(37,10,u'食品',format3)
    worksheet.write(38,10,u'糖果',format3)
    worksheet.write(39,10,u'车用品',format3)
    worksheet.write(40,10,u'日用品',format3)
    worksheet.write(41,10,u'小计',format3)

    worksheet.merge_range(1,16,1,18,u'基本信息',format2)
    worksheet.write(2,16,u'油站名称',format3)
    worksheet.write(3,16,u'油站地址',format3)
    worksheet.write(4,16,u'开业日期',format3)
    worksheet.write(5,16,u'油站经理',format3)
    worksheet.write(6,16,u'电话',format3)
    worksheet.merge_range(7,16,7,18,'',format3)

    worksheet.merge_range(9,16,9,18,u'数据选择',format2)
    worksheet.write(10,16,u'油站选择',format3)
    worksheet.merge_range(11,16,11,18,'',format3)
    worksheet.write(12,16,u'截止日期',format3)
    worksheet.merge_range(13,16,13,18,'',format3)
    worksheet.write(14,16,u'计量单位',format3)

    worksheet.merge_range(29,16,29,18,u'当月销售预测',format2)
    worksheet.merge_range(30,16,30,18,u'预测油品销量',format3)
    worksheet.write(31,16,u'汽油',format3)
    worksheet.write(31,18,u'吨/月',format3)
    worksheet.write(32,16,u'柴油',format3)
    worksheet.write(32,18,u'吨/月',format3)
    worksheet.write(33,16,u'小计',format3)
    worksheet.write(33,18,u'吨/月',format3)
    worksheet.merge_range(34,16,34,18,u'预测油品销售额',format3)
    worksheet.write(35,16,u'汽油',format3)
    worksheet.write(35,18,u'元/月',format3)
    worksheet.write(36,16,u'柴油',format3)
    worksheet.write(36,18,u'元/月',format3)
    worksheet.write(37,16,u'小计',format3)
    worksheet.write(37,18,u'元/月',format3)
    worksheet.merge_range(38,16,38,18,u'预测非油销售额',format3)
    worksheet.write(39,16,u'非油',format3)
    worksheet.write(39,18,u'元/月',format3)
    worksheet.merge_range(40,16,40,18,u'预测总体销售额',format3)
    worksheet.write(41,16,u'总体',format3)
    worksheet.write(41,18,u'元/月',format3)

#写入数据
def create_report_data(worksheet,unit,location,tag,format_list,user_id):
    #fill in the data
    format0 = format_list[0]
    format1 = format_list[1]
    format2 = format_list[2]
    format3 = format_list[3]

    data = get_report_info(unit,location=location,tag=tag,user_id=1)
    station_num = len(data['stations'])

    month = [31,28,31,30,31,30,31,31,30,31,30,31]
    year = time.localtime()[0]
    if (year%400 == 0) or ( year%4 == 0 and year%100 != 0 ):
        month[1] = 29

    stations = ''
    for station in data['stations']:
        stations += station + ','
    stations = stations[:-1]

    worksheet.merge_range('A1:S1',stations+u'销售数据概览',format0)
    worksheet.merge_range('R11:S11',stations,format3)
    worksheet.merge_range('R13:S13', time.strftime('%Y-%m-%d',time.localtime(time.time())), format3)
    if data['unit'] == 0:
        unit = u'吨'
    elif data['unit'] == 1:
        unit = u'升'
    worksheet.merge_range('R15:S15',unit,format3)

    worksheet.merge_range('R3:S3','',format3)
    worksheet.merge_range('R4:S4','',format3)
    worksheet.merge_range('R5:S5','',format3)
    worksheet.merge_range('R6:S6','',format3)
    worksheet.merge_range('R7:S7','',format3)

    est_qiyou_t = month[time.localtime()[1]-1]*(data['sale_stat_month_t'][0]+data['sale_stat_month_t'][1])/time.localtime()[2]
    worksheet.write('R32',str(est_qiyou_t),format3)
    est_chaiyou_t = month[time.localtime()[1]-1]*(data['sale_stat_month_t'][2])/time.localtime()[2]
    worksheet.write('R33',str(est_chaiyou_t),format3)

    est_qiyou_y = month[time.localtime()[1]-1]*(data['sale_stat_month_y'][0])/time.localtime()[2]
    worksheet.write('R36',str(est_qiyou_y),format3)
    est_chaiyou_y = month[time.localtime()[1]-1]*(data['sale_stat_month_y'][1])/time.localtime()[2]
    worksheet.write('R37',str(est_chaiyou_y),format3)

    for i in range(0,len(data['last_year_fuel_fact'])):
        worksheet.write(chr(67+i)+str(3), data['last_year_fuel_fact'][i], format3)

    for i in range(0,len(data['last_year_nonfuel_fact'])):
        worksheet.write(chr(67+i)+str(10), data['last_year_nonfuel_fact'][i], format3)

    for i in range(0,len(data['fuel_fact'])):
        worksheet.write(chr(67+i)+str(5), data['fuel_fact'][i], format3)

    for i in range(0,len(data['nonfuel_fact'])):
        worksheet.write(chr(67+i)+str(12), data['nonfuel_fact'][i], format3)

    for i in range(0,len(data['estimate_fuel'])):
        worksheet.write(chr(67+i)+str(4), data['estimate_fuel'][i], format3)

    for i in range(0,len(data['estimate_nonfuel'])):
        worksheet.write(chr(67+i)+str(11), data['estimate_nonfuel'][i], format3)

    for i in range(0,len(data['last_year_card_purchase_num'])):
        worksheet.write(chr(67+i)+str(17), data['last_year_card_purchase_num'][i], format3)

    for i in range(0,len(data['card_purchase_num'])):
        worksheet.write(chr(67+i)+str(18), data['card_purchase_num'][i], format3)

    for i in range(0,len(data['last_year_card_purchase_Amount'])):
        worksheet.write(chr(67+i)+str(19), data['last_year_card_purchase_Amount'][i], format3)

    for i in range(0,len(data['card_purchase_Amount'])):
        worksheet.write(chr(67+i)+str(20), data['card_purchase_Amount'][i], format3)

    return data

#插入图表

#折线图
def create_report_dash_line(workbook,unit,location,tag,worksheet,data):
    worksheet2 = workbook.add_worksheet()
    chart_line = workbook.add_chart({'type': 'line'})
    headings_line = [u'月份', u'汽油', u'柴油', u'总量']
    bold_line = workbook.add_format({'bold': 1})
    data_line = [
        range(1, len(data['qiyou_line'])+1 ),
        data['qiyou_line'],
        data['chaiyou_line']
    ]
    worksheet2.write_row('A1', headings_line, bold_line)
    worksheet2.write_column('A2', data_line[0])
    worksheet2.write_column('B2', data_line[1])
    worksheet2.write_column('C2', data_line[2])
    for i in range(2, len(data['qiyou_line'])+2 ):
        worksheet2.write('D'+str(i),'=B'+str(i)+'+C'+str(i) )

    chart_line.add_series({
        'name':       ['Sheet2', 0, 1],
        'categories': ['Sheet2', 1, 0, len(data['qiyou_line'])+1, 0],
        'values':     ['Sheet2', 1, 1, len(data['qiyou_line'])+1, 1],
    })
    chart_line.add_series({
        'name':       ['Sheet2', 0, 2],
        'categories': ['Sheet2', 1, 0, len(data['qiyou_line'])+1, 0],
        'values':     ['Sheet2', 1, 2, len(data['qiyou_line'])+1, 2],
    })
    chart_line.add_series({
        'name':       ['Sheet2', 0, 3],
        'categories': ['Sheet2', 1, 0, len(data['qiyou_line'])+1, 0],
        'values':     ['Sheet2', 1, 3, len(data['qiyou_line'])+1, 3],
    })
    chart_line.set_title ({'name': u'销量折线图'})
    chart_line.set_x_axis({'name': u'月份'})
    chart_line.set_y_axis({'name': u'销量'})
    chart_line.set_style(10)
    chart_line.set_size({'width': 720, 'height': 320})

    worksheet.insert_chart('A25', chart_line)


#饼状图
def create_report_dash_pie(workbook,unit,location,tag,worksheet,data):

    worksheet3 = workbook.add_worksheet()
    bold_pie = workbook.add_format({'bold': 1})
    headings_pie = ['Category', 'Values']
    data_pie = [
        [u'汽油', u'柴油', u'非油'],
        data['sale_stat_month_y'],
    ]
    worksheet3.write_row('A1', headings_pie, bold_pie)
    worksheet3.write_column('A2', data_pie[0])
    worksheet3.write_column('B2', data_pie[1])
    chart_pie = workbook.add_chart({'type': 'pie'})
    chart_pie.add_series({
        'name':       u'sale pie chart',
        'categories': ['Sheet3', 1, 0, 3, 0],
        'values':     ['Sheet3', 1, 1, 3, 1],
    })
    chart_pie.set_title({'name': u'销售占比饼图'})
    chart_pie.set_style(10)
    chart_pie.set_size({'width': 220, 'height': 220})
    worksheet.insert_chart('Q17', chart_pie)

#写入excel函数
def create_report_func_define(worksheet,format_list,data):
    format0 = format_list[0]
    format1 = format_list[1]
    format2 = format_list[2]
    format3 = format_list[3]

    station_num = len(data['stations'])

    month = [31,28,31,30,31,30,31,31,30,31,30,31]
    year = time.localtime()[0]
    if (year%400 == 0) or ( year%4 == 0 and year%100 != 0 ):
        month[1] = 29

    #1-12月的累加统计
    for i in range(3,25):
        if i in range(3,6) or i in range(10,13) or i in range(17,21):
            worksheet.write('O'+str(i),'=SUM(C'+str(i)+':N'+str(i)+')',format3)

    #增长率统计
    for j in (6,13):
        for i in range(67,80):
            worksheet.write(chr(i)+str(j),'='+chr(i)+str(j-1)+'/'+chr(i)+str(j-3),format3)

    #差异统计
    for j in (7,14):
        for i in range(67,80):
            worksheet.write(chr(i)+str(j),'='+chr(i)+str(j-2)+'-'+chr(i)+str(j-4),format3)

    #站日均
    for j in (8,15):
        day = 0
        for i in month:
            day += i
        worksheet.write('O'+str(j),'=O'+str(j-3)+'/'+str(day)+'/'+str(station_num),format3)
        for i in range(67,79):
            worksheet.write(chr(i)+str(j), '='+chr(i)+str(j-3)+'/'+str(month[i-67])+'/'+str(station_num),format3)

    #统计单次消费
    for j in (21,22):
        for i in range(67,80):
            worksheet.write(chr(i)+str(j),'='+chr(i)+str(j-2)+'/'+chr(i)+str(j-4),format3)

    #销售分析小计
    for i in ('L','M','N'):
        worksheet.write(i+'31','=SUM('+i+'28:'+i+'30)',format3)
        worksheet.write(i+'42','=SUM('+i+'35:'+i+'41)',format3)

    #销售预测
    worksheet.write('R34','=R32+R33',format3)
    worksheet.write('R38','=R36+R37',format3)
    worksheet.write('R42','=R38+R40',format3)