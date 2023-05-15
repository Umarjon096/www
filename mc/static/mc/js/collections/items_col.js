var app = app || {};

app.ItemsCol = Backbone.Collection.extend({
  model: app.Item,
  comparator: 'sequence',
  url: '/item/'
});

app.pics = new app.ItemsCol();
