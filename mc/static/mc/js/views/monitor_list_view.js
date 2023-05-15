var app = app || {};

app.MonitorListView = Backbone.View.extend({
  el: '#monitor_list',

  events: {
    'update-sort-mons': 'updateSort',
    'click .apply': 'apply'
    },

  showGlobalApply: function() {
    $('#main_apl_btn').removeClass('hidden');
  },

  updateSort: function(_event, model, position) {
    this.collection.remove(model);

    this.collection.each(function (model, index) {
      let ordinal = index;
      if (index >= position) {
        ordinal++;
      }
      model.set('sequence', ordinal);
    });

    model.set('sequence', position);
    this.collection.add(model, {at: position});
  },

  initialize: function() {
    this.listenTo(app.monitors, 'show_global_apply', this.showGlobalApply);
    this.listenTo(this.collection, 'reset', this.addAll);
    this.listenTo(this.collection, 'add', this.addAll);
  },

  addOne: function(monitor) {
    const view = new app.MonitorView({model:monitor, collection:app.playlists});
    this.$el.append(view.render().el);
  },

  addAll: function() {
    this.collection.each(this.addOne, this);
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    this.addAll();
    return this;
  },

  checkPlTime: function() {
    let noDoubles = true;
    this.collection.each(model => {
      const mon_pls = app.playlists.where({monitor: model.id});
      let pl_times = {};
      for (let i = 0; i < mon_pls.length; i++) {
        const pl = app.playlists.get(mon_pls[i]);
        const pl_time = pl.get('time_begin');
        if (pl_time in pl_times) {
          pl_times[pl_time]++;
        } else {
          pl_times[pl_time] = 1;
        }
      }
      for (let key in pl_times) {
        if (pl_times[key] > 1) {
          const msg = model.get('name') + ' - ошибка! Одинаковое время начала у плейлистов: ' + key;
          alert(msg);
          noDoubles = false;
        }
      }
    });
    return noDoubles;
  },

  apply: function() {
    if (!this.checkPlTime()) {
      return;
    }

    if (app.checkEmptyPls()) {
      if (!confirm('Пустые плейлисты будут удалены. Вы хотите продолжить?')) {
        return;
      } else {
        app.clearEmptyPls();
      }
    }

    const mons = this.collection.where({changed: true});
    let hosts_to_update = {};
    for (let i = 0; i < mons.length; i++) {
      const mon = mons[i];
      hosts_to_update[mon.get('host')] = mon;
      mons[i].trigger('external_apply');
    }

    if (mons.length > 0) {
      app.hideApply();
    }

    //дождемся пока все плейлисты сохранятся, а потом уж запустим обновление
    $.when.apply($, app.prms_array).done(() => {
      app.mons_updating = Object.keys(hosts_to_update).length;
      for (let key in hosts_to_update) {
        if (hosts_to_update.hasOwnProperty(key)) {
          (hosts_to_update[key]).trigger('external_fire_apply');
        }
      }
    });
  }
});
