from .fun_excel import *
from .fun_base import log
from .fun_file import read_dict_from_file, read_dict_from_file_ex, write_dict_to_file, write_dict_to_file_ex, delete_file
from .time_utils import TimeUtils
from .wxwork import WxWorkBot

class TemuExcel:

    def __init__(self, config, bridge):
        self.config = config
        self.bridge = bridge

    def write_funds(self):
        cache_file = f'{self.config.auto_dir}/temu/cache/funds_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)
        data = []
        for key, val in dict.items():
            data.append(val)

        excel_path = create_file_path(self.config.excel_temu_fund)
        data.insert(0, ['汇总', '', '', '', ''])
        data.insert(0, ['店铺名称', '总金额', '可用余额', '-', '导出时间'])
        log(data)
        # 删除第 4 列（索引为 3）
        for row in data:
            row.pop(3)  # 删除每行中索引为 3 的元素

        write_data(excel_path, 'Sheet1', data)

        app, wb, sheet = open_excel(excel_path, 'Sheet1')
        beautify_title(sheet)
        format_to_money(sheet, ['金额', '余额'])
        format_to_datetime(sheet, ['时间'])
        add_sum_for_cell(sheet, ['总金额', '可用余额'])
        add_borders(sheet)
        close_excel(app, wb)

    def format_purchase_advise_batch(self, sheet):
        beautify_title(sheet)
        format_to_datetime(sheet, ['时间'])
        format_to_number(sheet, ['平均日销', '本地和采购可售天数', '建议采购'], 1)
        add_borders(sheet)
        add_formula_for_column(sheet, '平均日销', '=G2/7')
        add_formula_for_column(sheet, '本地和采购可售天数', '=IF(H2>0,(E2+F2)/H2,0)')
        add_formula_for_column(sheet, '建议采购', '=IF(J2>I2,H2*9,0)')
        colorize_by_field(sheet, 'SKC')
        autofit_column(sheet, ['店铺名称', '商品信息'])
        column_to_left(sheet, ['商品信息'])
        InsertImageV2(sheet, ['SKC图片', 'SKU图片'], 'temu', 120)

    def write_purchase_advise(self, erp='mb'):
        cache_file = f'{self.config.auto_dir}/temu/cache/warehouse_list_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)

        store_info = read_dict_from_file(self.config.temu_store_info)

        header = ['店铺名称', 'SKC图片', 'SKU图片', '商品信息', '现有库存数量', '已采购数量', '近7日销量', '平均日销', '本地和采购可售天数', '生产天数', '建议采购', '产品起定量', '备货周期(天)', 'SKC', '导出时间']
        new_excel_path_list = []
        for mall_id, subOrderList in dict.items():
            excel_data = []
            mall_name = store_info.get(mall_id)[1]
            for product in subOrderList:
                spu = str(product['productId'])  # temu平台 spu_id
                skc = str(product['productSkcId'])  # temu平台 skc_id
                skcExtCode = product['skcExtCode']  # 商家 SKC货号
                category = product['category']  # 叶子类目
                onSalesDurationOffline = product['onSalesDurationOffline']  # 加入站点时长
                for sku in product['skuQuantityDetailList']:
                    priceReviewStatus = sku['priceReviewStatus']
                    if priceReviewStatus == 3:  # 过滤 开款价格状态 已作废的  2是已生效
                        continue
                    mall_info = f'{mall_name}\n{mall_id}'
                    productSkcPicture = product['productSkcPicture']  # skc图片
                    skuExtCode = str(sku['skuExtCode'])  # sku货号
                    sku_img = self.bridge.get_sku_img(skuExtCode, erp)
                    stock = self.bridge.get_sku_stock(skuExtCode, erp)

                    product_info = f"SPU: {spu}\nSKC: {skc}\nSKC货号: {skcExtCode}\nSKU货号: {skuExtCode}\n属性集: {sku['className']}\n类目: {category}\n加入站点时长: {onSalesDurationOffline}天\n"

                    row_item = []
                    row_item.append(mall_info)
                    row_item.append(productSkcPicture)
                    row_item.append(sku_img)
                    row_item.append(product_info)
                    row_item.append(stock)
                    row_item.append(0)
                    row_item.append(sku['lastSevenDaysSaleVolume'])
                    row_item.append(0)
                    row_item.append(0)
                    row_item.append(7)
                    row_item.append(0)
                    row_item.append(0)
                    row_item.append(0)
                    row_item.append(skc)
                    row_item.append(TimeUtils.current_datetime())
                    excel_data.append(row_item)

            new_excel_path = str(self.config.excel_purcase_advice_temu).replace('#store_name#', mall_name).replace(' ', '_')
            new_excel_path_list.append(new_excel_path)
            sheet_name = 'Sheet1'
            data = [header] + excel_data
            close_excel_file(new_excel_path)
            log(new_excel_path)
            batch_excel_operations(new_excel_path, [
                (sheet_name, 'write', sort_by_column(data, 6, 1), ['N']),
                (sheet_name, 'format', self.format_purchase_advise_batch)
            ])

        return new_excel_path_list
