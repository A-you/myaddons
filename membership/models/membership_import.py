# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/9/6 12:05
"""

from odoo import api, fields, models
import xlrd
import base64
import json
from odoo.exceptions import Warning
class WxappImportProduct(models.TransientModel):
    _name = 'membership.import'
    _description = u'会籍会员导入'

    xls = fields.Binary(u'表格文件')

    name = fields.Char(string=u"产品名")

    def create_person_partner(self,y):
        res_id=self.env['res.partner'].sudo().create({
		    "last_name": y['last_name'],
		    "company_type": "person",
		    "first_name": y["first_name"],
		    "en_last_name": y["en_last_name"],
		    "en_first_name": y["en_first_name"],
		    "email": y["email"],
		    "phone": y["phone"],
		    "other_phone": y['other_phone'],
	        'mobile': y['mobile'],
		    "internal_noted": y['internal_noted'],
		    "wechat": y['wechat'],
		    # tag_ids.append((4, self.env.ref('l10n_nl.account_tag_25').id))
		    "category_id": [(4, self.env.ref("membership.res_partner_category_data_igba").id)] if y['is_iba'] else None,
		    "member_take": True if y['is_iba'] else False,
	        # "membership_points_lines": [(0,0,{})]
	    })[0]

        return res_id


    # def resize_write_product(self):
    #     no_find_list = []
    #     for wiz in self.browse(self.ids):
    #         if not wiz.xls:
    #             continue
    #         excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.xls))
    #         sheets = excel.sheets()
    #         sheet1 = sheets[0]
    #         print(sheet1)
    #         for row in range(1, sheet1.nrows):
    #             partner_id = int(str(sheet1.cell(row,1).value).strip())
    #             member_num = str(sheet1.cell(row,3).value).strip()
    #             # print(partner_id,type(partner_id))
    #             # print(member_num,type(member_num))
    #             # browse:
    #             partner=self.env['res.partner'].sudo().search([('id','=',partner_id)])
    #             if partner:
    #                 print("有了",partner.name)
    #                 partner.write({
	#                     "membership_numbered": member_num
    #                 })
    def resize_write_product(self):
        no_find_list = []
        for wiz in self.browse(self.ids):
            if not wiz.xls:
                continue
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.xls))
            sheets = excel.sheets()
            sheet1 = sheets[1]
            sheet2 = sheets[2]
            company_list=[]
            #公司id_list
            com_id_list = []
            for row in range(1,sheet2.nrows):
	            data = {
		            "name": str(sheet2.cell(row,0).value).strip(),
		            "w_id": str(sheet2.cell(row,1).value).strip(),
		            "company_type": "company",
		            "phone": str(sheet2.cell(row,5).value).strip().replace(".",""),
		            # "membership_level": 2 if str(sheet2.cell(row,6).value).strip() == "ZR" else 1,
		            "membership_level": 1,
		            "membership_list": []
	            }
	            com_id_list.append(str(sheet2.cell(row,1).value).strip())
	            company_list.append(data)
	        #服务领域list
            service_type_list = []
            #没有公司的人
            no_com_members = []
            n = 0
            u = 0
            person_list = []
            for member_row in range(4,sheet1.nrows):
                str0 = str(sheet1.cell(member_row,24).value).strip()
                if str0:
                    str_list = str0.split(";")
                    for res_str in str_list:
                        service_type_list.append(res_str)
                _dict={
	                "is_iba": str(sheet1.cell(member_row,2).value).strip(),
	                "title": str(sheet1.cell(member_row,4).value).strip(),
	                "last_name": str(sheet1.cell(member_row,5).value).strip(),
	                "first_name": str(sheet1.cell(member_row,6).value).strip(),
	                "en_last_name": str(sheet1.cell(member_row,8).value).strip(),
	                "en_first_name": str(sheet1.cell(member_row,7).value).strip(),
	                "email": str(sheet1.cell(member_row,12).value).strip(),
	                "phone": str(sheet1.cell(member_row,16).value).strip().replace(".",""),
	                "mobile": str(sheet1.cell(member_row,25).value).strip().replace(".",""),
	                "other_phone": str(sheet1.cell(member_row,26).value).strip().replace(".",""),
	                "internal_noted": str(sheet1.cell(member_row,24).value).strip(),
	                "wechat": str(sheet1.cell(member_row,11).value).strip(),
	                "country": str(sheet1.cell(member_row, 9).value).strip()
                }
                person_com_id = str(sheet1.cell(member_row,22).value).strip()
                if str(sheet1.cell(member_row,3).value).strip() == 'ZR' or str(sheet1.cell(member_row,3).value).strip() == 'Zetwork':
                    if not person_com_id:
                        no_com_members.append(_dict)
                for company_id in company_list:
                    if company_id['w_id'] == str(sheet1.cell(member_row,22).value).strip():
                        # company_id['membership_list'].append(_dict)
                        #实现公司和个人1比1
                        # _dict['c_id'] = json.dumps(company_id)
                        _dict['c_id'] = company_id
                        person_list.append(_dict)
            # print("个人和公司对应",person_list)
            # srivice_type_ida = self.env['hotel.service.type'].sudo().search([("name", '=', "空間租用")])
            # srivice_type_idb = self.env['hotel.service.type'].sudo().search([("name", '=', "專業交流")])

            #根据个人的来创建公司，实现个人和公司1对1
            for x in person_list:
                com_id = self.env['res.partner'].sudo().create({
	                        "name": x['c_id']['name'],
	                        "company_type": x['c_id']['company_type'],
	                        "phone":x['c_id']["phone"],
	                        "is_company": 1,
	                        "membership_level": 1
	                    })[0]
                # self.env['membership.points.lines'].sudo().create({
	            #             "name": "空間租用",
	            #             "partner_id": com_id.id,
	            #             "member_type": "package",
	            #             "service_type_id": srivice_type_ida.id,
	            #             "points": 150,
	            #         })
                # self.env['membership.points.lines'].sudo().create({
	            #             "name": "專業交流",
	            #             "partner_id": com_id.id,
	            #             "member_type": "package",
	            #             "service_type_id": srivice_type_idb.id,
	            #             "points": 1850,
	            #         })
                per_id = self.create_person_partner(x)
                sql = """INSERT INTO personal_or_company_rel (current_id, relation_id)
                 VALUES (%s,%s);""" % (per_id.id, com_id.id)
                self._cr.execute(sql)
                self._cr.commit()
                sql = """INSERT INTO company_to_personal_rel (company_id, personal_id)
                                    VALUES (%s,%s);""" % (com_id.id, per_id.id)
                self._cr.execute(sql)
                self._cr.commit()
            # for x in company_list:
            #     com_id=self.env['res.partner'].sudo().create({
	        #         "name": x['name'],
	        #         "company_type": x['company_type'],
	        #         "phone": x["phone"],
	        #         "is_company": 1,
	        #         "membership_level": 1
            #     })[0]
            #     # 赠送积分
            #     self.env['membership.points.lines'].sudo().create({
	        #         "name": "空間租用",
	        #         "partner_id": com_id.id,
	        #         "member_type": "package",
	        #         "service_type_id": srivice_type_ida.id,
	        #         "points": 150,
            #     })
            #     self.env['membership.points.lines'].sudo().create({
	        #         "name": "專業交流",
	        #         "partner_id": com_id.id,
	        #         "member_type": "package",
	        #         "service_type_id": srivice_type_idb.id,
	        #         "points": 1850,
            #     })
            #     for y in x['membership_list']:
            #         if y:
            #             per_id = self.create_person_partner(y)
            #             sql = """INSERT INTO personal_or_company_rel (current_id, relation_id)
			#             VALUES (%s,%s);""" % (per_id.id, com_id.id)
            #             self._cr.execute(sql)
            #             self._cr.commit()
            #             sql = """INSERT INTO company_to_personal_rel (company_id, personal_id)
			#             			            VALUES (%s,%s);""" % (com_id.id, per_id.id)
            #             self._cr.execute(sql)
            #             self._cr.commit()
			#
            # #创建没有公司的人
            # print(len(no_com_members))
            for t in no_com_members:
                if t:
                    self.create_person_partner(t)
            # print(company_list)
            # for x in company_list:
            #     print(x['membership_list'])
            # print("服务领域",service_type_list)
            # print("服务领域长度",len(service_type_list))
            # print("服务领域",list(set(service_type_list)))
            # print("服务领域",len(list(set(service_type_list))))
	#
    #     if no_find_list:
    #         res = ", ".join(no_find_list)
    #         self.env.user.notify_warning(res,u'这些产品没有成功写入属性',sticky=True)