odoo.define('report.dgii.sale', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var QWeb = core.qweb;

    var IncomeTypeWidget = AbstractField.extend({
        _render: function () {
            var info = JSON.parse(this.value);

            if (!info) {
                this.$el.html('');
                return;
            }

            this.$el.html(QWeb.render('IncomeTypeWidget', {
                lines: info.income_type,
                ncfs: info.ncf_type
            }));

        },
    });

    field_registry.add('income_type', IncomeTypeWidget);


    var ExpenseTypeWidget = AbstractField.extend({
        _render: function () {
            var info = JSON.parse(this.value);

            if (!info) {
                this.$el.html('');
                return;
            }

            this.$el.html(QWeb.render('ExpenseTypeWidget', {
                lines: info.expense_lines,
            }));
        },
    });

    field_registry.add('expense_type', ExpenseTypeWidget);

return {
    ExpenseTypeWidget: ExpenseTypeWidget,
    IncomeTypeWidget: IncomeTypeWidget
}
});