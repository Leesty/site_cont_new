(function () {
  var toggle = document.getElementById("support-toggle");
  var panel = document.getElementById("support-panel");
  if (!toggle || !panel) return;

  var loaded = false;
  var widgetRoot = document.getElementById("support-widget-root");
  if (!widgetRoot) return;

  function getCsrfToken() {
    var name = "csrftoken";
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var c = cookies[i].trim();
      if (c.indexOf(name + "=") === 0) return c.substring(name.length + 1);
    }
    return "";
  }

  function showPanel() {
    panel.classList.remove("d-none");
  }

  function hidePanel() {
    panel.classList.add("d-none");
  }

  function loadPanel() {
    if (loaded) {
      showPanel();
      return;
    }
    fetch("/support/widget/", {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (r) {
        if (!r.ok) throw new Error("Не удалось загрузить чат");
        return r.text();
      })
      .then(function (html) {
        panel.innerHTML = html;
        loaded = true;
        var form = document.getElementById("support-form");
        if (form) {
          form.addEventListener("submit", onSubmit);
        }
        var closeBtn = panel.querySelector(".support-panel-close");
        if (closeBtn) {
          closeBtn.addEventListener("click", hidePanel);
        }
        showPanel();
        scrollMessagesToBottom();
      })
      .catch(function () {
        alert("Не удалось загрузить чат поддержки.");
      });
  }

  function scrollMessagesToBottom() {
    var wrap = panel.querySelector(".support-panel-body");
    if (wrap) wrap.scrollTop = wrap.scrollHeight;
  }

  function onSubmit(e) {
    e.preventDefault();
    var form = e.target;
    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
    }
    var formData = new FormData(form);
    fetch("/support/widget/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCsrfToken(),
      },
    })
      .then(function (r) {
        if (!r.ok) throw new Error("Ошибка отправки");
        return r.text();
      })
      .then(function (html) {
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, "text/html");
        var newMessages = doc.getElementById("support-messages");
        var current = document.getElementById("support-messages");
        if (newMessages && current) {
          current.innerHTML = newMessages.innerHTML;
        }
        form.reset();
        scrollMessagesToBottom();
      })
      .catch(function () {
        alert("Не удалось отправить сообщение.");
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
      });
  }

  toggle.addEventListener("click", function (e) {
    e.preventDefault();
    if (panel.classList.contains("d-none")) {
      loadPanel();
    } else {
      hidePanel();
    }
  });
})();
