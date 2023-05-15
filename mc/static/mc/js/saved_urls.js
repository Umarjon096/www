var app = app || {};

app.savedURL = Backbone.Model.extend({
  defaults: {
    name: '',
    url: '',
    video: false,
    audio: false
  },
  urlRoot: '/saved_url/'
});

app.savedURLCol = Backbone.Collection.extend({
  model: app.savedURL,
  comparator: 'id',
  url: '/saved_url/'
});

app.saved_urls = new app.savedURLCol();

app.SURLView = Backbone.View.extend({
  className: 'radio-elem',
  template: _.template($('#radio-template').html()),

  events: {
    'click': 'addToPL',
    'click .del': 'confirmDelete'
  },

  addToPL: function(event) {
    app.active_playlist.trigger(
      'from_surl_to_url',
      [this.model.get('url'), this.model.get('name'), true]
    );
    event.stopImmediatePropagation();
  },

  confirmDelete: function(event) {
    event.stopImmediatePropagation();
    if (confirm("Внимание, будет удален URL. Продолжить?")) {
      this.model.destroy();
    }
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  }
});

app.SURLListView = Backbone.View.extend({
  el: '#surl_list',

  initialize: function () {
    this.listenTo(this.collection, 'reset', this.addAll);
    this.listenTo(this.collection, 'destroy', this.addAll);
    this.listenTo(this.collection, 'add', this.addOne);
    this.collection.fetch({reset: true});
  },

   events: {
    'focus .new_url_item': 'toggleUrlName',
    'click .url_item_radio': 'addSRadio',
    'click .url_item_video': 'addSVideo',
    'click .url_item_site': 'addSite',
    'click .script_item_site': 'addScript'
  },

  toggleUrlName: function(event) {
    this.$el.find('.new_url_adds').show();
  },

  isURL: function(str) {
    const a  = document.createElement('a');
    a.href = str;
    return (a.host && a.host != window.location.host);
  },

  addSRadio: function() {
    const new_url = this.$el.find('.new_radio_url').val();
    const new_name = this.$el.find('.new_radio_name').val();

    const new_model = {
      url: new_url,
      name: new_name,
      video: false,
      audio: true
    };

    this.addSUrl(new_model);

  },

  addSVideo: function() {
    const new_url = this.$el.find('.new_video_url').val();
    const new_name = this.$el.find('.new_video_name').val();

    const new_model = {
      url: new_url,
      name: new_name,
      video: true,
      audio: false
    };

    this.addSUrl(new_model);
  },

  addSite: function() {
    const new_url = this.$el.find('.new_site_url').val();
    const new_name = this.$el.find('.new_site_name').val();

    if (!this.isURL(new_url)) {
      alert('Некорректный URL');
      return;
    }

    app.active_playlist.trigger(
      'from_surl_to_url',
      [new_url, new_name, true]
    );
  },

  addScript: function() {
    const new_script = this.$el.find('.new_script_code').val();

    app.active_playlist.trigger(
      'from_script_to_url',
      [new_script, 'script', true]
    );
  },

  addSUrl: function(model) {
    if (!this.isURL(model.url)) {
      alert('Некорректный URL');
      return;
    }

    const surl = new app.savedURL(model);

    surl.save(
      null,
      {
        success: this.successHandler,
        error: this.errorHandler,
        context: this
      }
    );
  },

  successHandler: function(model, _response, options) {
    options.context.$el.find('.new_video_url').val('');
    options.context.$el.find('.new_video_name').val('');
    options.context.$el.find('.new_radio_url').val('');
    options.context.$el.find('.new_radio_name').val('');
    options.context.$el.find('.new_site_url').val('');
    options.context.$el.find('.new_site_name').val('');
    options.context.$el.find('.new_script_code').val('');

    options.context.collection.add(model);

    $('.radio-list').scrollTop(9999999);
    if (model.attributes.video) {
      messageSuccess('Видеопоток сохранен');
    } 
    else if (model.attributes.audio)
    {
      messageSuccess('Радио сохранено');
    }
    else (model.attributes.audio)
    {
      messageSuccess('URL сохранен');
    }
  },

  addOne: function(surl) {
    const id = surl.attributes.video
      ? '#video_list .saved_urls'
      : '#radio_list .saved_urls';

    var view = new app.SURLView({model:surl});
    this.$(id).append(view.render().el);
  },

  addAll: function() {
    this.$('.saved_urls').html('');
    this.collection.each(this.addOne, this);

    if (this.collection.filter(surl => surl.attributes.video).length == 0) {
      this.$('#video_list .saved_urls').html('<div class="ml-3">Список пуст</div>');
    }

    if (this.collection.filter(surl => !surl.attributes.video).length == 0) {
      this.$('#radio_list .saved_urls').html('<div class="ml-3">Список пуст</div>');
    }
  },

  errorHandler: function(_model, res) {
    messageError(res.responseText);
  }
});

$(document).ready(function() {
  new app.SURLListView({collection: app.saved_urls});
});
