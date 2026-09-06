/* Optional teaching motion. The HTML/SVG resting state is the complete lesson. */
(() => {
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!Element.prototype.animate) return;

  function controller(button, makeAnimations) {
    const label = button.textContent;
    let animations = [];
    let state = 'idle';
    let generation = 0;
    function reset() {
      generation += 1;
      animations.forEach(animation => animation.cancel());
      animations = [];
      state = 'idle';
      button.textContent = label;
      button.dataset.state = state;
      button.hidden = preference.matches;
    }
    button.addEventListener('click', () => {
      if (preference.matches) return;
      if (state === 'playing') {
        animations.forEach(animation => animation.pause());
        state = 'paused';
        button.textContent = 'Resume';
      } else if (state === 'paused') {
        animations.forEach(animation => animation.play());
        state = 'playing';
        button.textContent = 'Pause';
      } else {
        const current = ++generation;
        animations = makeAnimations();
        state = 'playing';
        button.textContent = 'Pause';
        Promise.all(animations.map(animation => animation.finished)).then(() => {
          if (generation === current) reset();
        }).catch(() => { /* Cancellation restores the complete static scene. */ });
      }
      button.dataset.state = state;
    });
    preference.addEventListener('change', reset);
    // Pause an active replay when the page is backgrounded.
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && state === 'playing') {
        animations.forEach(animation => animation.pause());
        state = 'paused';
        button.textContent = 'Resume';
        button.dataset.state = state;
      }
    });
    reset();
  }

  const propagation = document.querySelector('[data-motion="propagation"]');
  if (propagation) controller(propagation, () => {
    const scene = document.querySelector('#propagation-scene');
    const duration = 3600;
    return [
      scene.querySelector('.propagation-pulse').animate([
        { offset: 0, transform: 'translate(102px, 85px)', opacity: 0 },
        { offset: .08, transform: 'translate(102px, 85px)', opacity: 1 },
        { offset: .37, transform: 'translate(207px, 85px)', opacity: 1 },
        { offset: .4, transform: 'translate(207px, 85px)', opacity: 0 },
        { offset: .53, transform: 'translate(273px, 85px)', opacity: 0 },
        { offset: .56, transform: 'translate(273px, 85px)', opacity: 1 },
        { offset: .85, transform: 'translate(377px, 85px)', opacity: 1 },
        { offset: .88, transform: 'translate(377px, 85px)', opacity: 0 },
        { offset: 1, transform: 'translate(377px, 85px)', opacity: 0 }
      ], { duration, easing: 'linear' }),
      scene.querySelector('[data-at="mediator"]').animate([
        { offset: 0, opacity: 0 }, { offset: .34, opacity: 0 },
        { offset: .43, opacity: .85 }, { offset: .58, opacity: 0 },
        { offset: 1, opacity: 0 }
      ], { duration }),
      scene.querySelector('[data-at="outcome"]').animate([
        { offset: 0, opacity: 0 }, { offset: .8, opacity: 0 },
        { offset: .9, opacity: .85 }, { offset: 1, opacity: 0 }
      ], { duration })
    ];
  });

  const depth = document.querySelector('[data-motion="depth"]');
  if (depth) controller(depth, () => {
    const animations = [];
    const bars = document.querySelectorAll('.effect-bars li');
    // Reveal each link and its recorded effect together; no new quantities.
    for (let d = 1; d <= 5; d++) {
      const start = .04 + (d - 1) * .16;
      const frames = [
        { offset: 0, opacity: 0 }, { offset: start, opacity: 0 },
        { offset: start + .1, opacity: 1 }, { offset: 1, opacity: 1 }
      ];
      const link = document.querySelector(`.depth-link[data-depth="${d}"]`);
      animations.push(link.animate(frames, { duration: 4200, easing: 'ease-in-out' }));
      animations.push(bars[d - 1].animate(frames, { duration: 4200, easing: 'ease-in-out' }));
    }
    return animations;
  });
})();
