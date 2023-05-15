var app = app || {};

app.MonitorsCol = Backbone.Collection.extend({
  model: app.Monitor,
  comparator: 'sequence',
  url: '/monitor/'
});

app.monitors = new app.MonitorsCol();
