const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
ctx.lineWidth = 20;
ctx.lineCap = 'round';
ctx.strokeStyle = 'black';  // ✅ Explicitly set to black

let drawing = false;
canvas.addEventListener('mousedown', () => drawing = true);
canvas.addEventListener('mouseup', () => {
  drawing = false;
  ctx.beginPath();
});
canvas.addEventListener('mouseout', () => {
  drawing = false;
  ctx.beginPath();
});
canvas.addEventListener('mousemove', draw);

function draw(e) {
  if (!drawing) return;
  const rect = canvas.getBoundingClientRect();
  ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function clearCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'white';  // ✅ Refill background
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.beginPath();
  document.getElementById('result').innerText = '';
}

function predict() {
  const spinner = document.getElementById('spinner');
  const result = document.getElementById('result');

  // Show spinner & clear previous result
  spinner.style.display = 'block';
  result.innerText = '';

  canvas.toBlob(function(blob) {
    const formData = new FormData();
    formData.append('image', blob, 'digit.png');

    fetch('/predict', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      // Hide spinner
      spinner.style.display = 'none';

      if (data.error) {
        result.innerText = 'Error: ' + data.error;
      } else {
        result.innerText = "Predicted Digit: " + data.digit;
      }
    })
    .catch(err => {
      spinner.style.display = 'none';
      result.innerText = 'Error: ' + err.message;
    });
  });
}

ctx.fillStyle = 'white';
ctx.fillRect(0, 0, canvas.width, canvas.height);