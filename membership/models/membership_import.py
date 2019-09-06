# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/9/6 12:05
"""

from odoo import api, fields, models
import xlrd
import base64
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
		    "internal_noted": y['internal_noted'],
		    "wechat": y['wechat'],
		    # tag_ids.append((4, self.env.ref('l10n_nl.account_tag_25').id))
		    "category_id": [(4, self.env.ref("membership.res_partner_category_data_igba").id)] if y['is_igba'] else None,
	        # "membership_points_lines": [(0,0,{})]
	    })[0]
        #赠送积分
        srivice_type_ida=self.env['hotel.service.type'].sudo().search([("name",'=',"空間租用")])
        self.env['membership.points.lines'].sudo().create({
		    "name": "空間租用",
		    "partner_id": res_id.id,
	        "member_type": "package",
	        "service_type_id": srivice_type_ida.id,
	        "points": 150,
	    })
        srivice_type_idb = self.env['hotel.service.type'].sudo().search([("name", '=', "專業交流")])
        self.env['membership.points.lines'].sudo().create({
	        "name": "專業交流",
	        "partner_id": res_id.id,
	        "member_type": "package",
	        "service_type_id": srivice_type_idb.id,
	        "points": 1850,
        })
        return res_id


    def resize_write_product(self):
        print(self.ids)
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
            print(len(com_id_list),com_id_list)
	        #服务领域list
            service_type_list = []
            #没有公司的人
            no_com_members = []
            for member_row in range(4,sheet1.nrows):
                str0 = str(sheet1.cell(member_row,24).value).strip()
                if str0:
                    str_list = str0.split(";")
                    for res_str in str_list:
                        service_type_list.append(res_str)
                _dict={
	                "is_iba": 1 if str(sheet1.cell(member_row,2).value).strip()=="YES" else 0,
	                "title": str(sheet1.cell(member_row,4).value).strip(),
	                "last_name": str(sheet1.cell(member_row,6).value).strip(),
	                "first_name": str(sheet1.cell(member_row,5).value).strip(),
	                "en_last_name": str(sheet1.cell(member_row,8).value).strip(),
	                "en_first_name": str(sheet1.cell(member_row,7).value).strip(),
	                "email": str(sheet1.cell(member_row,12).value).strip(),
	                "phone": str(sheet1.cell(member_row,16).value).strip().replace(".",""),
	                "mobile": str(sheet1.cell(member_row,25).value).strip().replace(".",""),
	                "other_phone": str(sheet1.cell(member_row,26).value).strip().replace(".",""),
	                "internal_noted": str(sheet1.cell(member_row,24).value).strip(),
	                "wechat": str(sheet1.cell(member_row,11).value).strip(),
	                "country": str(sheet1.cell(member_row, 9).value).strip(),
	                "is_igba":  True if str(sheet1.cell(member_row, 3).value).strip() == "Yes" else False
                }
                # company.country_id = self.ref('base.us')
                person_com_id = str(sheet1.cell(member_row,22).value).strip()
                if not person_com_id or person_com_id not in com_id_list:
                    no_com_members.append(_dict)
                for company_id in company_list:
                    if company_id['w_id'] == str(sheet1.cell(member_row,22).value).strip():
                        company_id['membership_list'].append(_dict)
                    # else:
            print(len(no_com_members))
            for x in company_list:
                com_id=self.env['res.partner'].sudo().create({
	                "name": x['name'],
	                "company_type": x['company_type'],
	                "phone": x["phone"],
	                "is_company": 1,
	                "membership_level": 1
                })[0]
                for y in x['membership_list']:
                    if y:
                        per_id = self.create_person_partner(y)
                        sql = """INSERT INTO personal_or_company_rel (current_id, relation_id)
			            VALUES (%s,%s);""" % (per_id.id, com_id.id)
                        self._cr.execute(sql)
                        self._cr.commit()
                        sql = """INSERT INTO company_to_personal_rel (company_id, personal_id)
			            			            VALUES (%s,%s);""" % (com_id.id, per_id.id)
                        self._cr.execute(sql)
                        self._cr.commit()

            #创建没有公司的人
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

            # for sh in sheets:
            #     for row in range(2, sh.nrows):
            #         vlue_name = str(sh.cell(row,1).value).strip()
            #         product_id = self.env['product.template'].sudo().search([('name','=',vlue_name)])
            #         if product_id:
            #             try:
            #                 vlas={
            #                     "original_price": sh.cell(row, 2).value,
            #                     "list_price": sh.cell(row, 3).value,
            #                     "wxapp_published": sh.cell(row, 4).value,
            #                     "description_wxapp": sh.cell(row, 5).value,
            #                     "website_published": sh.cell(row, 7).value
            #                 }
            #                 print("已找到的产品,",product_id)
            #                 product_id.write(vlas)
            #             except Exception as e:
            #                 print ("写入失败日志",e)
            #         if not product_id:
            #             no_find_list.append(vlue_name)

        if no_find_list:
            res = ", ".join(no_find_list)
            self.env.user.notify_warning(res,u'这些产品没有成功写入属性',sticky=True)