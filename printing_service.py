import os
from math import floor
from escpos.printer import Serial, Network, Usb, Dummy
from logger import Logger

class PrintingService:
    initialized = False

    class RecieptPrinter(object):
        """This is a wrapper class around escpos.printer to implement some printer connections and passing commands"""
        def __init__(self, **printer_args):\
            self.__printer = None
            printers = {
                'dummy':   self._connect_dummy,
                'network': self._connect_network,
                'usb':     self._connect_usb,
                'serial':  self._connect_serial
            }
            try:
                self.__printer = printers[printer_args['type']](**printer_args)
                Logger.debug(f"{printer_args['type'].upper()} Printer connected: {e.__cause__}")
            except Exception as e:
                Logger.error(f"No {printer_args['type'].upper()} Printer found: {e.__cause__}")

        def is_connected(self):
            """returns True if printer is connected"""
            if self.__printer is None:
                return False
            else:
                return self.__printer.is_online()

        def _connect_dummy(self, **kwargs):
            """Initializes the __printer instance with Dummy printer
               @param: None
               @retrurn: Dummy()
            """
            return Dummy()
            
        def _connect_network(self, **kwargs):
            """Initializes the __printer instance with Network printer
               @param: ip of printer
               @retrurn: Network()
            """
            return Network(kwargs['ip'])
            
        def _connect_serial(self, **kwargs):
            """Initializes the __printer instance with Serial printer
               @param: port
               @param: baudrate
               @retrurn: Serial()
            """
            return Serial(kwargs['port'], baudrate=kwargs['baudrate'])
            
        def _connect_usb(self, **kwargs):
            """Initializes the __printer instance with Usb printer
               @param: profile
               @retrurn: Usb()
            """
            #profile="TM-T88III"
            return Usb(0x04b8, 0x0202, 0, profile=kwargs['profile'])
            
        def print_sales_reciept(self, **invoice):
            """prints keyworded arguments in the sequence
               @param: logo,       str value to print at top mostly company name
               @param: header,     tuple(order_identifier, other detail)
               @param: table,      list(header, body)
               @param: total,      tuple(text, amount)
               @param: payable,    tuple(text, amount payable)
               @param: qty,        tuple(text, quantity)
               @param: pay_method, tuple(text, amount)
               @param: change,     tuple(text, amount)
               @param: discount,   tuple(text, amount)
               @param: footer,     tuple(servedby, datetime)
               @retrurn: None
            """
            self._print_logo        (invoice['logo'])
            self._print_header      (invoice['header'])
            self._print_table       (invoice['table'])
            self._ln()
            self._println           (invoice['total'], bold=True)
            self._println           (invoice['payable'], bold=True)
            self._ln()
            self._println           (invoice['qty'])
            self._println           (invoice['pay_method'])
            self._println           (invoice['change'])
            self._println           (invoice['discount'])
            self._print_footer      (invoice['footer'])
            
            self._cut()

        def _print_logo(self, text):
            """prints the text passed as top level heading 
               @param: text, str type
               @retrurn: None
            """
            self._println(text, align='center', bold=True, double_width=True, double_height=True)
            self._ln(count=1)

        def _print_header(self, lines):
            """prints given lines to reciept header with pre-defined styles
               @param: lines, tuple(strings) atmost two values
               @retrurn: None
            """
            self._print_sep_line()
            self._println(lines[0], font='b', align='center', double_width=True)
            self._ln()
            self._println(lines[1], font='b', align='center', double_width=True, underline=True)
            self._print_sep_line()

        def _print_footer(self, lines, greetings="Thank You"):
            """prints the lines tuple and greeting in the footer
               @param: lines, tuple(strings), 2 values atmost 
               @param: greetings, default is 'Thank You'
               @retrurn: None
            """
            self._print_sep_line()
            self._println(greetings, font='b', align='center', double_width=True)
            self._ln()
            self._println(lines[0])
            self._println(lines[1])

        def _print_sep_line(self, sep='-', count=42):
            """prints a seprator line
               @param: sep, separator charactor deafult is dash '-'
               @param: count, number of characters in a line
               @retrurn: None
            """
            self._println(text=sep * count)

        def _print_table(self, table):
            """prints list of strings
               @param: table, list(string)
               @retrurn: None
            """

            for row in table:
                self._println(row)

        def _print_double_line(self, line):
            """prints a double_width and double_height text
               @param: line, text to be printed
               @retrurn: None
            """
            self._ln()
            self._println(line, font='b', width=2, height=2, custom_size=True)
            self._ln()

        def _println(self, text, **styles):
            """prints text with given styles, thses styles are applied using Escpos.printer.set
               @param: text, text to be printed
               @param: styles, keyworded arguments, to see detailed information about styles see Escpos.printer.set
               @retrurn: None
            """
            self.__printer.set(**styles)
            self.__printer.textln(text)
            
        def _ln(self, count=1):
            """prints empty lines
               @param: count, number of empty lines
               @retrurn: None
            """            
            self.__printer.ln(count=count)

        def _cut(self):
            """calls the cut method of Escpos.printer, cuts the paper
               @param: None
               @retrurn: None
            """
            self.__printer.cut()

        def _ctrl(self, ctl="HT", tab_size=4):
            """set the tab size for next line
               see the Escpos.printer.control for detailed information about parameters
               @param: ctl  
               @param: tab_size, default is 4
               @retrurn: Serial()
            """
            count = 40 // tab_size
            self.__printer.control(ctl, count=count, tab_size=tab_size)

    class RecieptFormatter(RecieptPrinter):
        char_per_line = 42
        
        def __init__(self, **printer_args):
            super().__init__(**printer_args)

        def format_sales_reciept(self, invoice):
            """fromats the invoice data pass it to printer
               @param: invoice, to examine the structure of invoice see below
               @retrurn: None
            """
            if self.is_connected():
                self.print_sales_reciept(
                    logo=invoice['company'],
                    header=(invoice['orderno'], invoice['servetype']),
                    table=self._format_table(
                        data=invoice['table']['body'],
                        division=(0.7, 0.15, 0.15),
                        header=invoice['table']['header']
                    ),
                    total=self._format_single_line(
                        data=invoice['total'],
                        division=(0.5, 0.5)
                    ),
                    payable=self._format_single_line(
                        data=invoice['payable'],
                        division=(0.5, 0.5)
                    ),
                    qty=self._format_single_line(
                        data=invoice['qty'],
                        division=(0.5, 0.5)
                    ),
                    discount=self._format_single_line(
                        data=invoice['discount'],
                        division=(0.5, 0.5)
                    ),
                    pay_method=self._format_single_line(
                        data=invoice['pay_method'],
                        division=(0.5, 0.5)
                    ),
                    change=self._format_single_line(
                        data=invoice['change'],
                        division=(0.5, 0.5)
                    ),
                    footer=(invoice['servedby'], invoice['datetime'])
                )
            else:
                Logger.error(f"Printer not connected")


        def _format_double_line(self, **line_def):
            """formats tuple of strings into a one double_width, double_height string
               @param: division, disvision of line in floating value (0.0-1.0)
               @param: data, tuple of string values
               @retrurn: string
            """
            col_count = len(line_def['division'])
            chars_dist = self._compute_chars_dist(line_def['division'], char_width=1.5)
            line = self._format_line(chars_dist, line_def['data'])
            return line

        def _format_single_line(self, **line_def):
            """formats tuple of strings into a one string
               @param: division, disvision of line in floating value (0.0-1.0)
               @param: data, tuple of string values
               @retrurn: string
            """
            col_count = len(line_def['division'])
            chars_dist = self._compute_chars_dist(line_def['division'], char_width=1)
            line = self._format_line(chars_dist, line_def['data'])
            return line

        def _format_table(self, **table_def):
            """formats the given data into list of strings
               @param: division, tuple of floating values for disvision of line (0.0-1.0)
               @param: data, list of tuples(tuple of string values)
               @param: header, tuple containing the table header values
               @retrurn: list of strings
            """
            col_count = len(table_def['division'])
            chars_dist = self._compute_chars_dist(table_def['division'], char_width=1)
            table = self._format_header(chars_dist, table_def['header'])
            
            for row in table_def['data']:
                table.append(self._format_line(chars_dist, row))
            
            return table

        def _format_header(self, chars_dist, header_data, space_count=2):
            """formats the table header into a list of strings along with seperator as element of list
               @param: char_dist, distribution of characters per column tuple(int)
               @param: header_data, tuple of string values
               @param: space_count, space to leave empty after each column
               @retrurn: list of strings
            """
            header = header_data
            header = []
            col_count = len(chars_dist)
            header.append(self._format_line(chars_dist, header_data))
            header.append(self._format_header_sep(chars_dist, space_count=space_count))
            return header

        def _format_header_sep(self, chars_dist, space_count=2):
            """formats the header seperator into a string
               @param: char_dist, distribution of characters per column tuple(int)
               @param: space_count, space to leave empty after each column
               @retrurn: string
            """
            sep_line = ''
            spaces = ' ' * space_count
            iter = 0
            for dist in chars_dist:
                if iter == len(chars_dist) - 1:
                    sep_line += '-' * dist
                else:
                    sep_line += '-' * dist + (' ' * space_count)
                iter += 1
            return sep_line

        def _format_line(self, chars_dist, data):
            """formats the line, same a _format_single_line but it doesn't calculate its own char_distribution
               @param: char_dist, distribution of characters per column tuple(int)
               @param: data, tuple of string values
               @retrurn: list of strings
            """
            col_count = len(chars_dist)
            availabe_chars = self.char_per_line - ((col_count - 1) * 2)
            line = ""
            iter = 0
            for item in data:
                if iter == len(data) - 1:
                    line += self._format_text(max_chars=chars_dist[iter], text=data[iter], reverse=True)
                else:
                    line += self._format_text(max_chars=chars_dist[iter], text=data[iter])
                iter += 1
            return line

        def _format_text(self, max_chars, text, reverse=False, space_count=2):
            """formats the appending empty spaces as needed
               @param: max_chars, max caharcters are allowed in string
               @param: text, string value to format
               @param: reverse, set True to append spaces at left
               @param: space_count, space to leave empty after each column
               @retrurn: list of strings
            """
            diff = int(max_chars - len(text))
            if diff > 0:
                if reverse:
                    return ' ' * diff + text 
                else:
                    return text + ' ' * ( diff + space_count )
            else:
                if not reverse:
                    return text[:max_chars] + (' ' * space_count)
                else:
                    return text[:max_chars]

        # computes characters distributaion in each col
        def _compute_chars_dist(self, division, char_width=1, space_count=2):
            """computes the character distribution for a given disvision tuple
               @param: division, division of columns in floating values
               @param: char_width, 1 for single_width 2 for double_width
               @param: space_count, space to leave empty after each column
               @retrurn: list of integer values for character distribution
            """
            col_count = len(division)
            availabe_chars = (self.char_per_line//char_width) - ((col_count - 1) * space_count)
            consumed_chars = 0
            chars_dist = []
            iter = 0
            for div in division:
                chars_in_col = floor(availabe_chars*div)
                if iter == len(division) - 1:
                    chars_dist.append((availabe_chars - consumed_chars))
                else:
                    chars_dist.append(chars_in_col)
                    consumed_chars += chars_in_col
                iter += 1
            return chars_dist

    class Service(RecieptFormatter):
        def __init__(self):
            super().__init__(type='serial', port='COM5', baudrate=9600)
        
        def create_sales_invoice(self, invoice):
            self.format_sales_reciept(invoice)
            

    def init(self):
        PrintingService.service = PrintingService.Service()
        self.initialized = True

if __name__ == '__main__':
    Logger().init()
    PrintingService().init()

    # Structure passed to print_sales_invoice
    PrintingService.service.create_sales_invoice({
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
    })
