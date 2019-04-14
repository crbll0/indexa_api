odoo.define('report_dgii', function (require) {
"use strict";

  var core = require('web.core');
  var form_common = require('web.form_common');
  var QWeb = core.qweb;

  var AccountTaxtWidget = form_common.AbstractField.extend({
      render_value: function() {
          var info = JSON.parse(this.get('value'));

          if (info !== false) {
              this.$el.html(QWeb.render('AccountTaxtWidget', {
                  'sales': info.sales,
                  'purchases': info.purchases
              }));
          }
          else {
              this.$el.html('');
          }
      }

  });

  core.form_widget_registry.add('account_taxes', AccountTaxtWidget);

});
