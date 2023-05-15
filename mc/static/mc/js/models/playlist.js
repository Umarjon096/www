var app = app || {};

app.Playlist = Backbone.Model.extend({
  defaults: {
    content_type: 'hybrid',
    monitor: undefined,
    sequence: 1,
    interval: 60000,
    time_begin: '00:00',
    shuffle: false,
    is_adv: false,
    fade_time: 400,
    buffer_time: 0.5,
    adv_at_once: false,
    volume: '',
    scale_factor: 100,
    url_refresh_mode: null
  },
  urlRoot: '/playlist/'
});
