# Printing Service is wrapper around Escpos for easy formatting the invoice

You can define your own methods like RecieptFormatter.fromat_sales_invoice to match your design needs.

# Usage 
It's pretty simple to use
Intialize as follow
```
PrintingServer().init()
```
once properly initialized it can be used anywhere in your project by importing PrintingService from module

# Example
```
from printing_service import PrintingService

PrintingService().init()

invoice = {
    'company': 'My Food', 
    'orderno': 'Order # 01042021-000001', 
    'servetype': 'Eat In', 
    'total': ('Total', '£11.5'), 
    'payable': ('Payable', '£11.5'), 
    'qty': ('Total Quantity', '3'), 
    'pay_method': ('Cash', '£11.5'), 
    'discount': ('Discount', '£0.0'), 
    'change': ('Cash Change', '£0.0'), 
    'servedby': 'Order Served By Till Admin', 
    'datetime': 'Date / Time : 01-Apr-2021 04:58:11 PM', 
    'table': {
        'header': ('Description', 'Qty', 'Total'), 
        'body': [
            ('Tikka Bites On Chips Or Naan', '1', '6.5'), 
            (' --> 1 X Salad', '1', '0.0'), 
            (' --> Cubed Chicken Tikka', '1', '0.0'), 
            ('3 Strips', '1', '2.0'), 
            ('5 Strips', '1', '3.0')
        ]
    }
}

PrintingService.service.create_sales_invoice(invoice)

```
Feel free to tweak around, I've added the detailed description in all methods, beside the code is self explanatory. 

# Note 
This module uses a third part Logger which is also supplied with it