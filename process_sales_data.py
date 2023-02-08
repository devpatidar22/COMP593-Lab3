from sys import argv, exit
import os
from datetime import date
import pandas as pd
import re
import openpyxl


def main():
    sales_csv = get_sales_csv()
    orders_dir = create_orders_dir(sales_csv)
    process_sales_data(sales_csv, orders_dir)
    return


def get_sales_csv():

    num_parmams = len(argv)-1
    if num_parmams >= 1:
        sales_csv = argv[1]
        if os.path.isfile(sales_csv):
            return sales_csv
        else:
            print('Error: Invalid path to sales data CSV file')
            exit(1)

    else:
        print('Error: Missing path to sales data CSV file')
        exit(1)


def create_orders_dir(sales_csv):
    sales_dir = os.path.dirname(os.path.abspath(sales_csv))
    todays_date = date.today().isoformat()
    orders_dir = os.path.join(sales_dir, f'Orders_{todays_date}')

    if not os.path.isdir(orders_dir):
        os.makedirs(orders_dir)

    return orders_dir


def process_sales_data(sales_csv, orders_dir):
    sales_df = pd.read_csv(sales_csv)
    sales_df.insert(7, "TOTAL PRICE",
                    sales_df['ITEM QUANTITY'] * sales_df['ITEM PRICE'])
    sales_df.drop(columns=['ADDRESS', 'CITY', 'STATE',
                  'POSTAL CODE', 'COUNTRY'], inplace=True)

    for order_id, order_df in sales_df.groupby('ORDER ID'):
        order_df.drop(columns=['ORDER ID'], inplace=True)

        order_df.sort_values(by='ITEM NUMBER', inplace=True)

        grand_total = order_df['TOTAL PRICE'].sum()
        grand_total_df = pd.DataFrame(
            {'ITEM PRICE': ['GRAND TOTAL: '], 'TOTAL PRICE': [grand_total]})
        order_df = pd.concat([order_df, grand_total_df])
       
        export_order_to_excel(order_id, order_df, orders_dir)


def export_order_to_excel(order_id, order_df, orders_dir):
    customer_name = order_df['CUSTOMER NAME'].values[0]
    customer_name = re.sub(r'W', '', customer_name)
    order_file = f'Order{order_id}_{customer_name}.xlsx'
    order_path = os.path.join(orders_dir, order_file)
    sheet_name = f'Order #{order_id}'
    
    writer = pd.ExcelWriter(order_path, engine='xlsxwriter')
    order_df.to_excel(writer, sheet_name=sheet_name)
    workbook  = writer.book
    worksheet = writer.sheets[sheet_name]
    format3 = workbook.add_format({'num_format': '$# #,##0.00'})

    worksheet.set_column(0, 0, 11, None)
    worksheet.set_column(1,1,13,None)
    worksheet.set_column(2,4,15,None)
    worksheet.set_column(6, 7, 13, format3)
    worksheet.set_column(7, 7, 10, format3)
    worksheet.set_column(8, 8, 30, format3)
    writer.close()

    w = openpyxl.load_workbook(order_path)
    wsh = w.active
    wsh.delete_cols(1)
    w.save(order_path)

    return


if __name__ == '__main__':
    main()