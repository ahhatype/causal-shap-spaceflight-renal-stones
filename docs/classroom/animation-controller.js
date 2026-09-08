/* Optional teaching motion. The HTML/SVG resting state is the complete lesson. */
(() => {
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!Element.prototype.animate) return;

  // Reuse the original four-node sequence, with deliberate rather than autoplay motion.
  const chain = document.querySelector('#chain-animation');
  if (chain) {
    const setup = () => {
      const svg = chain;
      if (!svg || svg.nodeName.toLowerCase() !== 'svg') return;
      const controls = document.querySelector('.chain-controls');
      if (controls.dataset.ready) return;
      controls.dataset.ready = 'true';
      const play = document.querySelector('#chain-play');
      const status = document.querySelector('#chain-status');
      let playing = false;
      const animations = () => svg.getAnimations({ subtree: true });
      function stop(label) {
        svg.classList.remove('is-playing');
        animations().forEach(animation => animation.pause());
        playing = false;
        play.textContent = 'Play comparison';
        play.setAttribute('aria-pressed', 'false');
        if (label) status.textContent = label;
      }
      function seek(view) {
        stop();
        // The SVG has a -3s delay: these times show 3s and 9s in its 12s cycle.
        animations().forEach(animation => { animation.currentTime = view === 'prediction' ? 0 : 6000; });
        status.textContent = view === 'prediction' ? 'Prediction view' : 'Structural credit view';
      }
      play.addEventListener('click', () => {
        if (preference.matches) return;
        if (playing) stop('Comparison paused');
        else {
          svg.classList.add('is-playing');
          animations().forEach(animation => animation.play());
          playing = true;
          play.textContent = 'Pause comparison';
          play.setAttribute('aria-pressed', 'true');
          status.textContent = 'Playing comparison';
        }
      });
      controls.querySelectorAll('[data-chain-view]').forEach(button => {
        button.addEventListener('click', () => seek(button.dataset.chainView));
      });
      function motionPreference() {
        play.hidden = preference.matches;
        seek('prediction');
      }
      preference.addEventListener('change', motionPreference);
      document.addEventListener('visibilitychange', () => {
        if (document.hidden && playing) stop('Comparison paused');
      });
      controls.hidden = false;
      motionPreference();
    };
    chain.addEventListener('load', setup);
    setup();
  }

})();
