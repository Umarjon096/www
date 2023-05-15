var app = app || {};

app.PlaylistsCol = Backbone.Collection.extend({
  model: app.Playlist,
  comparator: 'time_begin',
  url: '/playlist/'
});

app.playlists = new app.PlaylistsCol();
