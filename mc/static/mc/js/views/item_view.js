var app = app || {};

app.ItemView = Backbone.View.extend({

  template: _.template($('#file-template').html()),

  events: {
    'click .del': 'delete',
    'drop': 'drop',
    'click .up': 'moveUp',
    'click .down': 'moveDown'
  },

  drop: function(event, index) {
    this.$el.trigger('update-sort', [this.model, index]);
  },

  moveUp: function() {
    const prev = this.$el.prev();
    if (prev.length !== 0) {
      prev.before(this.$el);
    }
    this.$el.trigger('update-sort', [this.model, this.$el.index()]);
  },

  moveDown: function() {
    const next = this.$el.next();
    if (next.length !== 0) {
      next.after(this.$el);
    }
    this.$el.trigger('update-sort', [this.model, this.$el.index()]);
  },

  initialize: function() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'url_timeout', this.urlTimeout);
  },

  urlTimeout: function() {
    this.$el.addClass('url_timeout');
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    if (this.model.get('bitrate_violation'))
    {
      alert('Превышен битрейт файла '+this.model.get('name')+'! Файл будет удалён.')
      this.forceDelete();
      return;
    }
      
    return this;
  },

  delete: function(event) {
    if (!confirm("Вы уверены, что хотите удалить этот файл?")) {
      return;
    }
    this.$el.trigger('mon-changed');
    this.model.destroy();
    event.stopImmediatePropagation();
  },

  forceDelete: function() {
    this.$el.trigger('mon-changed');
    this.model.destroy();
  }
});
