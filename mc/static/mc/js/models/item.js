var app = app || {};

app.Item = Backbone.Model.extend({
  defaults: {
    type: 'image',
    playlist: undefined,
    sequence: 1,
    name: '',
    file_url: '',
    local_path: '',
    thumb_url: '',
    file_id: undefined,
    url: '',
    only_save_url: undefined,
    dont_save_url: undefined,
    loading: false,
    is_site: false,
    is_script: false,
    bitrate: 0,
    bitrate_violation: false,
    wrong_orientation: false,
    duration: 30
  },
  urlRoot: '/item/'
});
