(function () {
  const lyricsEl = document.getElementById('lyrics');
  if (!lyricsEl) return; // not the song page

  const params = new URLSearchParams(location.search);
  const slug = params.get('slug');
  if (!slug) {
    lyricsEl.textContent = 'Falta el parámetro ?slug= en la URL.';
    return;
  }

  const audio = document.getElementById('audio');
  const titleEl = document.getElementById('song-title');
  const artistEl = document.getElementById('song-artist');

  fetch(`data/${encodeURIComponent(slug)}.json`)
    .then(r => {
      if (!r.ok) throw new Error('no existe la ficha de esta canción');
      return r.json();
    })
    .then(song => {
      titleEl.textContent = song.title;
      artistEl.textContent = song.artist || 'artista sin confirmar';
      audio.src = song.audio;
      document.title = `${song.title} — Karaoke`;
      renderLyrics(song);
    })
    .catch(err => {
      lyricsEl.textContent = `No se pudo cargar la canción (${err.message}).`;
    });

  function renderLyrics(song) {
    if (song.sync === 'none' || !song.lines || song.lines.length === 0) {
      lyricsEl.innerHTML = '<p class="no-sync">Todavía no hay letra sincronizada para este tema. Reproducí igual la pista de abajo.</p>';
      return;
    }

    const lineEls = song.lines.map(line => {
      const p = document.createElement('p');
      p.className = 'line';
      p.dataset.time = line.time;

      if (line.words && line.words.length) {
        line.words.forEach(w => {
          const span = document.createElement('span');
          span.className = 'word';
          span.dataset.time = w.time;
          span.textContent = w.text + ' ';
          p.appendChild(span);
        });
      } else {
        p.textContent = line.text;
      }
      return p;
    });

    lineEls.forEach(el => lyricsEl.appendChild(el));

    const hasWords = song.sync === 'word';
    let activeLine = null;
    let activeWord = null;

    audio.addEventListener('timeupdate', () => {
      const t = audio.currentTime;

      let currentLine = null;
      for (const el of lineEls) {
        if (parseFloat(el.dataset.time) <= t) currentLine = el;
        else break;
      }
      if (currentLine !== activeLine) {
        if (activeLine) activeLine.classList.remove('active');
        if (currentLine) {
          currentLine.classList.add('active');
          currentLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        activeLine = currentLine;
      }

      if (hasWords && currentLine) {
        const words = currentLine.querySelectorAll('.word');
        let currentWord = null;
        words.forEach(w => {
          if (parseFloat(w.dataset.time) <= t) currentWord = w;
        });
        if (currentWord !== activeWord) {
          if (activeWord) activeWord.classList.remove('active-word');
          if (currentWord) currentWord.classList.add('active-word');
          activeWord = currentWord;
        }
      }
    });

    lyricsEl.addEventListener('click', (e) => {
      const el = e.target.closest('[data-time]');
      if (el) audio.currentTime = parseFloat(el.dataset.time);
    });
  }
})();
