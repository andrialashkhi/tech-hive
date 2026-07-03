document.addEventListener('DOMContentLoaded', () => {
    const revealTargets = document.querySelectorAll('.reveal');
    if (revealTargets.length) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        revealTargets.forEach((el) => io.observe(el));
    }

    document.querySelectorAll('.flash-msg').forEach((msg) => {
        const closeBtn = msg.querySelector('button');
        const dismiss = () => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(20px)';
            setTimeout(() => msg.remove(), 250);
        };
        if (closeBtn) closeBtn.addEventListener('click', dismiss);
        setTimeout(dismiss, 5000);
    });

    const heroGlow = document.querySelector('.hero');
    if (heroGlow) {
        const glow = heroGlow.querySelector('.hero-glow');
        heroGlow.addEventListener('mousemove', (e) => {
            const rect = heroGlow.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            if (glow) {
                glow.style.transform = `translate(${x * 0.06 - 40}px, ${y * 0.06 - 40}px)`;
            }
        });
    }
});
