(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Plain left clicks only, so cmd/ctrl/shift-click still opens links the usual way.
  var plainClick = function (e) { return !(e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button); };

  // Splash: fade out and continue to the site after 5 seconds (or on click).
  var splash = document.querySelector('.splash-link');
  if (splash) {
    var timer = null;
    var leaving = false;
    var go = function () {
      if (leaving) { return; }
      leaving = true;
      clearTimeout(timer);
      document.body.classList.add('leaving');
      // replace(), so Back from the site doesn't land on the splash and bounce forward again
      setTimeout(function () { location.replace(splash.getAttribute('href')); }, reduce ? 0 : 350);
    };
    splash.addEventListener('click', function (e) { if (plainClick(e)) { e.preventDefault(); go(); } });
    // pageshow also fires on first load, and again when the page comes back from the back/forward cache
    window.addEventListener('pageshow', function () {
      leaving = false;
      document.body.classList.remove('leaving');
      clearTimeout(timer);
      timer = setTimeout(go, 5000);
    });
    return;
  }

  // Mobile menu.
  var burger = document.querySelector('.burger');
  var menu = document.querySelector('.mobile-menu');
  if (burger && menu) {
    var setMenu = function (open) {
      document.body.classList.toggle('menu-open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      menu.setAttribute('aria-hidden', open ? 'false' : 'true');
    };
    burger.addEventListener('click', function () { setMenu(!document.body.classList.contains('menu-open')); });
    window.addEventListener('resize', function () { if (window.innerWidth >= 800) { setMenu(false); } });
  }

  // Fade elements in as they scroll into view. The `js` class (which hides them) is only added
  // once this is about to run, so an error earlier in the file can never leave content hidden.
  var reveal = [].slice.call(document.querySelectorAll('.reveal'));
  document.documentElement.classList.add('js');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.05 });
    reveal.forEach(function (el) { io.observe(el); });
  } else {
    reveal.forEach(function (el) { el.classList.add('in'); });
  }

  // Videos: load the file on first click, then use the browser's own controls.
  [].forEach.call(document.querySelectorAll('.player'), function (player) {
    var video = player.querySelector('video');
    var start = function () {
      if (!video.src) { video.src = video.getAttribute('data-src'); }
      video.controls = true;
      player.classList.add('playing');
      var started = video.play();
      if (started && started.catch) {
        started.catch(function () { video.controls = false; player.classList.remove('playing'); });
      }
    };
    player.querySelector('.play').addEventListener('click', start);
    video.addEventListener('click', function () { if (!video.controls) { start(); } });
  });

  // Lightbox for gallery images.
  // - Each slide gets its own <img>; the new one fades in while the old one fades out (a real crossfade).
  // - The already-cached grid thumbnail is shown at once and swapped for the full-size file when it is ready.
  // - Neighbouring images are preloaded, and a tile starts loading when the pointer rests on it.
  var links = [].slice.call(document.querySelectorAll('[data-lightbox]'));
  if (links.length) {
    var FADE = reduce ? 0 : 300;
    var box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<button class="close" type="button" aria-label="Close">&times;</button>' +
      '<button class="prev" type="button" aria-label="Previous">&#8249;</button>' +
      '<button class="nextimg" type="button" aria-label="Next">&#8250;</button>';
    document.body.appendChild(box);
    var nextBtn = box.querySelector('.nextimg');
    var current = null;
    var idx = 0;
    var token = 0;

    var wrap = function (i) { return (i + links.length) % links.length; };
    var fullOf = function (i) { return links[wrap(i)].getAttribute('href'); };
    var thumbOf = function (i) {
      var t = links[wrap(i)].querySelector('img');
      return t ? (t.currentSrc || t.src) : fullOf(i);
    };
    var preload = function (src) { (new Image()).src = src; };
    var remove = function (el) { if (el.parentNode) { el.parentNode.removeChild(el); } };
    var decoded = function (im) { return im.decode().catch(function () {}); };
    var pictures = function () { return [].slice.call(box.querySelectorAll('img')); };

    var show = function (i) {
      idx = wrap(i);
      var mine = ++token;
      var el = new Image();
      el.alt = '';
      el.className = 'hidden';
      el.src = thumbOf(idx);
      decoded(el).then(function () {
        if (mine !== token) { return; }
        var old = current;
        pictures().forEach(function (im) { if (im !== old) { remove(im); } }); // leftovers from very quick clicks
        // The picture's shape sets its displayed size (see the CSS), so the thumbnail and the
        // full-size file occupy exactly the same box, and the arrows can follow it.
        var ratio = el.naturalWidth / el.naturalHeight;
        el.style.setProperty('--ar', ratio);
        box.style.setProperty('--ar', ratio);
        box.insertBefore(el, nextBtn);
        current = el;
        void el.offsetWidth; // flush styles so the fade-in below is a transition, not a jump
        el.classList.remove('hidden');
        if (old) {
          old.classList.add('hidden');
          setTimeout(function () { remove(old); }, FADE + 60);
        }
        var full = new Image();
        full.src = fullOf(idx);
        decoded(full).then(function () {
          if (current === el) { el.src = full.src; }
          preload(fullOf(idx + 1));
          preload(fullOf(idx - 1));
          preload(thumbOf(idx + 2));
          preload(thumbOf(idx - 2));
        });
      });
    };
    var open = function (i) {
      box.classList.add('open');
      document.body.classList.add('lightbox-open');
      box.setAttribute('aria-hidden', 'false');
      show(i);
    };
    var close = function () {
      var mine = ++token;
      box.classList.remove('open');
      document.body.classList.remove('lightbox-open');
      box.setAttribute('aria-hidden', 'true');
      setTimeout(function () {
        if (mine === token) { pictures().forEach(remove); current = null; }
      }, FADE + 60);
    };
    links.forEach(function (a, i) {
      var hover;
      a.addEventListener('click', function (e) { if (plainClick(e)) { e.preventDefault(); open(i); } });
      a.addEventListener('mouseenter', function () { hover = setTimeout(function () { preload(a.getAttribute('href')); }, 150); });
      a.addEventListener('mouseleave', function () { clearTimeout(hover); });
    });
    box.querySelector('.close').addEventListener('click', close);
    box.querySelector('.prev').addEventListener('click', function () { show(idx - 1); });
    nextBtn.addEventListener('click', function () { show(idx + 1); });
    box.addEventListener('click', function (e) { if (e.target === box) { close(); } });
    document.addEventListener('keydown', function (e) {
      if (!box.classList.contains('open')) { return; }
      if (e.key === 'Escape') { close(); }
      if (e.key === 'ArrowLeft') { show(idx - 1); }
      if (e.key === 'ArrowRight') { show(idx + 1); }
    });
  }
})();
