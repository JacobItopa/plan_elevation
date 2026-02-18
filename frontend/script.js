const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const imagePreview = document.getElementById('image-preview');
const previewContainer = document.getElementById('preview-container');
const uploadContent = document.querySelector('.upload-content');
const generateBtn = document.getElementById('generate-btn');
const btnText = document.querySelector('.btn-text');
const btnLoader = document.querySelector('.btn-loader');
const resultSection = document.getElementById('result-section');
const resultImage = document.getElementById('result-image');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const downloadBtn = document.getElementById('download-btn');

let selectedFile = null;

// Drag & Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

uploadArea.addEventListener('click', (e) => {
    if (e.target.closest('.remove-btn')) return;
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        handleFile(fileInput.files[0]);
    }
});

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file.');
        return;
    }

    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        previewContainer.style.display = 'block';
        uploadContent.style.display = 'none';
        generateBtn.disabled = false;
        resultSection.style.display = 'none'; // hide previous result
    };
    reader.readAsDataURL(file);
}

function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    previewContainer.style.display = 'none';
    uploadContent.style.display = 'block';
    generateBtn.disabled = true;
    resultSection.style.display = 'none';
}

generateBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // UI Loading State
    generateBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';

    resultSection.style.display = 'block';
    loadingOverlay.style.display = 'flex';
    loadingText.textContent = "Uploading floor plan...";
    resultImage.src = ""; // Clear previous

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Generation failed');
        }

        loadingText.textContent = "AI is generating elevation (this may take 30s+)...";

        const data = await response.json();

        if (data.status === 'success' && data.result_image_url) {
            resultImage.src = data.result_image_url;
            downloadBtn.href = data.result_image_url;

            // Wait for image to load before removing overlay
            resultImage.onload = () => {
                loadingOverlay.style.display = 'none';
            };
            resultImage.onerror = () => {
                loadingText.textContent = "Error loading result image.";
            }

        } else {
            throw new Error('No result image URL returned.');
        }

    } catch (error) {
        console.error(error);
        alert('Error: ' + error.message);
        loadingOverlay.style.display = 'none';
        resultSection.style.display = 'none';
    } finally {
        generateBtn.disabled = false;
        btnText.style.display = 'inline-block';
        btnLoader.style.display = 'none';
    }
});
