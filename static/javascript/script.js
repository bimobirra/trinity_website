const form = document.getElementById("predict");

form.addEventListener("submit", function (e) {
  e.preventDefault();

  // Get form fields safely
  const brand = document.getElementById("Brand").value;
  const year = parseInt(document.getElementById("Year").value);
  const transmission = document.getElementById("Transmission").value;
  const model = document.getElementById("Model").value;
  const trim = document.getElementById("Trim").value;
  const body = document.getElementById("Body").value;
  const condition = document.getElementById("Condition").value;
  const odometer = parseInt(document.getElementById("Odometer").value);
  const interiorColor = document.getElementById("Interiorcolor").value;
  const color = document.getElementById("Color").value;

  let dict = {
    "year": year,
    "make": brand,
    "model": model,
    "trim": trim,
    "body": body,
    "transmission": transmission,
    "condition": condition,
    "odometer": odometer,
    "color": color,
    "interior": interiorColor
  };

  const predictBtn = form.querySelector('button[type="submit"], input[type="submit"]');
  if (predictBtn) {
    predictBtn.disabled = true;
    predictBtn.textContent = 'Predicting...';
  }

  const result = document.getElementById("result");
  result.innerHTML = '<span style="color:#0dcaf0">Predicting...</span>';

  axios.post("/predict/", dict, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(res => {
      result.innerHTML = `<span style="color:white">${res.data.result}</span>`;
    })
    .catch(error => {
      result.innerHTML = `<span style="color:red">Error: ${error.response?.data?.error || error.message}</span>`;
      
    })
    .finally(() => {
      if (predictBtn) {
        predictBtn.disabled = false;
        predictBtn.textContent = 'Predict';
      }
    });
});
