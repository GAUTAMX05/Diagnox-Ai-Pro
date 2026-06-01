document.addEventListener('DOMContentLoaded', () => {
    const symptomsSelect = document.getElementById('symptoms');
    if (symptomsSelect && typeof Choices !== 'undefined') {
        new Choices(symptomsSelect, {
            removeItemButton: true,
            placeholderValue: 'Search symptoms (e.g., headache)',
            searchPlaceholderValue: 'Type to filter...',
            itemSelectText: '',
        });
    }

    const form = document.getElementById('symptom-form');
    const resultContainer = document.getElementById('result-container');
    const predictBtn = document.getElementById('predict-btn');
    const spinner = document.querySelector('.spinner');
    const btnText = document.querySelector('.btn-text');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        predictBtn.disabled = true;
        if (btnText) btnText.style.visibility = 'hidden';
        spinner?.classList.remove('hidden');
        resultContainer?.classList.add('hidden');

        const formData = new FormData(form);
        const severity = document.getElementById('severity')?.value;
        if (severity) formData.append('severity', severity);

        try {
            await new Promise((r) => setTimeout(r, 1200));
            const response = await fetch('/predict', { method: 'POST', body: formData });
            const data = await response.json();
            displayResults(data);
        } catch {
            if (resultContainer) {
                resultContainer.innerHTML = '<p class="result-error">Error processing request.</p>';
                resultContainer.classList.remove('hidden');
            }
        } finally {
            predictBtn.disabled = false;
            if (btnText) btnText.style.visibility = 'visible';
            spinner?.classList.add('hidden');
        }
    });

    function displayResults(data) {
        if (!resultContainer) return;
        if (data.error) {
            resultContainer.innerHTML = `<p class="result-error">${data.error}</p>`;
        } else {
            const disease = data.prediction || 'Unknown';
            const suggestion = data.suggestion || 'Consult a doctor.';
            const home = data.home_remedy || suggestion;
            const doctor = data.doctor_advice || suggestion;
            const reportLink = data.report_url
                ? `<a href="${data.report_url}" class="btn-report-dl" target="_blank"><i class="ph ph-file-pdf"></i> Download PDF Report</a>`
                : '';
            const riskBadge = data.risk
                ? `<span class="pill pill-${data.risk_class || (data.risk || '').toLowerCase()}">${data.risk}</span>`
                : '';
            resultContainer.innerHTML = `
                <p class="result-title">AI Diagnosis Prediction ${riskBadge}</p>
                <h2 class="predicted-disease">${escapeHtml(disease)}</h2>
                <div class="advice-block home-advice">
                    <h4><i class="ph ph-house-line"></i> Home Remedies & Self-Care</h4>
                    <p>${escapeHtml(home)}</p>
                </div>
                <div class="advice-block doctor-advice">
                    <h4><i class="ph ph-stethoscope"></i> Doctor's Medical Advice</h4>
                    <p>${escapeHtml(doctor).replace(/\n/g, '<br>')}</p>
                </div>
                <div class="result-actions">${reportLink}
                <a href="/reports" class="btn-report-link">View Reports</a></div>
            `;
        }
        resultContainer.classList.remove('hidden');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
