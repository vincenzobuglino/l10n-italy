odoo.define("fiscal_epos_print.pos_order_mgmt", function (require) {
    "use strict";

    var core = require("web.core");
    var pos_order_mgmt = require('pos_order_mgmt.widgets');
    var epson_epos_print = require('fiscal_epos_print.epson_epos_print');
    var _t = core._t;
    var OrderListScreenWidget = pos_order_mgmt.OrderListScreenWidget;
    var eposDriver = epson_epos_print.eposDriver;

    OrderListScreenWidget.include({
        _prepare_order_from_order_data: function (order_data, action) {
            var order = this._super(order_data, action);
            if (action === 'print') {
                order.refund_report = order_data.refund_report;
                order.refund_date = order_data.refund_date;
                order.refund_doc_num = order_data.refund_doc_num;
                order.refund_cash_fiscal_serial = order_data.refund_cash_fiscal_serial;
            }
            else if (action === 'return') {
                order.refund_report = order_data.fiscal_z_rep_number;
                order.refund_date = order_data.fiscal_receipt_date;
                order.refund_doc_num = order_data.fiscal_receipt_number;
                order.refund_cash_fiscal_serial = order_data.fiscal_printer_serial;
            }
            // for action === 'copy' we don't need to do anything

            return order;
        },
        // copiato da screens.PaymentScreenWidget
        getPrinterOptions: function (){
            var protocol = ((this.pos.config.use_https) ? 'https://' : 'http://');
            var printer_url = protocol + this.pos.config.printer_ip + '/cgi-bin/fpmate.cgi';
            return [{url: printer_url}];
        },
        // copiato da screens.PaymentScreenWidget
        sendToFP90Printer: function(receipt, printer_options) {
            for (var i = 0; i < printer_options.length; i++){
                var printer_option = printer_options[i];
                var fp90 = new eposDriver(printer_option, this);
                fp90.printFiscalReceipt(receipt);
            }
        },
        action_print: function (order_data, order) {
            if (this.pos.config.printer_ip) {
                if (order_data.fiscal_receipt_number) {
                    this.pos.gui.show_popup('error', {
                        'title': _t('Order already printed'),
                        'body': order_data.pos_reference + _t(": order already has a fiscal number, ") + order_data.fiscal_receipt_number,
                    });
                    return;
                }
                var receipt = order_data.export_for_printing();
                var printer_options = this.getPrinterOptions();
                printer_options.order = order_data;
                this.sendToFP90Printer(receipt, printer_options);
            }
            return this._super(order_data, order);
        },
    });

});
