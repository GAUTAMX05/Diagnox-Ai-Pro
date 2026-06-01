document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. 🧬 Neural Network Background Animation
    // ==========================================
    const canvas = document.getElementById('neural-bg');
    const ctx = canvas.getContext('2d');
    let particlesArray;

    // Set Canvas Size
    function setCanvasSize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    setCanvasSize();

    // Theme Color (Medical Cyan)
    const particleColor = 'rgba(6, 182, 212, 0.8)'; // Teal
    const connectionColor = 'rgba(6, 182, 212,'; // RGB prefix

    class Particle {
        constructor(x, y, directionX, directionY, size) {
            this.x = x;
            this.y = y;
            this.directionX = directionX;
            this.directionY = directionY;
            this.size = size;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
            ctx.fillStyle = particleColor;
            ctx.fill();
        }
        update() {
            if (this.x > canvas.width || this.x < 0) this.directionX = -this.directionX;
            if (this.y > canvas.height || this.y < 0) this.directionY = -this.directionY;
            this.x += this.directionX;
            this.y += this.directionY;
            this.draw();
        }
    }

    function initParticles() {
        particlesArray = [];
        let numberOfParticles = (canvas.height * canvas.width) / 12000; // Density
        for (let i = 0; i < numberOfParticles; i++) {
            let size = (Math.random() * 2) + 1;
            let x = (Math.random() * ((innerWidth - size * 2) - (size * 2)) + size * 2);
            let y = (Math.random() * ((innerHeight - size * 2) - (size * 2)) + size * 2);
            let directionX = (Math.random() * 0.4) - 0.2;
            let directionY = (Math.random() * 0.4) - 0.2;
            particlesArray.push(new Particle(x, y, directionX, directionY, size));
        }
    }

    function connectParticles() {
        let opacityValue = 1;
        for (let a = 0; a < particlesArray.length; a++) {
            for (let b = a; b < particlesArray.length; b++) {
                let distance = ((particlesArray[a].x - particlesArray[b].x) ** 2) + 
                               ((particlesArray[a].y - particlesArray[b].y) ** 2);
                if (distance < (canvas.width / 7) * (canvas.height / 7)) {
                    opacityValue = 1 - (distance / 20000);
                    ctx.strokeStyle = `${connectionColor} ${opacityValue})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                    ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animateParticles() {
        requestAnimationFrame(animateParticles);
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
        }
        connectParticles();
    }

    window.addEventListener('resize', () => {
        setCanvasSize();
        initParticles();
    });
    
    initParticles();
    animateParticles();


    // ==========================================
    // 2. ⌨️ Typing Effect (Hero Section)
    // ==========================================
    new Typed('#typing-text', {
        strings: [
            'Predicting Diseases...',
            'Analyzing Symptoms...',
            'Suggesting Specialists...',
            'Empowering Your Health.'
        ],
        typeSpeed: 40,
        backSpeed: 30,
        loop: true,
        smartBackspace: true
    });


    // ==========================================
    // 3. 📜 Scroll Reveal Animation
    // ==========================================
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible-section');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.hidden-section').forEach(section => {
        observer.observe(section);
    });


    // ==========================================
    // 4. ⚙️ Functional Logic (Choices + Form)
    // ==========================================
    
    // Theme Toggle
    const themeBtn = document.getElementById('theme-toggle');
    const body = document.body;
    themeBtn.addEventListener('click', () => {
        const current = body.getAttribute('data-theme');
        body.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
        // Note: For full light mode, CSS variables in style.css need light variants
    });

    // Choices.js Init
    const symptomsSelect = document.getElementById('symptoms');
    if (symptomsSelect) {
        new Choices(symptomsSelect, {
            removeItemButton: true,
            placeholderValue: 'Search symptoms (e.g., headache)',
            searchPlaceholderValue: 'Type to filter...',
            itemSelectText: '',
        });
    }

    // Form Submission Logic
    const form = document.getElementById('symptom-form');
    const resultContainer = document.getElementById('result-container');
    const predictBtn = document.getElementById('predict-btn');
    const spinner = document.querySelector('.spinner');
    const btnText = document.querySelector('.btn-text');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI Loading State
        predictBtn.disabled = true;
        btnText.textContent = 'Processing...';
        spinner.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        
        const formData = new FormData(form);
        const severity = document.getElementById('severity').value;
        formData.append('severity', severity);

        try {
            // Artificial delay for "Scanning" feel (1.5s)
            await new Promise(r => setTimeout(r, 1500));

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            displayResults(data);

        } catch (error) {
            resultContainer.innerHTML = `<div class="result-box" style="border-left-color: #ef4444;"><p>Error processing request.</p></div>`;
            resultContainer.classList.remove('hidden');
        } finally {
            predictBtn.disabled = false;
            btnText.textContent = 'Analyze Health Data';
            spinner.classList.add('hidden');
        }
    });

    function displayResults(data) {
        if (data.error) {
            resultContainer.innerHTML = `<div class="result-box" style="border-left-color: #ef4444;">${data.error}</div>`;
        } else {
            const confidence = data.confidence || 85; // Fallback
            const disease = data.prediction || "Unknown";
            const suggestion = data.suggestion || "Consult a doctor.";
            const mapLink = `https://www.google.com/maps/search/?api=1&query=specialist+for+${disease}`;

            resultContainer.innerHTML = `
                <div class="result-box">
                    <h3 class="result-title">AI Diagnosis Prediction</h3>
                    <h2 class="predicted-disease">${disease}</h2>
                    
                    <div class="confidence-wrapper">
                        <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:#94a3b8;">
                            <span>AI Confidence</span>
                            <span>${confidence}%</span>
                        </div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: 0%"></div>
                        </div>
                    </div>

                    <div style="margin-top: 1.5rem; color: #cbd5e1;">
                        <strong><i class="ph-duotone ph-lightbulb"></i> Suggestion:</strong>
                        <p>${suggestion}</p>
                    </div>

                    <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                        <a href="${mapLink}" target="_blank" class="btn-primary" style="padding: 0.7rem 1.5rem; font-size: 0.9rem;">
                            <i class="ph-bold ph-map-pin"></i> Find Specialists Nearby
                        </a>
                    </div>
                </div>
            `;
            
            resultContainer.classList.remove('hidden');
            
            // Animate Bar after render
            setTimeout(() => {
                document.querySelector('.confidence-fill').style.width = `${confidence}%`;
            }, 100);
        }
    }
});