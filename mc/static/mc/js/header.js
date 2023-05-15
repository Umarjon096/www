var app = app || {};

app.HeaderView = Backbone.View.extend({
  el: '#host_settings_region',

  events: {
    'click .apply_bl': 'applySettings',
    'click .day_adder': 'addDay',
    'click .del': 'delDay',
    'click .clear': 'clearValues'
  },

  clearValues: function(event) {
    const currentEl = $(event.currentTarget).parent();
    currentEl.find('.time_begin').val(null);
    currentEl.find('.time_end').val(null);
  },

  addDay: function() {
    const selector = $('#week').find('option:selected');
    if (selector.prop('disabled')) {
      return;
    }
    selector.prop('disabled', true);
    $(`.day[day|=${selector.val()}]`).slideDown();
  },

  delDay: function(event) {
    const day = $(event.currentTarget).siblings('.day_of_week').val();
    const currentEl = $(event.currentTarget).parent();
    currentEl.find('.time_begin').val(null);
    currentEl.find('.time_end').val(null);
    currentEl.slideUp();
    $(`#week option[value=${day}]`).prop('disabled', false);
  },

  pullBlackouts: function() {
    const that = this;
    $.get(
      '/blackouts/',
      data => {
        that.populateBLs(data);
      }
    );
  },

  populateBLs: function(data) {
    const j_data = JSON.parse(data);
    const region = $('#host_settings_region');
    for (let i = 0; i < j_data.length; i++) {
      const bl = j_data[i];
      const day = region.find(`input.day_of_week[value="${bl.day_of_week}"]`).parent();
      day.find('.time_end').val(bl.time_end);
      day.find('.time_begin').val(bl.time_begin);
      if (bl.day_of_week > 0) {
        day.show();
        $(`week option[value=${bl.day_of_week}]`).prop('disabled', true);
      }
    }
  },

  applySettings: function(event) {
    const that = this;
    const set_rgn = $('#host_settings_region');
    const rows = set_rgn.find('.day');
    let new_bls = {};
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const dayofweek = parseInt($(row).find('.day_of_week').val());
      const time_end = $(row).find('.time_end').val();
      const time_begin = $(row).find('.time_begin').val();
      const active = (time_end != '' && time_begin != '');
      if (active) {
        new_bls[dayofweek] = {'time_end': time_end, 'time_begin': time_begin};
      }
    }
    if (Object.keys(new_bls).length > 1 && new_bls[0] != undefined) {
      alert('Установлен общий интервал. Пожалуйста, очистите дневные интервалы.');
      return;
    }
    this.toggleLoad(set_rgn, false);
    $.post(
      '/blackouts/',
      JSON.stringify(new_bls)
    ).done(res => {
      that.populateBLs(res, set_rgn);
      messageSuccess('Интервалы работы сохранены');
      $('#monitor').modal('hide');
      that.toggleLoad(set_rgn, true);
    }).fail(res => {
      console.log(res);
      messageError(res.responseText);
      that.toggleLoad(set_rgn, true);
    })
  },

  toggleLoad: function(region, showButtons) {
    if (showButtons) {
      region.find('.lds-facebook').hide();
      region.find('.modal-footer').show();
    } else {
      region.find('.lds-facebook').show();
      region.find('.modal-footer').hide();
    }
  },

  initialize: function() {
    this.pullBlackouts();
  }
});

app.HV = new app.HeaderView();
