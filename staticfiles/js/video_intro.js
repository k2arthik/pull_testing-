/**
 * Video Intro Controller - Refined for Visuals and Audio
 */
(function () {
    const OVERLAY_ID = 'video-intro-overlay';
    const VIDEO_ID = 'intro-video';
    const INTERACTION_OVERLAY_ID = 'intro-interaction-overlay';
    const SKIP_BTN_ID = 'skip-intro';
    const SESSION_KEY = 'video_intro_played';

    function initVideoIntro() {
        const overlay = document.getElementById(OVERLAY_ID);
        const video = document.getElementById(VIDEO_ID);
        const interOverlay = document.getElementById(INTERACTION_OVERLAY_ID);
        const skipBtn = document.getElementById(SKIP_BTN_ID);

        if (!overlay || !video || !interOverlay || !skipBtn) {
            console.error("Video intro elements missing, forcing cleanup.");
            document.body.classList.remove('intro-active');
            return;
        }

        // Force check: if already played, remove immediately
        if (sessionStorage.getItem(SESSION_KEY)) {
            overlay.style.display = 'none';
            overlay.classList.add('hidden');
            document.body.classList.remove('intro-active');
            return;
        }

        // Show intro
        overlay.style.display = 'flex';
        document.body.classList.add('intro-active');

        let introEnded = false;
        let safetyTimeout = null;

        const endIntro = () => {
            if (introEnded) return;
            introEnded = true;
            if (safetyTimeout) clearTimeout(safetyTimeout);

            console.log("Ending video intro...");
            overlay.classList.add('hidden');
            document.body.classList.remove('intro-active');

            try {
                video.pause();
                video.src = ""; // Clear source to stop buffering
                video.load();
            } catch (e) {
                console.warn("Error pausing video during cleanup:", e);
            }

            sessionStorage.setItem(SESSION_KEY, 'true');
            window.dispatchEvent(new Event('video-intro-finished'));
            setTimeout(() => {
                overlay.style.display = 'none';
                overlay.remove(); // Remove from DOM entirely
            }, 800);
        };

        const handleInteraction = () => {
            console.log("User interacted with video intro.");
            video.muted = false;
            // Set a safety timeout: if video doesn't end in 10 seconds, just skip it
            safetyTimeout = setTimeout(endIntro, 10000);

            video.play().then(() => {
                interOverlay.style.opacity = '0';
                setTimeout(() => { interOverlay.style.display = 'none'; }, 300);
            }).catch(error => {
                console.warn("Playback failed even after interaction, skipping intro:", error);
                endIntro();
            });
        };

        // Listen for interaction on the overlay
        interOverlay.addEventListener('click', handleInteraction);
        interOverlay.addEventListener('touchstart', handleInteraction);

        // Also end on video completion or skip
        video.addEventListener('ended', endIntro);
        video.addEventListener('error', (e) => {
            console.error("Video error detected, skipping intro:", e);
            endIntro();
        });
        skipBtn.addEventListener('click', endIntro);

        // Try playing muted automatically first
        video.muted = true;
        video.play().catch(e => {
            console.warn("Muted autoplay blocked:", e);
            // If even muted autoplay is blocked, we still wait for interaction
        });

        // GLOBAL SAFETY: If for some reason nothing has happened after 12 seconds total, force end
        setTimeout(endIntro, 12000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVideoIntro);
    } else {
        initVideoIntro();
    }
})();
