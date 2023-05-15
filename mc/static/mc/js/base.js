function checkArrows() {
  'use strict';

  try {
    eval('var foo = (x)=>x+1');
  } catch (e) {
    return false;
  }

  return true;
}

function replaceWithWarning(id) {
  // Пишем на ванильном js, чтобы работало всегда
  var anchor = document.getElementById(id);

  var warning = document.createElement('h1');
  warning.innerHTML = 'Ваш бразуер не поддерживается!';
  warning.className += 'pl-2 pt-4';

  anchor.parentNode.replaceChild(warning, anchor);
}

$(function() {
  if ($('#scroll').length) {
    const ps = new PerfectScrollbar('#scroll', {
      wheelSpeed: 2,
      wheelPropagation: true,
      minScrollbarLength: 20
    });

    $('#scroll').on('ps-scroll-down', () => {
      $('.screen-top-fixed').css('top', '+=105');
    });

    $('#scroll').on('ps-scroll-up', () => {
      $('.screen-top-fixed').css('top', '-=105');
    });

    $('#scroll').on('ps-y-reach-start', () => {
      $('.screen-top-fixed').css('top', '');
    });
  }

  const custom = document.querySelector('#settings-scroll');
  if (custom) {
    new PerfectScrollbar(custom, {
      suppressScrollX: true
    });
  }

  $('.scroll').each((_index, element) => {
    const container = $(element)[0];
    const ps = new PerfectScrollbar(container, {
      suppressScrollX: true
    });
  });
});

(function() {
  let selected_date;
  let ticker;
  let t;
  function getSrvTime() {
    $.ajax({
      type: 'POST',
      url: '/get_time/',
      success: data => {
        //clearInterval(ticker);
        selected_date = new Date(data.time);
        ticker = setInterval(function () {
          selected_date.setSeconds(selected_date.getSeconds() + 1);
          var time_wrapper = moment(selected_date).tz(data.tz);
          document.getElementById('cur_date').innerHTML = time_wrapper.format("DD.MM.YYYY HH:mm:ss (Z)");
      }, 1000);

      }
    });
  };
  getSrvTime();
})();

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie != '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

$.ajaxSetup({
  beforeSend: (xhr, settings) => {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});

function messageError(text) {
  $.jGrowl(text, {theme: 'error', position: 'bottom-right'});
}

function messageSuccess(text) {
  $.jGrowl(text, {theme: 'success', position: 'bottom-right'});
}

function handleError(e, msg, func) {
  console.log(e);

  if (typeof msg !== 'undefined') {
    messageError(msg);
  }

  if (typeof func !== 'undefined') {
    return func();
  }
}

const checkDelay = 5000;  // 5 секунд

function checkReboot(retries, funcAll, funcShowDone, funcError) {
  $.ajax({
    type: 'GET',
    url: '/reboot_all/',
    timeout: 0,

    success: data => {
      // Все хосты не стартовали или уже перезагрузились
      // или же у нас закончились попытки
      if (data.every(
        host => host.start == null || (host.start != null && host.check != null)
      ) || retries <= 0) {
        funcAll(data);

      } else {
        if (typeof funcShowDone !== 'undefined') {
          funcShowDone(data);
        }

        setTimeout(() => checkReboot(
          --retries,
          funcAll,
          funcShowDone,
          funcError
        ), checkDelay);
      }
    },

    error: () => {
      if (retries <= 0) {
        if (typeof funcError !== 'undefined') {
          funcError();
        }

      } else {
        setTimeout(() => checkReboot(
          --retries,
          funcAll,
          funcShowDone,
          funcError
        ), checkDelay);
      }
    }
  });
}

function convertToTimeString(timeString) {
  const time = parseInt(timeString);

  if (time <= 0) {
    return '0 сек';
  }

  const sec = time % 60;
  const min = Math.floor(time / 60);

  const secStr = sec > 0 ? `${sec} сек` : '';
  const minStr = min > 0 ? `${min} мин` : '';

  if (minStr.length > 0 && secStr.length > 0) {
    return minStr + ' ' + secStr;
  }

  if (secStr.length > 0) {
    return secStr;
  }

  if (minStr.length > 0) {
    return minStr;
  }

  return '0 сек';
}
