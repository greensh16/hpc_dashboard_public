// Keep this file intentionally small: the page works without JavaScript.
// Highlight the current section in the navigation as visitors scroll.
const links = [...document.querySelectorAll('.nav a[href^="#"]')]
const targets = links.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean)

if ('IntersectionObserver' in window && targets.length) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue
      for (const link of links) {
        const active = link.getAttribute('href') === `#${entry.target.id}`
        if (active) link.setAttribute('aria-current', 'location')
        else link.removeAttribute('aria-current')
      }
    }
  }, { rootMargin: '-25% 0px -65% 0px' })
  targets.forEach((target) => observer.observe(target))
}
