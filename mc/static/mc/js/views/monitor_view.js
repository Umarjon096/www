var app = app || {};

app.MonitorView = Backbone.View.extend({
  tagName: 'div',
  className: 'screen',
  template: _.template($('#monitor-template').html()),

  events: {
    'click .add_pl': 'addPL',
    'click .apply': 'apply',
    'change': 'setChanged',
    'change .volume_style': 'changeVol',
    'input .volume_style': 'changeDisplayVol',
    'change .pl_volume': 'changeVol',
    'mon-changed': 'setChanged',
    'update-sort-on-delete': 'updateSortOnDelete',
    'adv-checked': 'addAll'
  },

  changeDisplayVol: function(event){
    let filtered_vol = event.target.value;
    this.$el.find('#pl_volume').val(filtered_vol);
  },

  changeVol: function(event) {
    event.stopImmediatePropagation();
    const that = this;
    that.$el.find('#volume').prop('disabled', true);
    let filtered_vol = event.target.value;
    if (filtered_vol == 60) {
      filtered_vol = 1;
    }
    $.ajax({
      url: '/set_host_volume/',  //Server script to process data
      type: 'POST',
      //Ajax events
      //beforeSend: beforeSendHandler,
      success: res => {
        that.$el.find('#volume').val(res);
        that.$el.find('#pl_volume').val(Math.round(res));
        that.$el.find('#volume').prop('disabled', false);
      },
      error: e => handleError(
        e,
        'Ошибка! В случае повторения обратитесь в техподдержку.'
      ),
      // Form data
      data: JSON.stringify({mon_id: this.model.id, volume: filtered_vol}),
      //Options to tell jQuery not to process data or worry about content-type.
      cache: false,
      contentType: false,
      processData: false
    });
  },

  setChanged: function() {
    if (app.loadingContent != 0) {
      return;
    }

    this.model.set('changed', true);
    this.$el.addClass('changed_mon');
    this.model.trigger('show_global_apply');
  },

  commitChanges: function() {
    this.model.set('changed', false);
    this.$el.removeClass('changed_mon');
  },

  updateSort: function(_event, model, position) {
    this.collection.remove(model);

    _.each(
      this.collection.where({
        monitor: this.model.id
      }),
      (model, index) => {
        let ordinal = index;
        if (index >= position) {
          ordinal++;
        }
        model.set('sequence', ordinal);
      }
    );

    model.set('sequence', position);
    this.collection.add(model, {at: position});
  },

  updateSortOnDelete: function() {
    let ordinal = 1;
    _.each(
      this.collection.where({
        monitor: this.model.id
      }),
      model => {
        model.set('sequence', ordinal);
        ordinal++;
      }
    );
  },

  initialize: function() {
    this.listenTo(this.collection, 'reset', this.addAll);
    this.listenTo(this.collection, 'add', this.addAll);
    // this.listenTo(this.collection, 'change', this.addAll);
    this.listenTo(this.collection, 'destroy', this.updateSortOnDelete);
    this.listenTo(this.collection, 'destroy', this.addAll);
    this.listenTo(app.pics, 'reset', this.displayCurImg);
    this.listenTo(this.model, 'external_apply', this.apply);
    this.listenTo(this.model, 'external_fire_apply', this.fireApply);
    this.listenTo(this.model, 'commit_changes', this.commitChanges);
    this.curWatcher();
  },

  addOne: function(playlist) {
    const view = new app.PlaylistView({model:playlist, collection:app.pics});
    this.$('.playlists').append(view.render().el);
  },

  addAll: function() {
    this.$('.playlists').html('');
    let filtered_col = this.collection.where({monitor: this.model.id});
    _.each(filtered_col, this.addOne, this);
    if (filtered_col.length == 1) {
      this.$('.playlists').addClass('bt_hidden');
    } else {
      this.$('.playlists').removeClass('bt_hidden');
    }
  },

  render: function() {
    if (this.model.get('music_box')) {
      this.$el.addClass('music_mon');
    }
    this.$el.html(this.template(this.model.toJSON()));
    this.addAll();
    this.get_volume();
    return this;
  },

  get_volume: function() {
    if (!this.model.get('music_box')) {
      return;
    }
    const that = this;
    $.ajax({
      url: '/get_host_volume/',  //Server script to process data
      type: 'POST',
      //Ajax events
      //beforeSend: beforeSendHandler,
      success: res => {
        that.$el.find('#volume').val(res);
        that.$el.find('#pl_volume').val(Math.round(res));
      },
      error: e => handleError(
        e,
        'Ошибка! В случае повторения обратитесь в техподдержку.'
      ),
      // Form data
      data: this.model.id,
      //Options to tell jQuery not to process data or worry about content-type.
      cache: false,
      contentType: false,
      processData: false
    });
  },

  get_cur_song: function() {
    const that = this;
    $.ajax({
      url: '/get_current_song/',
      type: 'POST',

      success: res => {
        that.$el.find('.screen-top__song').text(res);
        that.$el.find('.screen-top__song').attr('title', 'Текущая песня: ' + res);
      },

      error: e => handleError(
        e,
        'Ошибка! В случае повторения обратитесь в техподдержку.'
      ),
      // Form data
      data: that.model.id,
      //Options to tell jQuery not to process data or worry about content-type.
      cache: false,
      contentType: false,
      processData: false
    });
  },

  get_cur_image_old: function(oldHtml) {
    $.ajax({
      url: '/get_current_image/',
      type: 'POST',

      success: res => {
        this.$el.find('.screen-top__icon').html(`<img src="${res}">`);
      },

      error: e => {
        this.$el.find('.screen-top__icon').html(oldHtml);
      },

      data: this.model.id,
      cache: false,
      contentType: false,
      processData: false
    });
  },

  get_cur_image: function(){
    //найдём текущий плейлист
    var now = new Date();

    var pl_now = new Date(); //возмём текущую дату за опорную для вычисления времени плейлиста
    
    var prev_pl_now = new Date();
    prev_pl_now.setHours(0);
    prev_pl_now.setMinutes(0);
    prev_pl_now.setSeconds(0);

    var prev_pl = null;

    const mon_pls = this.collection.where({monitor: this.model.id});
    const mon_len = mon_pls.length;
    for (let i = 0; i < mon_len; i++) {
      const pl = this.collection.get(mon_pls[i]);
      let pl_time_arr = pl.get('time_begin').split(':');
      pl_now.setHours(pl_time_arr[0]);
      pl_now.setMinutes(pl_time_arr[1]);
      pl_now.setSeconds(0);
      
      if (!prev_pl)
        prev_pl = pl;       


      if ((prev_pl_now < now && now < pl_now)|| i == mon_len-1){
        if (i == mon_len-1)
        {
          prev_pl_now = pl_now;
          prev_pl = pl;
        }
          

        //нашли плейлист, теперь найдём текущий файл
        let pl_pics = app.pics.where({playlist: pl.id});
        // console.log('PL NOW', pl_pics);
        const pics_len = pl_pics.length;
        let sum_dur = 0;
        let pics_end_times = [];
        for (let j = 0; j < pics_len; j++) {
          const pic = app.pics.get(pl_pics[j]);
          let pic_dur = pic.get('duration');
          sum_dur += pic_dur*1000;
        }
        if (sum_dur == 0) //если длительности ни у кого нет, то и считать нечего
          return;
        // console.log(now, prev_pl_now);
        let unix_now = now.getTime();
        let prev_pl_unix_now = prev_pl_now.getTime();
        while (unix_now > prev_pl_unix_now) {
          prev_pl_unix_now += sum_dur;
        }      
        // console.log(unix_now, prev_pl_unix_now, sum_dur);
        let media_start_time = prev_pl_unix_now - sum_dur;
        // console.log(unix_now, media_start_time);
        for (let j = 0; j < pics_len; j++) {
          const pic = app.pics.get(pl_pics[j]);
          
          let pic_dur = pic.get('duration');
          media_start_time += pic_dur*1000;
          pics_end_times.push([pic.get('thumb_url'), media_start_time])
          // console.log(pics_end_times);
        }
        let result_url = '';
        for (let media of pics_end_times){
          if (unix_now < media[1]) {
            //console.log('CUR M:', media[0]);
            result_url = media[0];
            break;
          }
          result_url = media[0];
        }
        this.checkAndReplaceImg(result_url);


      }
      prev_pl_now = pl_now;
      prev_pl = pl;

    }

    //

  },

  checkAndReplaceImg(new_img_url){
    let cur_url = this.$el.find('.screen-top__icon img').attr('src');
    // console.log(cur_url, new_img_url);
    if (new_img_url != cur_url)
      this.$el.find('.screen-top__icon').html(`<img src="${new_img_url}">`);
  },

  curWatcher: function() {
    const self = this;

    if (this.model.get('music_box')) {
      this.get_cur_song();

      setInterval(
          () => {
          self.get_cur_song();
        },
        15000
      );

    } else {
      const old = place = this.$el.find('.screen-top__icon').html();

      // this.get_cur_image(old);

      setInterval(
          () => {
          self.get_cur_image(old);
        },
        1000
      );
    }
  },

  addPL: function() {
    const mon_pls = this.collection.where({monitor: this.model.id});
    const mon_len = mon_pls.length;
    let eldest_time = "";
    let new_time = "00:00";
    for (let i = 0; i < mon_len; i++) {
      const pl = this.collection.get(mon_pls[i]);
      if (pl.get('time_begin') > eldest_time) {
        eldest_time = pl.get('time_begin');
      }
    }

    if (eldest_time != "") {
      const time_arr = eldest_time.split(':');
      if (time_arr[0] >= "23") {
        new_time = "23:59";

      } else {
        const pad = "00";
        const hours = parseInt(time_arr[0]) + 1;
        new_time = (pad + hours.toString()).slice(-pad.length) + ':' + time_arr[1];
      }
    }

    const pl_type = this.model.get('music_box') ? 'audio' : 'hybrid';

    const new_pl = new app.Playlist({
      sequence: mon_len + 1,
      time_begin: new_time,
      monitor: this.model.id,
      content_type: pl_type,
      volume: undefined
    });
    new_pl.save();
    this.$el.trigger('mon-changed');
    this.collection.add(new_pl);
  },

  apply: function() {
    let dfd = new $.Deferred();
    const pls = this.collection.where({monitor: this.model.id});
    let left_to_process = pls.length;
    for (let i = 0; i < pls.length; i++) {
      pls[i].save().always(() => {
        left_to_process -= 1;
        if (left_to_process == 0) {
          dfd.resolve();
        }
      });
    }
    app.prms_array.push(dfd.promise());
    if (pls.length == 0) {
      dfd.resolve();
    }
  },

  fireApply: function() {
    this.model.apply_is_firing = true;
    const that = this;
    const mon_sg = this.model.get('sync_group');
    let lowest_host_id = this.model.get('host');
    let mon_from_lowest_host = this.model.id;
    let lower_host_mon_obj = undefined;
    if (mon_sg) {
      _.each(
        app.monitors.where({
          sync_group: mon_sg
        }),
        model => {
          if (model.get('host') < lowest_host_id) {
            lowest_host_id = model.get('host');
            mon_from_lowest_host = model.id;
            lower_host_mon_obj = model;
          }
        }
      );
    }

    if (mon_from_lowest_host !== this.model.id) {
      if(!lower_host_mon_obj.apply_is_firing)
        lower_host_mon_obj.trigger('external_fire_apply');
      return;
    }

    $.ajax({
      url: '/pl_command/',  //Server script to process data
      type: 'POST',
      //Ajax events
      //beforeSend: beforeSendHandler,
      success: res => {
        if (res == 'ok') {
          that.model.apply_is_firing = true;
          if (mon_sg) {
            _.each(
              app.monitors.where({
                sync_group: mon_sg
              }),
              model => {
                model.trigger('commit_changes');
                app.mons_updating -= 1;
                if (app.mons_updating == 0) {
                  app.showApply();
                }
              }
            );
          } else {
            const mons = app.monitors.where({host: that.model.get('host')});
            for (let i = 0; i < mons.length; i++) {
              mons[i].trigger('commit_changes');
            }
            app.mons_updating -= 1;
            if (app.mons_updating == 0) {
              app.showApply();
            }
          }
        } else {
          console.log(res);
          messageError('Ошибка! В случае повторения обратитесь в техподдержку. \n' + res);
        }
      },
      error: e => {
        that.model.apply_is_firing = true;
        handleError(
        e,
        'Ошибка! В случае повторения обратитесь в техподдержку.'
      )},
      // Form data
      data: JSON.stringify({"id": mon_from_lowest_host}),
      //Options to tell jQuery not to process data or worry about content-type.
      cache: false,
      contentType: false,
      processData: false
    });
  }
});
