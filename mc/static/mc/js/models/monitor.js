var app = app || {};

app.Monitor = Backbone.Model.extend({
  defaults: {
    sequence: 1,
    name: undefined,
    orientation: 'horizontal',
    customer: undefined,
    changed: false,
    host: 0,
    health: true,
    health_reason: '',
    music_box: false,
    licence: true,
    volume_locked: false,
    bt: false,
    apply_is_firing: false
  }
});
