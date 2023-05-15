var app = app || {};

app.PlaylistView = Backbone.View.extend({
  template: _.template($('#playlist-template').html()),

  events: {
    'update-sort': 'updateSort',
    'change .int_input': 'intChange',
    'change .shuffle_select': 'shuffleChange',
    'change .is_adv_select': 'isAdvChange',
    'change .adv_at_once_select': 'advAtOnceChange',
    'click .del': 'delete',
    'click .save': 'save',
    'change .time_begin': 'setTime',
    'change .scale_factor': 'setScale',
    'change .url_refresh_mode': 'setRefreshMode',
    'change .pl_volume': 'setVol',
    'click .radioBtn': 'setCurrentPl'
  },

  isValidDimensions: async function(file) {
    const type = file.type.split("/", 1)[0];
    let tooBig = false;
    let dfd = new $.Deferred();
    if (type == 'audio') {
      return true;
    } else if (type == 'video') {
      dfd.promise();
      const videoNode = document.createElement('video');
      const fileURL = URL.createObjectURL(file);
      videoNode.src = fileURL;
      videoNode.addEventListener(
        'loadedmetadata',
        () => {
          if (videoNode.videoWidth > MAX_MEDIA_SIZE || videoNode.videoHeight > MAX_MEDIA_SIZE) {
            alert('Разрешение медиа не должно превышать '+MAX_MEDIA_SIZE+' пикселей');
            tooBig = true;
          }
          dfd.resolve();
        }
      );
      videoNode.addEventListener('error', function(e){
        switch (e.target.error.code) {
             case e.target.error.MEDIA_ERR_ABORTED:
               alert('Проигрывание остановлено');
               break;
            case e.target.error.MEDIA_ERR_NETWORK:
              alert('Ошибка в сетевом подключении');
              break;
           case e.target.error.MEDIA_ERR_DECODE:
              alert(file.name+' Ошибка декодирования');
              break;
           case e.target.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
             //console.log('Формат не поддерживается');
             alert(file.name+' Формат не поддерживается, используйте MP4');
             break;
           default:
             alert('Неизвестная ошибка');
             break;
           }
    tooBig = true;
    dfd.resolve();
});

    } else if (type == 'image') {
      dfd.promise();
      const img = new Image();
      img.onload = () => {
        if (this.width > MAX_MEDIA_SIZE || this.height > MAX_MEDIA_SIZE) {
          alert('Разрешение медиа не должно превышать '+MAX_MEDIA_SIZE+' пикселей');
          tooBig = true;
        }
        dfd.resolve();
      };
      img.src = URL.createObjectURL(file);
    } else {
      alert('Некорректный тип файла');
      return false;
    }
    await dfd.done();
    return !tooBig;
  },

  getAllowedFormats: function() {
    // TODO Добавить или уточнить форматы?
    if (this.model.get('content_type') === 'audio') {
      return 'audio/*';
    } else {
      return '.jpg,.jpeg,.bmp,.gif,.png,.mp4,.webm,.ogg';
    }
  },

  initDropzone: function(elem) {
    const availableSpace = Math.floor($('#space_left').data('spaceLeft') / 1024);
    const that = this;
    elem.dropzone({
      url: "/upload_chunks/",
      acceptedFiles: this.getAllowedFormats(),
      chunking: true,
      forceChunking: true,
      maxFilesize: availableSpace,
      parallelUploads: 1,
      parallelChunkUploads: false,

      addedfile: async file => {
        console.log('file added');
        let that_this = this;
        //let isValid = await that.isValidDimensions(file);
        // let isValid = true;
        // console.log(file.name, isValid);
        
      },

      accept: async function(file, done){
        console.log('ACCEPT', file);
        const url_cnt = that.collection.filter(el=>{
          return el.get('playlist')==that.model.id && el.get('url') !== ''; 
        }).length;
        if(url_cnt > 0)
        {
          done('Нельзя добавлять медиа в плейлист с URL');
          return;
        }
          
        
        let isValid = await that.isValidDimensions(file);
        if (isValid) {
          const modelFile = new app.Item({
            type: file.type.split("/", 1)[0],
            loading: true,
            name: file.name,
          });
          that.addOne(modelFile);

          that.blockForUpload();
          done();
        } else {
          done('Медиа-файл не подходит для проигрывания на устройстве');
          
        }
      },

      success: file => {
        // Делаем такую штуку ибо dropzone с чанками работает именно так
        response =  file.xhr.response;

        that.completeHandler(response, that);
        that.unblockForUpload();
      },

      error: (file, message) => {
        alert(message);
        console.log('error', message);
        that.unblockForUpload();
      },

      complete: file => {
        $(
          `.playlist-item__name:contains('${file.name}')`
        ).parent().removeClass('playlist-item--loading');
      },

      uploadprogress: (file, progress) => {
        // Фильтруем фальшивые 100%
        if (progress > 99.999) {
          return;
        }

        $(
          `.playlist-item__name:contains('${file.name}')`
        ).parent().find('progress.space').val(progress);

        const partProgress = progress / app.loadingContent;
        const shownProgress = parseInt($('.block').attr('value'));
        const newVal = shownProgress * (1 - 1 / app.loadingContent) + partProgress;
        // $('.block').attr('value', newVal);
        $('.load').html(`Осталось файлов: ${app.loadingContent}`);
      }
    });
  },

  blockForUpload: function() {
    if (app.loadingContent++ == 0) {
      $('.screen').block({
        message: '<div class="load"></div>' //<progress class="block" max="100" value="0"></progress>
      });
    }
  },

  unblockForUpload: function() {
    if (app.loadingContent == 0) {
      $('.screen').unblock();
      this.$el.trigger('mon-changed');
    }
  },

  setTime: function(event) {
    const time = $(event.currentTarget).val();
    this.model.set('time_begin', time);
  },

  setScale: function(event) {
    let scale = parseInt($(event.currentTarget).val());
    if (scale<1)
      scale=1;
    if (scale>=200)
      scale=199;
    this.model.set('scale_factor', scale);
    event.preventDefault();
  },

  setRefreshMode: function(event) {
    let refresh = parseInt($(event.currentTarget).val());
    if (refresh == NaN)
      refresh = null;
    this.model.set('url_refresh_mode', refresh);
    event.preventDefault();
  },

  setVol: function(event) {
    const time = $(event.currentTarget).val();
    this.model.set('volume', time);
  },

  setCurrentPl: function() {
    app.active_playlist = this.model;
  },

  addSUrl: function(url, name, dont_save_url, is_site, is_script) {
    const pl_len = this.collection.where({playlist: this.model.id}).length;
    if (pl_len > 0 && !is_script) {
      alert('Поток можно добавить только в пустой плейлист!');
      return;
    } else {
      this.$el.find('.new_url_name').val('');
      this.addURLItem(url, undefined, name, dont_save_url, is_site, is_script);
      $('#radio').modal('hide');
      $('#url').modal('hide');
      $('#video').modal('hide');
      $('#script').modal('hide');
    }
  },

  addSUrlEvent: function(event) {
    this.addSUrl(event[0], event[1], event[2], true, false);
  },

  addScriptEvent: function(event) {
    this.addSUrl(event[0], event[1], event[2], false, true);
  },

   isURL: function(str) {
     const a  = document.createElement('a');
     a.href = str;
     return (a.host && a.host != window.location.host);
  },

  addURLItem: function(url, only_save_url, name, dont_save_url, is_site, is_script) {
    const pl_len = this.collection.where({playlist: this.model.id}).length;
    let url_name = this.$el.find('.new_url_name').val();

    if (name) {
      url_name = name;
    }

    const new_item = new app.Item({
      sequence: pl_len + 1,
      playlist: this.model.id,
      name: url_name ? url_name : url,
      type: 'url',
      url: url,
      url_name: url_name,
      only_save_url: only_save_url,
      dont_save_url: dont_save_url,
      is_site: is_site,
      is_script: is_script
    });
    new_item.save();
    if (only_save_url && !dont_save_url) {
      this.$el.find('.new_url_name').val('');
      this.$el.find('.new_url_item').val('');
      messageSuccess('URL сохранен');
      return;
    }
    this.collection.add(new_item);
    this.$el.trigger('mon-changed');
    this.addAll();
  },

  updateSort: function(_event, model, position) {
    this.collection.remove(model);

    _.each(
      this.collection.where({
        playlist: this.model.id
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
    this.collection.add(model);
    var for_update = this.collection.where({playlist: this.model.id});
    this.updateSortDB(JSON.stringify(for_update));
    this.$el.trigger('mon-changed');
  },

  updateSortDB: function(in_data) {
    $.ajax({
      url: '/sort_items/',  //Server script to process data
      type: 'POST',
      //Ajax events
      //beforeSend: beforeSendHandler,
      success: res => console.log(res),
      error: e => handleError(
        e,
        'Ошибка! В случае повторения обратитесь в техподдержку.'
      ),
      // Form data
      data: in_data,
      //Options to tell jQuery not to process data or worry about content-type.
      cache: false,
      contentType: false,
      processData: false
    });
  },

  initialize: function() {
    // Костыль, чтобы инициализировать dropzone после рендера элементов
    _.bindAll(this, 'render', 'afterRender');
    const that = this;
    this.render = _.wrap(this.render, function(render) {
      render();
      that.afterRender();
      return that;
    });
    //this.listenTo(this.collection, 'add', this.addAll);
    this.listenTo(this.collection, 'reset', this.addAll);
    this.listenTo(this.collection, 'destroy', this.addAll);
    this.listenTo(this.model, 'clear_empty', this.delEmpty);
    this.listenTo(this.model, 'from_surl_to_url', this.addSUrlEvent);
    this.listenTo(this.model, 'from_script_to_url', this.addScriptEvent);
  },

  afterRender: function() {
    const elem = this.$('.upload');
    this.initDropzone(elem);
  },

  checkUrlAvailable: function(url, model) {
    $.ajax({
      type : "HEAD",
      url : url,
      timeout: 3000,
      jsonp : "jsonp",
      success : () => {
        console.log("ok");
      },
      error : (_xmlHttpRequest, textStatus) => {
        if (textStatus === 'timeout') {
          console.log("request timed out");
          model.trigger('url_timeout');
        }
      }
    });
  },

  addOne: function(file) {
    const view = new app.ItemView({model: file});
    const rendered = view.render();
    if (rendered)
      this.$('.playlist-items').append(rendered.el);
    if (file.get('url')) {
      this.checkUrlAvailable(file.get('url'), file);
      this.$('.url_refresh_mode_div').show();
    }
  },

  addAll: function() {
    this.$('.playlist-items').html('');
    _.each(this.collection.where({playlist: this.model.id}), this.addOne, this);
    this.$('.playlist-items').sortable({
      stop: (_event, ui) => {
        ui.item.trigger('drop', ui.item.index());
      }
    });
    const items_num = this.collection.where({playlist: this.model.id}).length;
    const is_adv = this.model.get('is_adv');
    this.$('.changing_interval, .shuffle_type').hide();
    if (items_num > 1) {
      if (this.model.get('content_type') == 'hybrid' || is_adv) {
        this.$('.changing_interval').show();
      } else {
        this.$('.shuffle_type').show();
      }
    }

    if (is_adv) {
      this.$('.changing_interval').show();
    }
   },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    this.addAll();
    return this;
  },

  intChange: function(event) {
    if (this.model.get('is_adv') == true) {
      this.model.set('interval', $(event.target).val() * 60000);
    } else {
      this.model.set('interval', $(event.target).val() * 1000);
    }
  },

  shuffleChange: function(event) {
    this.model.set('shuffle', $(event.target).prop('checked'));
  },

  isAdvChange: function(event) {
    let exit = false;
    const that = this;
    _.each(
      app.playlists.where({
        monitor: this.model.get('monitor')
      }),
      model => {
        if (model.get('is_adv') == true && that.model != model) {
          alert('На устройстве может быть только один рекламный плейлист!');
          exit = true;
        }
      }
    );

    if (!exit) {
      this.model.set('is_adv', $(event.target).prop('checked'));
      this.$el.trigger('adv-checked');
    } else {
      event.preventDefault();
    }
  },

  advAtOnceChange: function(event) {
    this.model.set('adv_at_once', $(event.target).prop('checked'));
  },

  completeHandler: function(result, that) {
    const objs = $.parseJSON(result);
    for (let i = 0; i < objs.length; i++) {
      that.addItem(objs[i]);
    }
    if(--app.loadingContent == 0)
      that.collection.sync(
        'create',
        this.collection,
        {
          success: res => {
            const to_del = that.collection.where({id: undefined});
            that.collection.remove(to_del);
            that.collection.set(res, {remove: false});
            that.addAll();
          }
        }
      );
  },

  errorHandler: function(a) {
    console.log(a);
    alert('Ошибка! В случае повторения обратитесь в техподдержку.');
  },

  addItem: function(obj) {
    const pl_len = this.collection.where({playlist: this.model.id}).length;
    const new_item = new app.Item({
      sequence: pl_len + 1,
      playlist: this.model.id,
      name: obj.name,
      type: obj.type,
      file_url: obj.url,
      local_path: obj.path,
      thumb_url: obj.thumb_url,
      file_id: obj.file_id
    });
    this.collection.add(new_item);
  },

  delete: function() {
    const count = this.collection.where({playlist: this.model.id}).length;
    if (count < 1) {
      this.$el.trigger('mon-changed');
      this.model.destroy();
    } else {
      if (confirm("Внимание, будут удалены все файлы плейлиста. Продолжить?")) {
        this.$el.trigger('mon-changed');
        this.model.destroy();
      }
    }
  },

  delEmpty: function() {
    const count = this.collection.where({playlist: this.model.id}).length;
    if (count < 1) {
      this.model.destroy();
    }
  },

  save: function() {
    this.model.save();
  },
});
