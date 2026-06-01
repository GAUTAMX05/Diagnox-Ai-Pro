document.addEventListener('DOMContentLoaded', () => {
    // --- Initialize Choices.js for the searchable dropdown ---
    const symptomsSelect = document.getElementById('symptoms');
    
    // Safety check to prevent errors
    if (!symptomsSelect) {
        console.error("Fatal Error: Could not find the 'symptoms' select element.");
        return;
    }

    const symptomsList = JSON.parse(symptomsSelect.dataset.symptoms || '[]');
    const symptomChoices = symptomsList.map(symptom => ({
        value: symptom,
        label: symptom.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
    }));
    
    const choices = new Choices(symptomsSelect, {
        removeItemButton: true,
        placeholder: true,
        placeholderValue: 'Type to search for symptoms...',
        searchPlaceholderValue: 'Type here...',
        allowHTML: true,
        choices: symptomChoices
    });

    // --- Get references to all DOM elements ---
    const form = document.getElementById('symptom-form');
    const predictBtn = document.getElementById('predict-btn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    const resultContainer = document.getElementById('result-container');
    
    // ## NEW: Get references for the location feature elements ##
    const locationFeature = document.getElementById('location-feature');
    const findDoctorBtn = document.getElementById('find-doctor-btn');
    const mapLinkContainer = document.getElementById('map-link-container');
    
    // --- Listen for the form's submit event ---
    form.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default page reload
        btnText.textContent = 'Analyzing...';
        spinner.classList.remove('hidden');
        predictBtn.disabled = true;
        resultContainer.classList.add('hidden');
        locationFeature.classList.add('hidden'); // Hide previous location results

        fetch('/predict', { method: 'POST', body: new FormData(form) })
            .then(response => response.json())
            .then(data => { displayResults(data); })
            .catch(error => {
                console.error('Error:', error);
                displayResults({ error: 'An unexpected error occurred. Please try again.' });
            })
            .finally(() => {
                btnText.textContent = 'Analyze Symptoms';
                spinner.classList.add('hidden');
                predictBtn.disabled = false;
            });
    });

    // --- Function to dynamically create and show the result card ---
    function displayResults(data) {
        let content = '';
        if (data.error) {
            content = `<div class="glass-card result-card error"><h2>Error</h2><p>${data.error}</p></div>`;
        } else {
            content = `
                <div class="glass-card result-card">
                    <div class="result-header">
                        <i class="ph ph-first-aid-kit"></i>
                        <span>AI Analysis Complete</span>
                    </div>
                    <div class="result-body">
                        <h3 class="result-title">Potential Condition</h3>
                        <h2>${data.prediction}</h2>
                        <p class="suggestion-title">Recommended Action</p>
                        <p>${data.suggestion}</p>
                    </div>
                </div>`;
            
            // ## NEW: If prediction is successful, show the "Find a Doctor" feature ##
            locationFeature.classList.remove('hidden');
            // Store the prediction in the button's dataset to use it later
            findDoctorBtn.dataset.prediction = data.prediction;
            // Clear any previous map links
            mapLinkContainer.innerHTML = '';
        }
        resultContainer.innerHTML = content;
        resultContainer.classList.remove('hidden');
    }

    // --- ## NEW: Geolocation Feature Logic ## ---
    findDoctorBtn.addEventListener('click', () => {
        mapLinkContainer.innerHTML = `<p class="location-status">Getting your location...</p>`;

        if (!navigator.geolocation) {
            mapLinkContainer.innerHTML = `<p class="location-error">Geolocation is not supported by your browser.</p>`;
            return;
        }

        // Request the user's current position
        navigator.geolocation.getCurrentPosition(geolocationSuccess, geolocationError);
    });

    function geolocationSuccess(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        const prediction = findDoctorBtn.dataset.prediction || "Doctor";

        // Use a helper function to find the right specialist
        const searchQuery = `${getSpecialist(prediction)} near me`;
        
        // Create the Google Maps URL
        const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(searchQuery)}&ll=${latitude},${longitude}`;

        // Display the link
        mapLinkContainer.innerHTML = `
            <a href="${googleMapsUrl}" target="_blank" class="map-link">
                Click here to see nearby medical facilities on Google Maps
                <i class="ph ph-arrow-square-out"></i>
            </a>`;
    }

    function geolocationError() {
        mapLinkContainer.innerHTML = `<p class="location-error">Unable to retrieve your location. Please enable location services in your browser.</p>`;
    }

    // Helper function to suggest a specialist based on the predicted disease
    function getSpecialist(disease) {
        const diseaseLower = disease.toLowerCase();
        if (diseaseLower.includes('heart') || diseaseLower.includes('hypertension')) {
            return 'Cardiologist';
        }
        if (diseaseLower.includes('fungal') || diseaseLower.includes('acne') || diseaseLower.includes('psoriasis')) {
            return 'Dermatologist';
        }
        if (diseaseLower.includes('gastro') || diseaseLower.includes('gerd') || diseaseLower.includes('ulcer')) {
            return 'Gastroenterologist';
        }
        if (diseaseLower.includes('arthritis') || diseaseLower.includes('spondylosis')) {
            return 'Orthopedist';
        }
        return 'Hospital'; // Default fallback if no specific specialist is found
    }
});