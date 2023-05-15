if (Dropzone) {
  Dropzone.autoDiscover = false;
}

$(function() {
  $(".sort").each((_index, element) => {
    initSortable($(element));
  });
});

function initSortable(elem) {
  if (elem.data('sortable-initialized')) {
    return false;
  }

  elem.data('sortable-initialized', true);

  elem.sortable({
    axis: "y"
  });
  elem.disableSelection();
}

function createReport(rebootData) {
  return rebootData.reduce((acc, cur) => {
    if (cur.start === null) {
      return acc
        + `<div class="offline mt-2 ml-2">${cur.host.name} не удалось отправить команду перезагрузки</div>`;

    } else if (cur.check === null) {
      return acc
        + `<div class="offline mt-2 ml-2">${cur.host.name} не отзывается после перезагрузки</div>`;

    } else {
      return acc + `<div class="online mt-2 ml-2">${cur.host.name} успешно перезагружено</div>`;
    }
  }, '');
}

$('.reboot_btn').click(() => {
  if (!confirm('Вы уверены, что хотите перезагрузить все устройства?')) {
    return;
  }

  const waitTime = 150;

  $.ajax({
    type: 'POST',
    url: '/reboot_all/',
    timeout: 0,
  });

  messageSuccess('Все устройства будут перезагружены, ожидайте');
  $.blockUI({
    blockMsgClass: 'blockMsgCustom',
    message: `<div id="reloaded"><div>Идет перезагрузка</div><progress class="block space" max="${waitTime}" value="0"></progress><div id="timer"></div></div><div id="reboots"></div>`
  });

  const progresser = setInterval(() => {
    $('.block').val((_, val) => ++val);
    $('#timer').html(
      'Осталось ' + convertToTimeString(waitTime - $('.block').val())
    );
  }, 1000);

  setTimeout(() => {
    checkReboot(
      25,
      data => {
        clearInterval(progresser);
        $('#reloaded').html('');

        let result = '';
        if (data.every(host => host.check != null && host.start != null)) {
          result = '<div class="ml-2 mt-2">Все устройства успешно перезагружены</div>';
        } else {
          result = createReport(data);
        }

        result += '<a href="#" class="btn btn-primary mb-2 mt-2" onclick="location.reload();">Ок</a>';

        $('#reboots').html(result);
      },

      data => $('#reboots').html(createReport(data)),

      () => {
        let error = '<div class="ml-2 mt-2">Не удалось связаться с мастером.</div>';
        error += '<div class="ml-2 mt-2">1. Попробуйте обновить страницу.</div>';
        error += '<div class="ml-2 mt-2">2. Если страница не открывается, то попробуйте отключить шнур питания устройства и включить его снова.</div>';
        error += '<div class="ml-2 mt-2 mb-2">3. Если страница и дальше не открывается, то обратитесь в техническую поддержку.</div>';

        clearInterval(progresser);
        $('#reloaded').html('');
        $('#reboots').html(error);
      }
    );
  }, 30000);
});

var app = app || {};

$('.apply').click(() => {
  app.MLV.apply();
});

app.checkEmptyPls = () => {
  for (let i = 0; i < app.playlists.length; i++) {
    const currentPl = app.playlists.models[i].id;
    if (app.pics.where({playlist: currentPl}).length == 0) {
      return true;
    }
  }
  return false;
}

app.clearEmptyPls = () => {
  for (let i = 0; i < app.playlists.length; i++) {
    const currentPl = app.playlists.models[i].id;
    if (app.pics.where({playlist: currentPl}).length == 0) {
      app.playlists.models[i].destroy();
      i--;
    }
  }
}

app.hideApply = () => {
  $('#main_apl_btn').addClass('hidden');
  $('.screen').block({
    message: null
  });
  $('.top-loader').show();
  $('#info_stage_1').show();
};

app.showApply = () => {
  $('#info_stage_1').hide();
  $('#info_stage_2').show();
  app.waitOneMinute();
};

app.endApply = () => {
  $('.screen').unblock();
  $('#info_stage_2').hide();
  $('.top-loader').hide();
};

const sleep = delay => new Promise(resolve => setTimeout(resolve, delay));

app.waitOneMinute = async () => {
  await sleep(60 * 1000);
  app.endApply();
};
